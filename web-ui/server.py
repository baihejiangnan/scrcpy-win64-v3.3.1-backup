#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrcpy 投屏控制中心 · Web UI 后端
零第三方依赖（仅标准库），提供 REST API 控制 adb / scrcpy，
并托管 static/ 下的前端页面。

用法:
    python server.py [--port 7100] [--host 127.0.0.1]
兼容 `npm run dev -- --port XXXX --host YYYY` 参数转发。
"""

import argparse
import ipaddress
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
from collections import deque
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

# 路径支持环境变量覆盖（打包成 exe 时由 launcher 注入）
BASE_DIR = Path(os.environ.get("SCRCPY_WEBUI_DIR") or Path(__file__).resolve().parent)  # web-ui/
RUNTIME_DIR = Path(os.environ.get("SCRCPY_RUNTIME_DIR") or BASE_DIR.parent)             # scrcpy-win64-v3.3.1/
STATIC_DIR = Path(os.environ.get("SCRCPY_STATIC_DIR") or BASE_DIR / "static")
DOWNLOAD_DIR = Path(os.environ.get("SCRCPY_DOWNLOAD_DIR") or BASE_DIR / "downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
WALLPAPER_DIR = Path(os.environ.get("SCRCPY_WALLPAPER_DIR") or BASE_DIR / "wallpapers")
WALLPAPER_DIR.mkdir(parents=True, exist_ok=True)
WALLPAPER_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}

ADB = str(RUNTIME_DIR / "adb.exe")
SCRCPY = str(RUNTIME_DIR / "scrcpy.exe")

CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0

MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon",
    ".json": "application/json; charset=utf-8",
}


def run_cmd(cmd, timeout=30):
    """同步执行命令，返回 (ok, output)。"""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           timeout=timeout, creationflags=CREATE_NO_WINDOW)
        out = (r.stdout or "") + (r.stderr or "")
        return r.returncode == 0, out.strip()
    except subprocess.TimeoutExpired:
        return False, "命令执行超时"
    except Exception as e:
        return False, str(e)


class State:
    """全局运行状态（线程安全）。"""

    def __init__(self):
        self.lock = threading.Lock()
        self.selected_device = ""
        self.mirror_proc = None
        self.mirror_since = 0.0
        self.record_proc = None
        self.record_file = ""
        self.record_since = 0.0
        self.logs = deque(maxlen=600)
        self.log_seq = 0

    # ---- 日志 ----
    def log(self, msg):
        with self.lock:
            self.log_seq += 1
            entry = {
                "seq": self.log_seq,
                "time": datetime.now().strftime("%H:%M:%S"),
                "msg": msg,
            }
            self.logs.append(entry)

    def logs_since(self, since):
        with self.lock:
            return [e for e in self.logs if e["seq"] > since]

    def clear_logs(self):
        with self.lock:
            self.logs.clear()

    # ---- 进程 ----
    def _watch(self, proc, kind):
        """后台线程：转发子进程输出到日志，并在退出时记录。"""
        def pump(stream):
            try:
                for line in iter(stream.readline, ""):
                    line = line.strip()
                    if line:
                        self.log(f"[{kind}] {line}")
            except Exception:
                pass

        if proc.stdout:
            threading.Thread(target=pump, args=(proc.stdout,), daemon=True).start()
        if proc.stderr:
            threading.Thread(target=pump, args=(proc.stderr,), daemon=True).start()

        def waiter():
            code = proc.wait()
            with self.lock:
                if kind == "mirror" and self.mirror_proc is proc:
                    self.mirror_proc = None
                    self.mirror_since = 0.0
                if kind == "record" and self.record_proc is proc:
                    f = self.record_file
                    self.record_proc = None
                    self.record_file = ""
                    self.record_since = 0.0
                    if f and os.path.exists(f) and os.path.getsize(f) > 0:
                        size = os.path.getsize(f) / (1024 * 1024)
                        self.log(f"✅ 录制完成: {os.path.basename(f)} ({size:.1f} MB)")
                    else:
                        self.log("⚠️ 录制结束，但文件为空或不存在")
            self.log(f"⏹️ {'投屏' if kind == 'mirror' else '录制'}进程已退出 (code={code})")

        threading.Thread(target=waiter, daemon=True).start()

    def snapshot(self):
        with self.lock:
            now = time.time()
            return {
                "selected": self.selected_device,
                "mirroring": self.mirror_proc is not None,
                "mirrorElapsed": int(now - self.mirror_since) if self.mirror_proc else 0,
                "recording": self.record_proc is not None,
                "recordElapsed": int(now - self.record_since) if self.record_proc else 0,
                "recordFile": os.path.basename(self.record_file) if self.record_file else "",
            }


STATE = State()


# ---------------- adb / scrcpy 操作 ----------------

_model_cache = {}
_MODEL_TTL = 300  # 型号缓存 5 分钟


def _device_model(dev_id):
    """获取设备型号（带缓存，失败返回 None）。"""
    cached = _model_cache.get(dev_id)
    if cached and time.time() - cached[1] < _MODEL_TTL:
        return cached[0]
    ok, out = run_cmd([ADB, "-s", dev_id, "shell", "getprop",
                       "ro.product.model"], timeout=5)
    model = out.splitlines()[0].strip() if ok and out.strip() else None
    _model_cache[dev_id] = (model, time.time())
    return model


def list_devices():
    ok, out = run_cmd([ADB, "devices"], timeout=10)
    devices = []
    if ok:
        for line in out.splitlines()[1:]:
            line = line.strip()
            if line and "\tdevice" in line:
                dev_id = line.split("\t")[0]
                devices.append({
                    "id": dev_id,
                    "wireless": ":" in dev_id,
                    "model": _device_model(dev_id),
                })
    return devices


def _parse_device_network_ips(output):
    """Parse Android `ip -f inet addr` output and prefer Wi-Fi interfaces."""
    candidates = []
    interface = ""
    preferred_prefixes = ("wlan", "wifi", "ap", "swlan", "eth")
    for line in output.splitlines():
        match = re.match(r"^\d+:\s+([^:@]+)", line)
        if match:
            interface = match.group(1)
            continue
        match = re.search(r"\binet\s+(\d+(?:\.\d+){3})/", line)
        if not match or not interface.lower().startswith(preferred_prefixes):
            continue
        try:
            address = ipaddress.ip_address(match.group(1))
        except ValueError:
            continue
        if address.is_private and not address.is_loopback and not address.is_link_local:
            candidates.append({"ip": str(address), "interface": interface})
    return candidates


def detect_device_network(dev_id):
    """Detect a phone's LAN/hotspot address through an existing ADB link."""
    if not dev_id:
        return []
    ok, out = run_cmd([ADB, "-s", dev_id, "shell", "ip", "-f", "inet", "addr"],
                      timeout=8)
    return _parse_device_network_ips(out) if ok else []


def valid_wireless_target(ip, port):
    try:
        address = ipaddress.ip_address(ip)
        port_num = int(port)
    except (ValueError, TypeError):
        return False
    return address.version == 4 and not address.is_unspecified and 1 <= port_num <= 65535


def pick_scrcpy_port():
    """让 Windows 选择一个当前可绑定的本地 TCP 端口。

    scrcpy 默认只尝试 27183:27199；Hyper-V/WSL 等组件可能把整段端口
    加入 Windows 排除范围，导致 bind 返回 10013。绑定 0 会避开这些范围。
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def build_scrcpy_command(p, local_port=None):
    """根据前端参数构建 scrcpy 命令（与原 GUI 逻辑一致）。"""
    cmd = [SCRCPY, "--serial", p["device"]]
    if local_port is not None:
        cmd += ["--port", str(local_port)]
    if p.get("rotation") and p["rotation"] != "0":
        cmd += ["--orientation", p["rotation"]]
    if p.get("fps"):
        cmd += ["--max-fps", str(p["fps"])]
    if p.get("bitrate"):
        cmd += ["--video-bit-rate", p["bitrate"]]
    size_map = {"720": "1280", "1080": "1920", "1440": "2560", "2160": "3840"}
    if p.get("resolution") and p["resolution"] in size_map:
        cmd += ["--max-size", size_map[p["resolution"]]]
    flags = p.get("flags", {})
    flag_map = {
        "showTouches": "--show-touches",
        "stayAwake": "--stay-awake",
        "noAudio": "--no-audio",
        "turnScreenOff": "--turn-screen-off",
        "alwaysOnTop": "--always-on-top",
        "fullscreen": "--fullscreen",
        "noControl": "--no-control",
        "disableScreensaver": "--disable-screensaver",
    }
    for k, v in flag_map.items():
        if flags.get(k):
            cmd.append(v)
    return cmd


# ---------------- HTTP 处理 ----------------

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    # 静默访问日志，避免刷控制台
    def log_message(self, fmt, *args):
        pass

    # ---- 工具 ----
    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path, download_name=None):
        try:
            data = Path(path).read_bytes()
        except OSError:
            self._send_json({"ok": False, "error": "文件不存在"}, 404)
            return
        ext = Path(path).suffix.lower()
        self.send_response(200)
        self.send_header("Content-Type", MIME.get(ext, "application/octet-stream"))
        self.send_header("Content-Length", str(len(data)))
        if download_name:
            self.send_header("Content-Disposition",
                             f'attachment; filename="{download_name}"')
        self.end_headers()
        self.wfile.write(data)

    def _read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(length) if length else b""

    def _read_json(self):
        try:
            return json.loads(self._read_body() or b"{}")
        except json.JSONDecodeError:
            return {}

    # ---- 路由 ----
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            return self._send_file(STATIC_DIR / "index.html")
        if path.startswith("/static/"):
            target = (BASE_DIR / unquote(path.lstrip("/"))).resolve()
            if STATIC_DIR.resolve() in target.parents and target.is_file():
                return self._send_file(target)
            return self._send_json({"ok": False, "error": "not found"}, 404)
        if path.startswith("/downloads/"):
            name = os.path.basename(unquote(path))
            target = DOWNLOAD_DIR / name
            if target.is_file():
                return self._send_file(target, download_name=name)
            return self._send_json({"ok": False, "error": "not found"}, 404)
        if path.startswith("/wallpapers/"):
            name = os.path.basename(unquote(path))
            target = WALLPAPER_DIR / name
            if target.is_file() and target.suffix.lower() in WALLPAPER_EXTS:
                return self._send_file(target)
            return self._send_json({"ok": False, "error": "not found"}, 404)

        if path == "/api/wallpapers":
            files = sorted(f.name for f in WALLPAPER_DIR.iterdir()
                           if f.is_file() and f.suffix.lower() in WALLPAPER_EXTS)
            return self._send_json({"ok": True, "wallpapers": files})

        if path == "/api/state":
            snap = STATE.snapshot()
            snap["devices"] = list_devices()
            snap["recordings"] = sorted(
                (f.name for f in DOWNLOAD_DIR.iterdir() if f.is_file()),
                reverse=True)[:20]
            return self._send_json({"ok": True, **snap})

        if path == "/api/logs":
            since = int(parse_qs(parsed.query).get("since", ["0"])[0])
            return self._send_json({"ok": True, "logs": STATE.logs_since(since)})

        if path == "/api/command":
            p = parse_qs(parsed.query)
            # 仅预览：需要 device 参数
            device = p.get("device", [""])[0]
            if not device:
                return self._send_json({"ok": False, "error": "缺少 device"})
            params = {
                "device": device,
                "rotation": p.get("rotation", ["0"])[0],
                "fps": p.get("fps", ["60"])[0],
                "bitrate": p.get("bitrate", ["4M"])[0],
                "resolution": p.get("resolution", [""])[0],
                "flags": {k: p.get(k, ["0"])[0] == "1" for k in (
                    "showTouches", "stayAwake", "noAudio", "turnScreenOff",
                    "alwaysOnTop", "fullscreen", "noControl", "disableScreensaver")},
            }
            cmd = build_scrcpy_command(params)
            # 用相对名展示更友好
            pretty = " ".join(cmd).replace(SCRCPY, "scrcpy.exe")
            return self._send_json({"ok": True, "command": pretty})

        return self._send_json({"ok": False, "error": "unknown endpoint"}, 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_json()

        # ---- 设备选择 ----
        if path == "/api/device/select":
            dev = body.get("device", "")
            with STATE.lock:
                STATE.selected_device = dev
            STATE.log(f"📱 已选择设备: {dev}" if dev else "已取消选择设备")
            return self._send_json({"ok": True})

        # ---- 无线连接 ----
        if path == "/api/wireless/detect":
            dev = body.get("device") or STATE.snapshot()["selected"]
            if not dev:
                return self._send_json({"ok": False, "error": "请先选择一台 USB 设备"})
            candidates = detect_device_network(dev)
            if not candidates:
                return self._send_json({
                    "ok": False,
                    "error": "未检测到手机的 Wi-Fi 或热点 IP，请确认网络已连接",
                })
            chosen = candidates[0]
            STATE.log(f"🔎 已识别设备 IP: {chosen['ip']} ({chosen['interface']})")
            return self._send_json({"ok": True, **chosen, "candidates": candidates})

        if path == "/api/wireless/enable":
            dev = STATE.snapshot()["selected"]
            if not dev:
                return self._send_json({"ok": False, "error": "请先选择设备"})
            port = str(body.get("port", "5555"))
            ok, out = run_cmd([ADB, "-s", dev, "tcpip", port], timeout=10)
            STATE.log(f"{'✅' if ok else '❌'} 启用 TCP/IP 端口 {port}: {out}")
            return self._send_json({"ok": ok, "output": out})

        if path == "/api/wireless/connect":
            ip = body.get("ip", "").strip()
            port = str(body.get("port", "5555")).strip()
            if not valid_wireless_target(ip, port):
                return self._send_json({"ok": False, "error": "IP 地址或端口不正确"})
            target = f"{ip}:{port}"
            STATE.log(f"📶 尝试无线连接 {target} ...")
            ok, out = run_cmd([ADB, "connect", target], timeout=30)
            success = ok and "connected" in out.lower()
            STATE.log(f"{'✅' if success else '❌'} 无线连接 {target}: {out}")
            return self._send_json({"ok": success, "output": out})

        if path == "/api/wireless/disconnect":
            target = body.get("target", "").strip()
            ok, out = run_cmd([ADB, "disconnect", target] if target
                              else [ADB, "disconnect"], timeout=10)
            STATE.log(f"📶 断开无线连接: {out or target or '全部'}")
            return self._send_json({"ok": True, "output": out})

        # ---- 投屏 ----
        if path == "/api/mirror/start":
            if STATE.snapshot()["mirroring"]:
                return self._send_json({"ok": False, "error": "投屏已在运行中"})
            dev = body.get("device") or STATE.snapshot()["selected"]
            if not dev:
                return self._send_json({"ok": False, "error": "请先选择设备"})
            body["device"] = dev
            local_port = pick_scrcpy_port()
            cmd = build_scrcpy_command(body, local_port=local_port)
            STATE.log(f"🚀 启动投屏: {' '.join(cmd).replace(SCRCPY, 'scrcpy.exe')}")
            try:
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, creationflags=CREATE_NO_WINDOW)
            except Exception as e:
                STATE.log(f"❌ 启动投屏失败: {e}")
                return self._send_json({"ok": False, "error": str(e)})
            with STATE.lock:
                STATE.mirror_proc = proc
                STATE.mirror_since = time.time()
            STATE._watch(proc, "mirror")
            return self._send_json({"ok": True})

        if path == "/api/mirror/stop":
            with STATE.lock:
                proc = STATE.mirror_proc
            if not proc:
                return self._send_json({"ok": False, "error": "当前没有投屏进程"})
            proc.terminate()
            STATE.log("⏹️ 已请求停止投屏")
            return self._send_json({"ok": True})

        # ---- 快速录制 ----
        if path == "/api/record/start":
            if STATE.snapshot()["recording"]:
                return self._send_json({"ok": False, "error": "录制已在进行中"})
            dev = body.get("device") or STATE.snapshot()["selected"]
            if not dev:
                return self._send_json({"ok": False, "error": "请先选择设备"})
            fmt = body.get("format", "mp4")
            if fmt not in ("mp4", "mkv"):
                fmt = "mp4"
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = str(DOWNLOAD_DIR / f"record_{ts}.{fmt}")
            local_port = pick_scrcpy_port()
            cmd = [SCRCPY, "--serial", dev, "--port", str(local_port),
                   "--record", filename]
            if body.get("noDisplay"):
                cmd.append("--no-display")
            STATE.log(f"⏺️ 开始录制 → {os.path.basename(filename)}")
            try:
                proc = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, creationflags=CREATE_NO_WINDOW)
            except Exception as e:
                STATE.log(f"❌ 启动录制失败: {e}")
                return self._send_json({"ok": False, "error": str(e)})
            with STATE.lock:
                STATE.record_proc = proc
                STATE.record_file = filename
                STATE.record_since = time.time()
            STATE._watch(proc, "record")
            return self._send_json({"ok": True, "file": os.path.basename(filename)})

        if path == "/api/record/stop":
            with STATE.lock:
                proc = STATE.record_proc
            if not proc:
                return self._send_json({"ok": False, "error": "当前没有录制进程"})
            # scrcpy 需要 Ctrl+C 平滑结束；terminate 在 Windows 下等价
            proc.terminate()
            STATE.log("⏹️ 已请求停止录制，正在收尾写盘...")
            return self._send_json({"ok": True})

        # ---- 截图 ----
        if path == "/api/screenshot":
            dev = STATE.snapshot()["selected"]
            if not dev:
                return self._send_json({"ok": False, "error": "请先选择设备"})
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            name = f"screenshot_{ts}.png"
            target = DOWNLOAD_DIR / name
            STATE.log("📷 正在截图...")
            try:
                with open(target, "wb") as f:
                    r = subprocess.run(
                        [ADB, "-s", dev, "exec-out", "screencap", "-p"],
                        stdout=f, stderr=subprocess.PIPE, timeout=15,
                        creationflags=CREATE_NO_WINDOW)
                if r.returncode == 0 and target.stat().st_size > 0:
                    STATE.log(f"✅ 截图成功: {name}")
                    return self._send_json({"ok": True, "file": name,
                                            "url": f"/downloads/{name}"})
                target.unlink(missing_ok=True)
                err = (r.stderr or b"").decode("utf-8", "ignore")
                STATE.log(f"❌ 截图失败: {err}")
                return self._send_json({"ok": False, "error": err or "截图失败"})
            except Exception as e:
                target.unlink(missing_ok=True)
                STATE.log(f"❌ 截图异常: {e}")
                return self._send_json({"ok": False, "error": str(e)})

        # ---- APK 安装 / 文件推送（浏览器上传字节流）----
        if path in ("/api/apk/install", "/api/file/push"):
            dev = STATE.snapshot()["selected"]
            if not dev:
                return self._send_json({"ok": False, "error": "请先选择设备"})
            raw = self._read_body() if not body else None
            # _read_json 已消费 body；此处重新按原始字节读取
            # 因此这两个端点约定：不要在 do_POST 开头读 json。
            return self._send_json({"ok": False, "error": "bad request"}, 400)

        # ---- 文件拉取 ----
        if path == "/api/file/pull":
            dev = STATE.snapshot()["selected"]
            if not dev:
                return self._send_json({"ok": False, "error": "请先选择设备"})
            remote = body.get("path", "").strip()
            if not remote:
                return self._send_json({"ok": False, "error": "请输入设备文件路径"})
            name = os.path.basename(remote.rstrip("/")) or "pulled_file"
            target = DOWNLOAD_DIR / name
            STATE.log(f"📥 从设备拉取: {remote}")
            ok, out = run_cmd([ADB, "-s", dev, "pull", remote, str(target)],
                              timeout=120)
            if ok and target.exists():
                STATE.log(f"✅ 拉取成功: {name}")
                return self._send_json({"ok": True, "file": name,
                                        "url": f"/downloads/{name}"})
            STATE.log(f"❌ 拉取失败: {out}")
            return self._send_json({"ok": False, "error": out or "拉取失败"})

        # ---- 日志 ----
        if path == "/api/logs/clear":
            STATE.clear_logs()
            STATE.log("🗑️ 日志已清空")
            return self._send_json({"ok": True})

        return self._send_json({"ok": False, "error": "unknown endpoint"}, 404)

    def do_PUT(self):
        """文件上传端点（原始字节流）:
        PUT /api/apk/install?name=app.apk   -> adb install
        PUT /api/file/push?name=x&dest=/sdcard/Download/ -> adb push
        """
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        dev = STATE.snapshot()["selected"]
        if not dev:
            return self._send_json({"ok": False, "error": "请先选择设备"})
        name = os.path.basename(qs.get("name", ["upload.bin"])[0])
        raw = self._read_body()
        if not raw:
            return self._send_json({"ok": False, "error": "空文件"})

        if parsed.path == "/api/apk/install":
            if not name.lower().endswith(".apk"):
                return self._send_json({"ok": False, "error": "仅支持 .apk 文件"})
            tmp = DOWNLOAD_DIR / f".tmp_{int(time.time())}_{name}"
            tmp.write_bytes(raw)
            STATE.log(f"📦 开始安装 APK: {name} ({len(raw)/1024/1024:.1f} MB)")
            ok, out = run_cmd([ADB, "-s", dev, "install", str(tmp)], timeout=300)
            tmp.unlink(missing_ok=True)
            success = ok and "success" in out.lower()
            STATE.log(f"{'✅' if success else '❌'} APK 安装: {out}")
            return self._send_json({"ok": success, "output": out})

        if parsed.path == "/api/file/push":
            dest = qs.get("dest", ["/sdcard/Download/"])[0]
            tmp = DOWNLOAD_DIR / f".tmp_{int(time.time())}_{name}"
            tmp.write_bytes(raw)
            STATE.log(f"📤 推送文件到设备: {name} → {dest}")
            ok, out = run_cmd([ADB, "-s", dev, "push", str(tmp), dest], timeout=300)
            tmp.unlink(missing_ok=True)
            STATE.log(f"{'✅' if ok else '❌'} 文件推送: {out}")
            return self._send_json({"ok": ok, "output": out})

        return self._send_json({"ok": False, "error": "unknown endpoint"}, 404)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=7100)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    # 检查运行环境
    if not os.path.exists(ADB):
        print(f"[警告] 未找到 adb.exe: {ADB}")
    if not os.path.exists(SCRCPY):
        print(f"[警告] 未找到 scrcpy.exe: {SCRCPY}")

    STATE.log("🚀 Web 控制中心已启动")
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    url = f"http://{args.host}:{args.port}/"
    print(f"Scrcpy Web 控制中心运行中: {url}")
    print("按 Ctrl+C 停止服务")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        # 退出时清理子进程
        snap = STATE.snapshot()
        with STATE.lock:
            for proc in (STATE.mirror_proc, STATE.record_proc):
                if proc:
                    proc.terminate()
        server.server_close()


if __name__ == "__main__":
    main()
