#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrcpy 投屏控制中心 · 原生窗口启动器

- 开发模式：python launcher.py  → 起服务器 + 原生窗口（pywebview）
- 打包模式（PyInstaller frozen）：exe 放在 scrcpy-win64 目录内，
  自动定位旁边的 adb.exe / scrcpy.exe，数据存到 exe 旁 web-ui-data/
- 调试：--no-window 只起服务器；--port N 指定端口
"""

import argparse
import os
import shutil
import socket
import sys
import threading
from pathlib import Path

FROZEN = getattr(sys, "frozen", False)


def setup_env():
    """frozen 模式下把 server.py 的路径指向 exe 旁边。"""
    if not FROZEN:
        return
    exe_dir = Path(sys.executable).resolve().parent
    bundle = Path(getattr(sys, "_MEIPASS", exe_dir))

    data = exe_dir / "web-ui-data"
    (data / "downloads").mkdir(parents=True, exist_ok=True)
    (data / "wallpapers").mkdir(parents=True, exist_ok=True)

    # 首次运行：把内置种子壁纸拷到可写的数据目录
    seed = bundle / "wallpapers"
    target = data / "wallpapers"
    if seed.is_dir() and not any(target.iterdir()):
        for f in seed.iterdir():
            if f.is_file():
                shutil.copy2(f, target / f.name)

    os.environ["SCRCPY_RUNTIME_DIR"] = str(exe_dir)
    os.environ["SCRCPY_STATIC_DIR"] = str(bundle / "static")
    os.environ["SCRCPY_DOWNLOAD_DIR"] = str(data / "downloads")
    os.environ["SCRCPY_WALLPAPER_DIR"] = str(data / "wallpapers")


def pick_port(preferred=None):
    if preferred:
        return preferred
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-window", action="store_true", help="只启动服务器（调试用）")
    args = parser.parse_args()

    setup_env()

    # 必须在环境变量就绪后再导入 server
    import server  # noqa: E402

    port = pick_port(args.port or None)
    httpd = server.ThreadingHTTPServer(("127.0.0.1", port), server.Handler)
    server.STATE.log("🚀 Web 控制中心已启动")
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    url = f"http://127.0.0.1:{port}/"

    if args.no_window:
        print(f"服务器运行中: {url}（Ctrl+C 停止）", flush=True)
        try:
            t.join()
        except KeyboardInterrupt:
            pass
        return

    import webview  # noqa: E402

    webview.create_window(
        "Scrcpy 控制中心",
        url,
        width=1376,
        height=900,
        min_size=(1024, 680),
        text_select=False,
    )
    webview.start()  # 阻塞直到窗口关闭
    httpd.shutdown()


if __name__ == "__main__":
    main()
