#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrcpy 图形化控制软件
功能：设备管理、投屏控制、录制、参数配置
作者：AI Assistant
版本：1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import subprocess
import threading
import time
import os
import json
import re
from datetime import datetime
import queue
import sys

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，兼容打包后的exe"""
    try:
        # PyInstaller创建临时文件夹，并将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        # 如果不是打包后的exe，使用当前目录
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class ScrcpyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Scrcpy 投屏控制中心 v1.0")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # 设置图标
        if os.path.exists("icon.png"):
            try:
                from PIL import Image, ImageTk
                icon = Image.open("icon.png")
                photo = ImageTk.PhotoImage(icon)
                self.root.iconphoto(False, photo)
            except:
                pass
        
        # 初始化变量
        self.devices = []
        self.selected_device = tk.StringVar()
        self.scrcpy_process = None
        self.recording_process = None
        self.is_recording = False
        self.recording_file = ""
        self.log_queue = queue.Queue()
        
        # 设置可执行文件路径
        self.adb_path = get_resource_path("adb.exe")
        self.scrcpy_path = get_resource_path("scrcpy.exe")
        
        # 检查必要文件
        if not os.path.exists(self.adb_path):
            messagebox.showerror("错误", f"找不到adb.exe文件: {self.adb_path}")
            return
        
        if not os.path.exists(self.scrcpy_path):
            messagebox.showerror("错误", f"找不到scrcpy.exe文件: {self.scrcpy_path}")
            return
        
        # 创建界面
        self.create_widgets()
        
        # 启动设备检测线程
        self.start_device_monitor()
        
        # 启动日志更新线程
        self.update_log()
        
        # 启动时记录路径信息
        self.log_message(f"ADB路径: {self.adb_path}")
        self.log_message(f"Scrcpy路径: {self.scrcpy_path}")

    def create_widgets(self):
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="Scrcpy 投屏控制中心", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 设备管理区域
        self.create_device_section(main_frame)
        
        # 模式选择区域
        self.create_mode_section(main_frame)
        
        # 控制按钮区域
        self.create_control_section(main_frame)
        
        # 日志区域
        self.create_log_section(main_frame)

    def create_device_section(self, parent):
        # 设备管理框架
        device_frame = ttk.LabelFrame(parent, text="设备管理", padding="10")
        device_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        device_frame.columnconfigure(1, weight=1)
        
        # 设备列表
        ttk.Label(device_frame, text="已连接设备:").grid(row=0, column=0, sticky="w")
        self.device_listbox = tk.Listbox(device_frame, height=3)
        self.device_listbox.grid(row=1, column=0, columnspan=2, sticky="ew", pady=5)
        
        # 设备操作按钮
        device_btn_frame = ttk.Frame(device_frame)
        device_btn_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
        
        ttk.Button(device_btn_frame, text="刷新设备", 
                  command=self.refresh_devices).pack(side="left", padx=(0, 5))
        ttk.Button(device_btn_frame, text="连接设备", 
                  command=self.connect_device).pack(side="left", padx=(0, 5))
        ttk.Button(device_btn_frame, text="断开连接", 
                  command=self.disconnect_device).pack(side="left")

    def create_mode_section(self, parent):
        # 模式选择框架
        mode_frame = ttk.LabelFrame(parent, text="投屏模式", padding="10")
        mode_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        mode_frame.columnconfigure(1, weight=1)
        
        # 预设模式
        preset_frame = ttk.Frame(mode_frame)
        preset_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        ttk.Label(preset_frame, text="预设模式:").grid(row=0, column=0, sticky="w")
        
        self.mode_var = tk.StringVar(value="custom")
        modes = [
            ("游戏模式", "game"),
            ("高性能游戏模式", "ultra"),
            ("视频模式", "video"),
            ("自定义模式", "custom")
        ]
        
        for i, (text, value) in enumerate(modes):
            ttk.Radiobutton(preset_frame, text=text, variable=self.mode_var, 
                           value=value, command=self.on_mode_change).grid(row=0, column=i+1, padx=(10, 0))
        
        # 自定义参数框架
        self.custom_frame = ttk.LabelFrame(mode_frame, text="自定义参数", padding="10")
        self.custom_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.custom_frame.columnconfigure(1, weight=1)
        
        # 基本参数
        basic_frame = ttk.Frame(self.custom_frame)
        basic_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        
        # 第一行参数
        ttk.Label(basic_frame, text="旋转角度:").grid(row=0, column=0, sticky="w")
        self.rotation_var = tk.StringVar(value="0")
        rotation_combo = ttk.Combobox(basic_frame, textvariable=self.rotation_var, 
                                     values=["0", "90", "180", "270"], width=10)
        rotation_combo.grid(row=0, column=1, padx=(5, 20))
        
        ttk.Label(basic_frame, text="最大帧率:").grid(row=0, column=2, sticky="w")
        self.fps_var = tk.StringVar(value="60")
        fps_combo = ttk.Combobox(basic_frame, textvariable=self.fps_var, 
                                values=["30", "60", "90", "120"], width=10)
        fps_combo.grid(row=0, column=3, padx=(5, 20))
        
        ttk.Label(basic_frame, text="比特率:").grid(row=0, column=4, sticky="w")
        self.bitrate_var = tk.StringVar(value="4M")
        bitrate_combo = ttk.Combobox(basic_frame, textvariable=self.bitrate_var, 
                                    values=["1M", "2M", "4M", "6M", "8M"], width=10)
        bitrate_combo.grid(row=0, column=5, padx=(5, 0))
        
        # 第二行参数
        ttk.Label(basic_frame, text="最大尺寸:").grid(row=1, column=0, sticky="w")
        self.size_var = tk.StringVar(value="1920")
        size_combo = ttk.Combobox(basic_frame, textvariable=self.size_var, 
                                 values=["800", "1280", "1920", "2560"], width=10)
        size_combo.grid(row=1, column=1, padx=(5, 20))
        
        # 复选框选项
        self.show_touches_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(basic_frame, text="显示触摸", 
                       variable=self.show_touches_var).grid(row=1, column=2, padx=(20, 0))
        
        self.stay_awake_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(basic_frame, text="防止休眠", 
                       variable=self.stay_awake_var).grid(row=1, column=3, padx=(20, 0))
        
        self.no_audio_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(basic_frame, text="禁用音频", 
                       variable=self.no_audio_var).grid(row=1, column=4, padx=(20, 0))

    def create_control_section(self, parent):
        control_frame = ttk.LabelFrame(parent, text="投屏控制", padding="10")
        control_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        
        # 第一行按钮
        btn_frame1 = ttk.Frame(control_frame)
        btn_frame1.pack(fill="x", pady=(0, 5))
        
        ttk.Button(btn_frame1, text="开始投屏", command=self.start_mirroring).pack(side="left", padx=(0, 10))
        ttk.Button(btn_frame1, text="停止投屏", command=self.stop_mirroring).pack(side="left", padx=(0, 10))
        ttk.Button(btn_frame1, text="开始录制", command=self.start_recording).pack(side="left", padx=(0, 10))
        ttk.Button(btn_frame1, text="停止录制", command=self.stop_recording).pack(side="left", padx=(0, 10))
        
        # 第二行按钮
        btn_frame2 = ttk.Frame(control_frame)
        btn_frame2.pack(fill="x", pady=(0, 5))
        
        ttk.Button(btn_frame2, text="仅录制模式", command=self.start_record_only).pack(side="left", padx=(0, 10))
        ttk.Button(btn_frame2, text="测试录制文件", command=self.test_record_file).pack(side="left", padx=(0, 10))
        
        # 录制选项
        options_frame = ttk.Frame(control_frame)
        options_frame.pack(fill="x", pady=(0, 5))
        
        self.record_format_var = tk.StringVar(value="mp4")
        ttk.Label(options_frame, text="录制格式:").pack(side="left")
        ttk.Combobox(options_frame, textvariable=self.record_format_var, 
                     values=["mp4", "mkv"], width=8).pack(side="left", padx=(5, 20))
        
        # 状态显示
        self.status_label = ttk.Label(control_frame, text="状态: 未连接")
        self.status_label.pack(side="right")

    def create_log_section(self, parent):
        # 日志框架
        log_frame = ttk.LabelFrame(parent, text="运行日志", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        
        # 日志控制按钮
        log_btn_frame = ttk.Frame(log_frame)
        log_btn_frame.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        
        ttk.Button(log_btn_frame, text="清空日志", 
                  command=self.clear_log).pack(side="left")
        ttk.Button(log_btn_frame, text="保存日志", 
                  command=self.save_log).pack(side="left", padx=(10, 0))

    def start_device_monitor(self):
        """启动设备监控线程"""
        def monitor():
            while True:
                self.refresh_devices()
                time.sleep(2)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

    def refresh_devices(self):
        """刷新设备列表"""
        try:
            result = subprocess.run([self.adb_path, "devices"], 
                                  capture_output=True, text=True, timeout=10,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
                self.devices = []
                
                for line in lines:
                    if line.strip() and '\tdevice' in line:
                        device_id = line.split('\t')[0]
                        self.devices.append(device_id)
                
                # 更新UI（在主线程中）
                self.root.after(0, self.update_device_list)
                
        except Exception as e:
            self.log_message(f"刷新设备失败: {e}")

    def update_device_list(self):
        """更新设备列表UI"""
        self.device_listbox.delete(0, tk.END)
        for device in self.devices:
            self.device_listbox.insert(tk.END, device)
        
        if self.devices:
            self.status_label.config(text=f"状态: 发现 {len(self.devices)} 个设备")
        else:
            self.status_label.config(text="状态: 未发现设备")

    def connect_device(self):
        """连接选中的设备"""
        selection = self.device_listbox.curselection()
        if selection:
            device_id = self.devices[selection[0]]
            self.selected_device.set(device_id)
            self.log_message(f"已选择设备: {device_id}")
            self.status_label.config(text=f"状态: 已选择设备 {device_id}")
        else:
            messagebox.showwarning("警告", "请先选择一个设备")

    def disconnect_device(self):
        """断开设备连接"""
        self.selected_device.set("")
        self.log_message("已断开设备连接")
        self.status_label.config(text="状态: 未连接")

    def on_mode_change(self):
        """模式改变时的处理"""
        mode = self.mode_var.get()
        if mode == "game":
            self.set_game_mode()
        elif mode == "ultra":
            self.set_ultra_mode()
        elif mode == "video":
            self.set_video_mode()
        elif mode == "custom":
            self.set_custom_mode()

    def set_game_mode(self):
        """设置游戏模式"""
        self.rotation_var.set("270")
        self.fps_var.set("60")
        self.bitrate_var.set("4M")
        self.size_var.set("1920")
        self.show_touches_var.set(False)
        self.stay_awake_var.set(True)
        self.no_audio_var.set(True)
        self.log_message("已切换到游戏模式")

    def set_ultra_mode(self):
        """设置高性能游戏模式"""
        self.rotation_var.set("270")
        self.fps_var.set("120")
        self.bitrate_var.set("8M")
        self.size_var.set("2560")
        self.show_touches_var.set(False)
        self.stay_awake_var.set(True)
        self.no_audio_var.set(True)
        self.log_message("已切换到高性能游戏模式")

    def set_video_mode(self):
        """设置视频模式"""
        self.rotation_var.set("0")
        self.fps_var.set("30")
        self.bitrate_var.set("2M")
        self.size_var.set("1280")
        self.show_touches_var.set(False)
        self.stay_awake_var.set(True)
        self.no_audio_var.set(False)
        self.log_message("已切换到视频模式")

    def set_custom_mode(self):
        """设置自定义模式"""
        self.log_message("已切换到自定义模式")

    def build_scrcpy_command(self):
        """构建scrcpy命令"""
        if not self.selected_device.get():
            raise ValueError("未选择设备")
        
        cmd = [self.scrcpy_path, "--serial", self.selected_device.get()]
        
        if self.rotation_var.get() != "0":
            cmd.extend(["--orientation", self.rotation_var.get()])
        
        if self.fps_var.get():
            cmd.extend(["--max-fps", self.fps_var.get()])
        
        if self.bitrate_var.get():
            cmd.extend(["--video-bit-rate", self.bitrate_var.get()])
        
        if self.size_var.get():
            cmd.extend(["--max-size", self.size_var.get()])
        
        if self.show_touches_var.get():
            cmd.append("--show-touches")
        
        if self.stay_awake_var.get():
            cmd.append("--stay-awake")
        
        if self.no_audio_var.get():
            cmd.append("--no-audio")
        
        return cmd

    def start_mirroring(self):
        """开始投屏"""
        try:
            if self.scrcpy_process:
                messagebox.showwarning("警告", "投屏已在运行中")
                return
            
            cmd = self.build_scrcpy_command()
            self.log_message(f"启动投屏: {' '.join(cmd)}")
            
            self.scrcpy_process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
            self.status_label.config(text="状态: 投屏中")
            self.log_message("投屏已启动")
            
        except Exception as e:
            messagebox.showerror("错误", f"启动投屏失败: {e}")
            self.log_message(f"启动投屏失败: {e}")

    def stop_mirroring(self):
        """停止投屏"""
        if self.scrcpy_process:
            self.scrcpy_process.terminate()
            self.scrcpy_process = None
            self.status_label.config(text="状态: 已停止投屏")
            self.log_message("投屏已停止")

    def start_recording(self):
        try:
            if self.is_recording:
                messagebox.showwarning("警告", "录制已在运行中")
                return
            
            # 获取当前时间作为默认文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"scrcpy_record_{timestamp}.mp4"
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".mp4",
                filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
                title="选择录制文件保存位置",
                initialfile=default_filename
            )
            
            if not filename:
                return
            
            # 确保文件路径使用绝对路径
            filename = os.path.abspath(filename)
            
            cmd = self.build_scrcpy_command()
            cmd.extend(["--record", filename])
            
            # 添加录制优化参数
            if "--no-display" not in cmd:
                # 如果不是仅录制模式，可以添加一些优化参数
                pass
            
            self.log_message(f"开始录制: {' '.join(cmd)}")
            self.log_message(f"录制文件路径: {filename}")
            
            # 检查目录是否存在且可写
            record_dir = os.path.dirname(filename)
            if not os.path.exists(record_dir):
                os.makedirs(record_dir, exist_ok=True)
                self.log_message(f"创建录制目录: {record_dir}")
            
            self.recording_process = subprocess.Popen(
                cmd, 
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.is_recording = True
            self.recording_file = filename
            self.status_label.config(text="状态: 录制中")
            self.log_message(f"录制已开始，保存到: {filename}")
            
            # 启动录制监控线程
            self.start_recording_monitor()
            
        except Exception as e:
            messagebox.showerror("错误", f"开始录制失败: {e}")
            self.log_message(f"开始录制失败: {e}")

    def start_recording_monitor(self):
        """启动录制监控线程"""
        def monitor_recording():
            try:
                while self.is_recording and self.recording_process:
                    # 检查进程是否还在运行
                    if self.recording_process.poll() is not None:
                        # 进程已结束
                        self.root.after(0, self.on_recording_finished)
                        break
                    time.sleep(1)
            except Exception as e:
                self.log_message(f"录制监控错误: {e}")
        
        thread = threading.Thread(target=monitor_recording, daemon=True)
        thread.start()

    def on_recording_finished(self):
        """录制完成后的处理"""
        if hasattr(self, 'recording_file') and os.path.exists(self.recording_file):
            file_size = os.path.getsize(self.recording_file)
            if file_size > 0:
                self.log_message(f"录制完成，文件大小: {file_size} 字节")
                self.log_message(f"录制文件位置: {self.recording_file}")
                
                # 询问是否打开录制文件所在目录
                if messagebox.askyesno("录制完成", 
                                     f"录制完成！\n文件保存到: {self.recording_file}\n\n是否打开文件所在目录？"):
                    try:
                        import subprocess
                        subprocess.run(['explorer', '/select,', self.recording_file.replace('/', '\\')], 
                                     creationflags=subprocess.CREATE_NO_WINDOW)
                    except Exception as e:
                        self.log_message(f"打开目录失败: {e}")
            else:
                self.log_message("警告: 录制文件为空，可能录制失败")
                messagebox.showwarning("警告", "录制文件为空，录制可能失败")
        else:
            self.log_message("警告: 录制文件不存在")
            messagebox.showwarning("警告", "录制文件不存在，录制可能失败")

    def stop_recording(self):
        if self.recording_process:
            try:
                # 优雅地终止录制进程
                self.recording_process.terminate()
                
                # 等待进程结束
                try:
                    self.recording_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # 如果5秒后还没结束，强制终止
                    self.recording_process.kill()
                    self.log_message("强制终止录制进程")
                
                self.recording_process = None
                self.is_recording = False
                self.status_label.config(text="状态: 录制已停止")
                self.log_message("录制已停止")
                
                # 延迟检查录制文件
                self.root.after(1000, self.on_recording_finished)
                
            except Exception as e:
                self.log_message(f"停止录制时出错: {e}")
                self.recording_process = None
                self.is_recording = False

    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_queue.put(log_entry)

    def update_log(self):
        """更新日志显示"""
        try:
            while True:
                log_entry = self.log_queue.get_nowait()
                self.log_text.insert(tk.END, log_entry)
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        
        # 每100ms更新一次
        self.root.after(100, self.update_log)

    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)

    def save_log(self):
        """保存日志"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="保存日志文件"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log_message(f"日志已保存到: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"保存日志失败: {e}")

    def on_closing(self):
        """程序关闭时的处理"""
        if self.scrcpy_process:
            self.scrcpy_process.terminate()
        if self.recording_process:
            self.recording_process.terminate()
        self.root.destroy()

    def start_record_only(self):
        """仅录制模式，不显示投屏窗口"""
        try:
            if self.is_recording:
                messagebox.showwarning("警告", "录制已在运行中")
                return
            
            if not self.selected_device.get():
                messagebox.showwarning("警告", "请先选择设备")
                return
            
            # 获取当前时间作为默认文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"scrcpy_record_only_{timestamp}.mp4"
            
            filename = filedialog.asksaveasfilename(
                defaultextension=f".{self.record_format_var.get()}",
                filetypes=[(f"{self.record_format_var.get().upper()} files", f"*.{self.record_format_var.get()}"), 
                          ("All files", "*.*")],
                title="选择录制文件保存位置",
                initialfile=default_filename
            )
            
            if not filename:
                return
            
            # 确保文件路径使用绝对路径
            filename = os.path.abspath(filename)
            
            cmd = self.build_scrcpy_command()
            cmd.extend(["--record", filename, "--no-display"])
            
            # 添加录制格式
            if self.record_format_var.get() != "mp4":
                cmd.extend(["--record-format", self.record_format_var.get()])
            
            self.log_message(f"开始仅录制模式: {' '.join(cmd)}")
            self.log_message(f"录制文件路径: {filename}")
            
            # 检查目录是否存在且可写
            record_dir = os.path.dirname(filename)
            if not os.path.exists(record_dir):
                os.makedirs(record_dir, exist_ok=True)
                self.log_message(f"创建录制目录: {record_dir}")
            
            self.recording_process = subprocess.Popen(
                cmd, 
                creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.is_recording = True
            self.recording_file = filename
            self.status_label.config(text="状态: 仅录制中")
            self.log_message(f"仅录制模式已开始，保存到: {filename}")
            
            # 启动录制监控线程
            self.start_recording_monitor()
            
        except Exception as e:
            messagebox.showerror("错误", f"开始仅录制失败: {e}")
            self.log_message(f"开始仅录制失败: {e}")

    def test_record_file(self):
        """测试录制文件是否可以正常播放"""
        if hasattr(self, 'recording_file') and os.path.exists(self.recording_file):
            filename = self.recording_file
        else:
            filename = filedialog.askopenfilename(
                filetypes=[("Video files", "*.mp4 *.mkv *.avi"), ("All files", "*.*")],
                title="选择要测试的视频文件"
            )
            
        if not filename:
            return
            
        try:
            # 检查文件信息
            file_size = os.path.getsize(filename)
            self.log_message(f"测试文件: {filename}")
            self.log_message(f"文件大小: {file_size} 字节")
            
            if file_size == 0:
                messagebox.showerror("错误", "文件为空，录制可能失败")
                return
            
            # 尝试用默认程序打开
            import subprocess
            result = subprocess.run(['start', '', filename], shell=True, 
                                  capture_output=True, text=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                self.log_message("已用默认程序打开视频文件")
                messagebox.showinfo("成功", f"已用默认程序打开视频文件\n文件大小: {file_size} 字节")
            else:
                self.log_message(f"打开文件失败: {result.stderr}")
                
                # 提供备选方案
                if messagebox.askyesno("打开失败", 
                                     "无法用默认程序打开视频文件。\n可能需要安装视频播放器或编解码器。\n\n是否打开文件所在目录？"):
                    subprocess.run(['explorer', '/select,', filename.replace('/', '\\')], 
                                 creationflags=subprocess.CREATE_NO_WINDOW)
                    
        except Exception as e:
            self.log_message(f"测试文件时出错: {e}")
            messagebox.showerror("错误", f"测试文件时出错: {e}")

def main():
    root = tk.Tk()
    app = ScrcpyGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 