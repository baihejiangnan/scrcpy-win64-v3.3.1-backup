#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrcpy 图形化控制软件 - 现代化美化版 v2.1
功能：设备管理、投屏控制、录制、参数配置、无线连接、多设备管理
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import subprocess
import threading
import time
import os
import sys
from datetime import datetime
import queue
import re

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，兼容打包后的exe"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ModernScrcpyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Scrcpy 投屏控制中心 v2.1 - Modern Edition")
        self.root.geometry("1000x750")
        self.root.minsize(900, 650)
        
        # 设置现代化主题
        self.setup_modern_theme()
        
        # 初始化变量
        self.devices = []
        self.selected_device = tk.StringVar()
        self.scrcpy_process = None
        self.recording_process = None
        self.is_recording = False
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
        
        self.create_modern_widgets()
        self.start_device_monitor()
        self.update_log()
        
        # 启动时记录路径信息
        self.log_message("🚀 Scrcpy 现代化控制中心 v2.1 已启动")
        self.log_message(f"📁 ADB路径: {self.adb_path}")
        self.log_message(f"📁 Scrcpy路径: {self.scrcpy_path}")

    def setup_modern_theme(self):
        """设置现代化主题样式"""
        style = ttk.Style()
        
        # 使用现代主题
        try:
            style.theme_use('clam')
        except:
            style.theme_use('default')
        
        # 定义颜色方案
        colors = {
            'bg': '#f5f5f5',
            'card_bg': '#ffffff',
            'primary': '#0078d4',
            'success': '#107c10',
            'warning': '#ff8c00',
            'danger': '#d13438',
            'text': '#323130',
            'text_light': '#605e5c'
        }
        
        # 配置样式
        style.configure('Card.TFrame', background=colors['card_bg'], relief='solid', borderwidth=1)
        style.configure('Modern.TLabel', font=('Segoe UI', 9), background=colors['card_bg'])
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground=colors['primary'])
        style.configure('Heading.TLabel', font=('Segoe UI', 11, 'bold'), background=colors['card_bg'])
        
        # 按钮样式
        style.configure('Primary.TButton', font=('Segoe UI', 9))
        style.configure('Success.TButton', font=('Segoe UI', 9))
        style.configure('Warning.TButton', font=('Segoe UI', 9))
        style.configure('Danger.TButton', font=('Segoe UI', 9))
        
        # 设置根窗口背景
        self.root.configure(bg=colors['bg'])

    def create_modern_widgets(self):
        """创建现代化界面组件"""
        # 主容器 - 减少内边距
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(2, weight=1)
        
        # 标题区域
        self.create_title_section(main_container)
        
        # 主要内容区域 - 减少间距
        content_frame = ttk.Frame(main_container)
        content_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 10))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # 左侧面板
        left_panel = ttk.Frame(content_frame)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_panel.rowconfigure(2, weight=1)
        
        # 右侧面板
        right_panel = ttk.Frame(content_frame)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_panel.rowconfigure(0, weight=1)
        
        # 创建各个区域
        self.create_device_card(left_panel)
        self.create_connection_card(left_panel)
        self.create_mode_card(left_panel)
        self.create_control_card(right_panel)

    def create_title_section(self, parent):
        """创建标题区域"""
        title_frame = ttk.Frame(parent)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        title_frame.columnconfigure(1, weight=1)
        
        # 图标和标题
        title_label = ttk.Label(title_frame, text="🎮 Scrcpy 投屏控制中心", style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky="w")
        
        # 版本信息
        version_label = ttk.Label(title_frame, text="v2.1 Modern Edition", 
                                font=('Segoe UI', 9), foreground='#666666')
        version_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # 状态指示器
        self.status_indicator = ttk.Label(title_frame, text="🔴 未连接", 
                                        font=('Segoe UI', 9, 'bold'))
        self.status_indicator.grid(row=0, column=2, sticky="e")

    def create_device_card(self, parent):
        """创建设备管理卡片"""
        device_card = ttk.LabelFrame(parent, text="📱 设备管理", style='Card.TFrame', padding="10")
        device_card.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        device_card.columnconfigure(0, weight=1)
        
        # 设备列表
        ttk.Label(device_card, text="已连接设备:", style='Modern.TLabel').grid(row=0, column=0, sticky="w", pady=(0, 3))
        
        self.device_listbox = tk.Listbox(device_card, height=3, font=('Segoe UI', 9),
                                       selectbackground='#0078d4', selectforeground='white',
                                       bg='white', fg='#2d2d2d', relief='flat', borderwidth=1)
        self.device_listbox.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        
        # 按钮区域
        btn_frame = ttk.Frame(device_card)
        btn_frame.grid(row=2, column=0, sticky="ew")
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)
        
        ttk.Button(btn_frame, text="🔄 刷新", command=self.refresh_devices, 
                  style='Primary.TButton').grid(row=0, column=0, sticky="ew", padx=(0, 1))
        ttk.Button(btn_frame, text="🔗 连接", command=self.connect_device, 
                  style='Success.TButton').grid(row=0, column=1, sticky="ew", padx=1)
        ttk.Button(btn_frame, text="❌ 断开", command=self.disconnect_device, 
                  style='Danger.TButton').grid(row=0, column=2, sticky="ew", padx=(1, 0))

    def create_connection_card(self, parent):
        """创建无线连接卡片"""
        conn_card = ttk.LabelFrame(parent, text="📶 无线连接", style='Card.TFrame', padding="8")
        conn_card.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        conn_card.columnconfigure(1, weight=1)
        
        # IP地址输入
        ttk.Label(conn_card, text="设备IP:", style='Modern.TLabel').grid(row=0, column=0, sticky="w", pady=1)
        self.ip_var = tk.StringVar(value="192.168.1.100")
        ip_entry = ttk.Entry(conn_card, textvariable=self.ip_var, font=('Segoe UI', 9))
        ip_entry.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=1)
        
        # 端口输入
        ttk.Label(conn_card, text="端口:", style='Modern.TLabel').grid(row=1, column=0, sticky="w", pady=1)
        self.port_var = tk.StringVar(value="5555")
        port_entry = ttk.Entry(conn_card, textvariable=self.port_var, font=('Segoe UI', 9), width=8)
        port_entry.grid(row=1, column=1, sticky="w", padx=(5, 0), pady=1)
        
        # 无线连接按钮
        wireless_btn_frame = ttk.Frame(conn_card)
        wireless_btn_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        wireless_btn_frame.columnconfigure(0, weight=1)
        wireless_btn_frame.columnconfigure(1, weight=1)
        
        ttk.Button(wireless_btn_frame, text="🔌 启用TCP", command=self.enable_tcpip, 
                  style='Warning.TButton').grid(row=0, column=0, sticky="ew", padx=(0, 1))
        ttk.Button(wireless_btn_frame, text="📶 无线连接", command=self.connect_wireless, 
                  style='Success.TButton').grid(row=0, column=1, sticky="ew", padx=(1, 0))

    def create_mode_card(self, parent):
        """创建模式选择卡片"""
        mode_card = ttk.LabelFrame(parent, text="⚙️ 投屏模式", style='Card.TFrame', padding="8")
        mode_card.grid(row=2, column=0, sticky="nsew")
        mode_card.columnconfigure(0, weight=1)
        
        # 预设模式
        ttk.Label(mode_card, text="预设模式:", style='Heading.TLabel').grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.mode_var = tk.StringVar(value="custom")
        modes = [
            ("🎮 游戏模式", "game"),
            ("⚡ 高性能模式", "ultra"), 
            ("📺 视频模式", "video"),
            ("🔧 自定义模式", "custom")
        ]
        
        for i, (text, value) in enumerate(modes):
            ttk.Radiobutton(mode_card, text=text, variable=self.mode_var, value=value, 
                          command=self.on_mode_change).grid(row=i+1, column=0, sticky="w", pady=1)
        
        # 自定义参数 - 减少内边距
        params_frame = ttk.LabelFrame(mode_card, text="参数设置", padding="6")
        params_frame.grid(row=len(modes)+1, column=0, sticky="ew", pady=(8, 0))
        params_frame.columnconfigure(1, weight=1)
        
        # 基础参数
        basic_params = [
            ("旋转:", "rotation_var", ["0", "90", "180", "270"], "0"),
            ("帧率:", "fps_var", ["15", "30", "60", "90", "120"], "60"),
            ("比特率:", "bitrate_var", ["1M", "2M", "4M", "6M", "8M", "12M"], "4M"),
            ("分辨率:", "resolution_var", ["原始", "720", "1080", "1440", "2160"], "1080")
        ]
        
        for i, (label, var_name, values, default) in enumerate(basic_params):
            ttk.Label(params_frame, text=label, style='Modern.TLabel').grid(
                row=i, column=0, sticky="w", pady=1)
            
            var = tk.StringVar(value=default)
            setattr(self, var_name, var)
            
            combo = ttk.Combobox(params_frame, textvariable=var, values=values, 
                               width=8, state="readonly")
            combo.grid(row=i, column=1, sticky="ew", padx=(5, 0), pady=1)
        
        # 高级选项 - 减少内边距
        advanced_frame = ttk.LabelFrame(params_frame, text="高级选项", padding="3")
        advanced_frame.grid(row=len(basic_params), column=0, columnspan=2, sticky="ew", pady=(5, 0))
        advanced_frame.columnconfigure(0, weight=1)
        advanced_frame.columnconfigure(1, weight=1)
        
        # 第一列选项
        col1_frame = ttk.Frame(advanced_frame)
        col1_frame.grid(row=0, column=0, sticky="ew", padx=(0, 3))
        
        self.show_touches_var = tk.BooleanVar(value=False)
        self.stay_awake_var = tk.BooleanVar(value=True)
        self.no_audio_var = tk.BooleanVar(value=False)
        self.turn_screen_off_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(col1_frame, text="显示触摸", variable=self.show_touches_var).pack(anchor="w", pady=1)
        ttk.Checkbutton(col1_frame, text="防止休眠", variable=self.stay_awake_var).pack(anchor="w", pady=1)
        ttk.Checkbutton(col1_frame, text="禁用音频", variable=self.no_audio_var).pack(anchor="w", pady=1)
        ttk.Checkbutton(col1_frame, text="关闭屏幕", variable=self.turn_screen_off_var).pack(anchor="w", pady=1)
        
        # 第二列选项
        col2_frame = ttk.Frame(advanced_frame)
        col2_frame.grid(row=0, column=1, sticky="ew", padx=(3, 0))
        
        self.always_on_top_var = tk.BooleanVar(value=False)
        self.fullscreen_var = tk.BooleanVar(value=False)
        self.no_control_var = tk.BooleanVar(value=False)
        self.disable_screensaver_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(col2_frame, text="窗口置顶", variable=self.always_on_top_var).pack(anchor="w", pady=1)
        ttk.Checkbutton(col2_frame, text="全屏显示", variable=self.fullscreen_var).pack(anchor="w", pady=1)
        ttk.Checkbutton(col2_frame, text="禁用控制", variable=self.no_control_var).pack(anchor="w", pady=1)
        ttk.Checkbutton(col2_frame, text="禁用屏保", variable=self.disable_screensaver_var).pack(anchor="w", pady=1)

    def create_control_card(self, parent):
        """创建控制面板卡片"""
        control_card = ttk.LabelFrame(parent, text="🎮 投屏控制", style='Card.TFrame', padding="8")
        control_card.grid(row=0, column=0, sticky="nsew")
        control_card.columnconfigure(0, weight=1)
        control_card.rowconfigure(4, weight=1)  # 为运行日志添加权重
        
        # 投屏控制
        mirror_frame = ttk.LabelFrame(control_card, text="投屏操作", padding="6")
        mirror_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        mirror_frame.columnconfigure(0, weight=1)
        mirror_frame.columnconfigure(1, weight=1)
        
        ttk.Button(mirror_frame, text="▶️ 开始投屏", command=self.start_mirroring, 
                  style='Success.TButton').grid(row=0, column=0, sticky="ew", padx=(0, 2))
        ttk.Button(mirror_frame, text="⏹️ 停止投屏", command=self.stop_mirroring, 
                  style='Danger.TButton').grid(row=0, column=1, sticky="ew", padx=(2, 0))
        
        # 录制控制 - 只保留快录功能
        record_frame = ttk.LabelFrame(control_card, text="录制操作", padding="6")
        record_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        record_frame.columnconfigure(0, weight=1)
        
        ttk.Button(record_frame, text="⚡ 快录", command=self.quick_record, 
                  style='Warning.TButton').grid(row=0, column=0, sticky="ew")
        
        # 录制选项
        format_frame = ttk.Frame(record_frame)
        format_frame.grid(row=1, column=0, sticky="ew", pady=(3, 0))
        
        ttk.Label(format_frame, text="格式:", style='Modern.TLabel').pack(side="left")
        self.record_format_var = tk.StringVar(value="mp4")
        ttk.Combobox(format_frame, textvariable=self.record_format_var, 
                    values=["mp4", "mkv", "avi"], width=6, state="readonly").pack(side="left", padx=(5, 0))
        
        # 快捷操作
        quick_frame = ttk.LabelFrame(control_card, text="快捷操作", padding="6")
        quick_frame.grid(row=2, column=0, sticky="ew", pady=0)
        quick_frame.columnconfigure(0, weight=1)
        quick_frame.columnconfigure(1, weight=1)
        quick_frame.columnconfigure(2, weight=1)
        
        ttk.Button(quick_frame, text="📱 APK", command=self.install_apk, 
                  style='Primary.TButton').grid(row=0, column=0, sticky="ew", padx=(0, 1))
        ttk.Button(quick_frame, text="📂 文件", command=self.file_transfer, 
                  style='Primary.TButton').grid(row=0, column=1, sticky="ew", padx=1)
        ttk.Button(quick_frame, text="📷 截图", command=self.take_screenshot, 
                  style='Primary.TButton').grid(row=0, column=2, sticky="ew", padx=(1, 0))
        
        # 状态显示 - 移除上下间距
        status_frame = ttk.LabelFrame(control_card, text="运行状态", padding="4")
        status_frame.grid(row=3, column=0, sticky="ew", pady=0)
        status_frame.columnconfigure(0, weight=1)
        
        self.status_text = tk.Text(status_frame, height=2, font=('Segoe UI', 9), 
                                 bg='#f8f8f8', fg='#2d2d2d', relief='flat', borderwidth=1,
                                 wrap=tk.WORD)
        self.status_text.grid(row=0, column=0, sticky="ew")
        
        # 运行日志区域 - 移除上间距
        log_frame = ttk.LabelFrame(control_card, text="📋 运行日志", padding="6")
        log_frame.grid(row=4, column=0, sticky="nsew", pady=0)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 日志文本区域
        self.control_log_text = scrolledtext.ScrolledText(log_frame, height=5, font=('Consolas', 8),
                                                        bg='#1e1e1e', fg='#ffffff', relief='flat', borderwidth=1,
                                                        insertbackground='white')
        self.control_log_text.grid(row=0, column=0, sticky="nsew")
        
        # 日志控制按钮
        log_controls = ttk.Frame(log_frame)
        log_controls.grid(row=1, column=0, sticky="ew", pady=(3, 0))
        
        ttk.Button(log_controls, text="🗑️ 清空", command=self.clear_control_log, 
                  style='Primary.TButton', width=6).pack(side="left", padx=(0, 3))
        ttk.Button(log_controls, text="💾 保存", command=self.save_control_log, 
                  style='Primary.TButton', width=6).pack(side="left")
        
        # 插入初始状态
        self.update_status_display("🚀 系统已就绪，等待连接设备...")

    def update_status_display(self, message):
        """更新状态显示"""
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, message)

    # 设备管理相关方法
    def start_device_monitor(self):
        def monitor():
            while True:
                self.refresh_devices()
                time.sleep(2)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

    def refresh_devices(self):
        try:
            result = subprocess.run([self.adb_path, "devices"], 
                                  capture_output=True, text=True, timeout=10,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]
                self.devices = []
                
                for line in lines:
                    if line.strip() and '\tdevice' in line:
                        device_id = line.split('\t')[0]
                        self.devices.append(device_id)
                
                self.root.after(0, self.update_device_list)
                
        except Exception as e:
            self.log_message(f"❌ 刷新设备失败: {e}")

    def update_device_list(self):
        self.device_listbox.delete(0, tk.END)
        for device in self.devices:
            # 区分有线和无线设备
            if ':' in device:
                self.device_listbox.insert(tk.END, f"📶 {device} (无线)")
            else:
                self.device_listbox.insert(tk.END, f"🔌 {device} (有线)")
        
        if self.devices:
            self.status_indicator.config(text=f"🟢 发现 {len(self.devices)} 个设备")
            device_info = '\n'.join([f"• {device}" for device in self.devices])
            self.update_status_display(f"✅ 已发现 {len(self.devices)} 个设备\n{device_info}")
        else:
            self.status_indicator.config(text="🔴 未发现设备")
            self.update_status_display("⚠️ 未发现设备\n请检查：\n• USB调试是否开启\n• 设备是否正确连接\n• 驱动是否安装")

    def connect_device(self):
        selection = self.device_listbox.curselection()
        if selection:
            device_id = self.devices[selection[0]]
            self.selected_device.set(device_id)
            self.log_message(f"✅ 已选择设备: {device_id}")
            self.status_indicator.config(text=f"🟡 已选择: {device_id[:15]}...")
            self.update_status_display(f"✅ 设备已连接\n📱 {device_id}\n🎮 可以开始投屏或录制")
        else:
            messagebox.showwarning("警告", "请先选择一个设备")

    def disconnect_device(self):
        self.selected_device.set("")
        self.log_message("❌ 已断开设备连接")
        self.status_indicator.config(text="🔴 未连接")
        self.update_status_display("❌ 设备已断开连接")

    # 无线连接相关方法
    def enable_tcpip(self):
        """启用TCP/IP模式"""
        if not self.selected_device.get():
            messagebox.showwarning("警告", "请先选择一个有线连接的设备")
            return
        
        try:
            port = self.port_var.get()
            cmd = [self.adb_path, "-s", self.selected_device.get(), "tcpip", port]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                self.log_message(f"✅ TCP/IP模式已启用，端口: {port}")
                messagebox.showinfo("成功", f"TCP/IP模式已启用\n端口: {port}\n\n现在可以拔掉USB线，使用无线连接")
            else:
                self.log_message(f"❌ 启用TCP/IP失败: {result.stderr}")
                messagebox.showerror("错误", f"启用TCP/IP失败:\n{result.stderr}")
                
        except Exception as e:
            self.log_message(f"❌ 启用TCP/IP异常: {e}")
            messagebox.showerror("错误", f"启用TCP/IP异常: {e}")

    def connect_wireless(self):
        """无线连接设备"""
        ip = self.ip_var.get().strip()
        port = self.port_var.get().strip()
        
        if not ip:
            messagebox.showwarning("警告", "请输入设备IP地址")
            return
        
        # 验证IP格式
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(ip_pattern, ip):
            messagebox.showwarning("警告", "IP地址格式不正确")
            return
        
        try:
            target = f"{ip}:{port}"
            cmd = [self.adb_path, "connect", target]
            self.log_message(f"📶 尝试无线连接: {ip}:{port}...")
            
            # 增加超时时间以提高慢速网络下的成功率
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30, 
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # 安全地合并 stdout 和 stderr，避免 NoneType 错误
            stdout_str = result.stdout or ""
            stderr_str = result.stderr or ""
            output = stdout_str + stderr_str
            
            if result.returncode == 0 and "connected" in output.lower():
                self.log_message(f"✅ 无线连接成功: {target}")
                messagebox.showinfo("成功", f"无线连接成功!\n设备: {target}")
                # 刷新设备列表
                self.refresh_devices()
            else:
                error_msg = output
                self.log_message(f"❌ 无线连接失败: {error_msg}")
                messagebox.showerror("连接失败", f"无线连接失败:\n{error_msg}\n\n请检查:\n• 设备IP是否正确\n• 设备是否在同一网络\n• 是否已启用TCP/IP模式")
                
        except Exception as e:
            self.log_message(f"❌ 无线连接异常: {e}")
            messagebox.showerror("错误", f"无线连接异常: {e}")

    # 模式设置相关方法
    def on_mode_change(self):
        mode = self.mode_var.get()
        if mode == "game":
            self.set_game_mode()
        elif mode == "ultra":
            self.set_ultra_mode()
        elif mode == "video":
            self.set_video_mode()

    def set_game_mode(self):
        self.rotation_var.set("270")
        self.fps_var.set("60")
        self.bitrate_var.set("4M")
        self.resolution_var.set("1080")
        self.show_touches_var.set(False)
        self.stay_awake_var.set(True)
        self.no_audio_var.set(True)
        self.turn_screen_off_var.set(False)
        self.always_on_top_var.set(True)
        self.log_message("🎮 已切换到游戏模式")
        self.update_status_display("🎮 游戏模式\n• 270°旋转（横屏）\n• 60fps流畅体验\n• 4M高质量画面\n• 禁用音频减少延迟")

    def set_ultra_mode(self):
        self.rotation_var.set("270")
        self.fps_var.set("120")
        self.bitrate_var.set("8M")
        self.resolution_var.set("1440")
        self.show_touches_var.set(False)
        self.stay_awake_var.set(True)
        self.no_audio_var.set(True)
        self.turn_screen_off_var.set(False)
        self.always_on_top_var.set(True)
        self.log_message("⚡ 已切换到高性能游戏模式")
        self.update_status_display("⚡ 高性能模式\n• 270°旋转（横屏）\n• 120fps极致流畅\n• 8M超高画质\n• 专为竞技游戏优化")

    def set_video_mode(self):
        self.rotation_var.set("0")
        self.fps_var.set("30")
        self.bitrate_var.set("2M")
        self.resolution_var.set("1080")
        self.show_touches_var.set(False)
        self.stay_awake_var.set(True)
        self.no_audio_var.set(False)
        self.turn_screen_off_var.set(False)
        self.always_on_top_var.set(False)
        self.log_message("📺 已切换到视频模式")
        self.update_status_display("📺 视频模式\n• 正常方向\n• 30fps节能流畅\n• 2M平衡画质\n• 保留音频效果")

    def build_scrcpy_command(self):
        """构建scrcpy命令"""
        if not self.selected_device.get():
            raise ValueError("未选择设备")
        
        cmd = [self.scrcpy_path, "--serial", self.selected_device.get()]
        
        # 旋转设置
        if self.rotation_var.get() != "0":
            cmd.extend(["--orientation", self.rotation_var.get()])
        
        # 帧率设置
        if self.fps_var.get():
            cmd.extend(["--max-fps", self.fps_var.get()])
        
        # 比特率设置
        if self.bitrate_var.get():
            cmd.extend(["--video-bit-rate", self.bitrate_var.get()])
        
        # 分辨率设置 - 修复这里的问题
        resolution = self.resolution_var.get()
        if resolution and resolution != "原始":
            if resolution == "720":
                cmd.extend(["--max-size", "1280"])
            elif resolution == "1080":
                cmd.extend(["--max-size", "1920"])
            elif resolution == "1440":
                cmd.extend(["--max-size", "2560"])
            elif resolution == "2160":
                cmd.extend(["--max-size", "3840"])
        
        # 基础选项
        if self.show_touches_var.get():
            cmd.append("--show-touches")
        
        if self.stay_awake_var.get():
            cmd.append("--stay-awake")
        
        if self.no_audio_var.get():
            cmd.append("--no-audio")
        
        if self.turn_screen_off_var.get():
            cmd.append("--turn-screen-off")
        
        if self.always_on_top_var.get():
            cmd.append("--always-on-top")
        
        if self.fullscreen_var.get():
            cmd.append("--fullscreen")
        
        if self.no_control_var.get():
            cmd.append("--no-control")
        
        if self.disable_screensaver_var.get():
            cmd.append("--disable-screensaver")
        
        return cmd

    # 投屏和录制相关方法
    def start_mirroring(self):
        try:
            if self.scrcpy_process:
                messagebox.showwarning("警告", "投屏已在运行中")
                return
            
            cmd = self.build_scrcpy_command()
            self.log_message(f"🚀 启动投屏: {' '.join(cmd)}")
            
            self.scrcpy_process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
            self.status_indicator.config(text="🟢 投屏中")
            self.update_status_display("🎮 投屏已启动\n✅ 正在镜像设备屏幕\n🎯 可以开始操作设备")
            self.log_message("✅ 投屏已启动")
            
        except Exception as e:
            messagebox.showerror("错误", f"启动投屏失败: {e}")
            self.log_message(f"❌ 启动投屏失败: {e}")

    def stop_mirroring(self):
        if self.scrcpy_process:
            self.scrcpy_process.terminate()
            self.scrcpy_process = None
            self.status_indicator.config(text="🟡 已停止投屏")
            self.update_status_display("⏹️ 投屏已停止")
            self.log_message("⏹️ 投屏已停止")

    # 快捷操作相关方法
    def install_apk(self):
        """安装APK文件"""
        if not self.selected_device.get():
            messagebox.showwarning("警告", "请先选择设备")
            return
        
        apk_file = filedialog.askopenfilename(
            title="选择APK文件",
            filetypes=[("APK files", "*.apk"), ("All files", "*.*")]
        )
        
        if not apk_file:
            return
        
        try:
            self.log_message(f"📱 开始安装APK: {os.path.basename(apk_file)}")
            cmd = [self.adb_path, "-s", self.selected_device.get(), "install", apk_file]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0 and "Success" in result.stdout:
                self.log_message(f"✅ APK安装成功: {os.path.basename(apk_file)}")
                messagebox.showinfo("成功", f"APK安装成功!\n{os.path.basename(apk_file)}")
            else:
                error_msg = result.stdout + result.stderr
                self.log_message(f"❌ APK安装失败: {error_msg}")
                messagebox.showerror("失败", f"APK安装失败:\n{error_msg}")
                
        except Exception as e:
            self.log_message(f"❌ APK安装异常: {e}")
            messagebox.showerror("错误", f"APK安装异常: {e}")

    def file_transfer(self):
        """文件传输"""
        if not self.selected_device.get():
            messagebox.showwarning("警告", "请先选择设备")
            return
        
        # 创建文件传输对话框
        transfer_window = tk.Toplevel(self.root)
        transfer_window.title("📂 文件传输")
        transfer_window.geometry("500x300")
        transfer_window.transient(self.root)
        transfer_window.grab_set()
        
        # 上传文件
        upload_frame = ttk.LabelFrame(transfer_window, text="上传到设备", padding="10")
        upload_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(upload_frame, text="选择文件上传", 
                  command=lambda: self.upload_file()).pack(pady=5)
        
        # 下载文件
        download_frame = ttk.LabelFrame(transfer_window, text="从设备下载", padding="10")
        download_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(download_frame, text="设备路径:").pack(anchor="w")
        self.device_path_var = tk.StringVar(value="/sdcard/Download/")
        ttk.Entry(download_frame, textvariable=self.device_path_var, width=50).pack(fill="x", pady=2)
        
        ttk.Button(download_frame, text="下载文件", 
                  command=lambda: self.download_file()).pack(pady=5)

    def upload_file(self):
        """上传文件到设备"""
        file_path = filedialog.askopenfilename(title="选择要上传的文件")
        if not file_path:
            return
        
        try:
            self.log_message(f"📤 开始上传文件: {os.path.basename(file_path)}")
            cmd = [self.adb_path, "-s", self.selected_device.get(), "push", file_path, "/sdcard/Download/"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                self.log_message(f"✅ 文件上传成功: {os.path.basename(file_path)}")
                messagebox.showinfo("成功", f"文件上传成功!\n{os.path.basename(file_path)}")
            else:
                error_msg = result.stdout + result.stderr
                self.log_message(f"❌ 文件上传失败: {error_msg}")
                messagebox.showerror("失败", f"文件上传失败:\n{error_msg}")
                
        except Exception as e:
            self.log_message(f"❌ 文件上传异常: {e}")
            messagebox.showerror("错误", f"文件上传异常: {e}")

    def download_file(self):
        """从设备下载文件"""
        device_path = self.device_path_var.get().strip()
        if not device_path:
            messagebox.showwarning("警告", "请输入设备文件路径")
            return
        
        save_path = filedialog.asksaveasfilename(
            title="保存文件到",
            initialfile=os.path.basename(device_path)
        )
        
        if not save_path:
            return
        
        try:
            self.log_message(f"📥 开始下载文件: {device_path}")
            cmd = [self.adb_path, "-s", self.selected_device.get(), "pull", device_path, save_path]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                self.log_message(f"✅ 文件下载成功: {os.path.basename(save_path)}")
                messagebox.showinfo("成功", f"文件下载成功!\n{os.path.basename(save_path)}")
            else:
                error_msg = result.stdout + result.stderr
                self.log_message(f"❌ 文件下载失败: {error_msg}")
                messagebox.showerror("失败", f"文件下载失败:\n{error_msg}")
                
        except Exception as e:
            self.log_message(f"❌ 文件下载异常: {e}")
            messagebox.showerror("错误", f"文件下载异常: {e}")

    def take_screenshot(self):
        """截图"""
        if not self.selected_device.get():
            messagebox.showwarning("警告", "请先选择设备")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"screenshot_{timestamp}.png"
        
        save_path = filedialog.asksaveasfilename(
            title="保存截图到",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile=default_filename
        )
        
        if not save_path:
            return
        
        try:
            self.log_message("📷 正在截图...")
            # 先截图到设备
            device_screenshot = "/sdcard/screenshot_temp.png"
            cmd1 = [self.adb_path, "-s", self.selected_device.get(), "shell", "screencap", "-p", device_screenshot]
            
            result1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=10,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result1.returncode == 0:
                # 下载截图到电脑
                cmd2 = [self.adb_path, "-s", self.selected_device.get(), "pull", device_screenshot, save_path]
                result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=10,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
                
                if result2.returncode == 0:
                    # 删除设备上的临时文件
                    cmd3 = [self.adb_path, "-s", self.selected_device.get(), "shell", "rm", device_screenshot]
                    subprocess.run(cmd3, creationflags=subprocess.CREATE_NO_WINDOW)
                    
                    self.log_message(f"✅ 截图成功: {os.path.basename(save_path)}")
                    
                    if messagebox.askyesno("截图完成", 
                                         f"📷 截图完成!\n📁 文件: {os.path.basename(save_path)}\n\n是否打开文件所在目录？"):
                        try:
                            subprocess.run(['explorer', '/select,', save_path.replace('/', '\\')], 
                                         creationflags=subprocess.CREATE_NO_WINDOW)
                        except Exception as e:
                            self.log_message(f"❌ 打开目录失败: {e}")
                else:
                    error_msg = result2.stdout + result2.stderr
                    self.log_message(f"❌ 下载截图失败: {error_msg}")
                    messagebox.showerror("失败", f"下载截图失败:\n{error_msg}")
            else:
                error_msg = result1.stdout + result1.stderr
                self.log_message(f"❌ 截图失败: {error_msg}")
                messagebox.showerror("失败", f"截图失败:\n{error_msg}")
                
        except Exception as e:
            self.log_message(f"❌ 截图异常: {e}")
            messagebox.showerror("错误", f"截图异常: {e}")

    def quick_record(self):
        """快速录制 - 使用简化命令直接保存到用户目录"""
        try:
            if self.is_recording:
                messagebox.showwarning("警告", "录制已在运行中")
                return
            
            if not self.selected_device.get():
                messagebox.showwarning("警告", "请先选择设备")
                return
            
            # 快速录制设置
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            format_ext = self.record_format_var.get()
            filename = os.path.join(os.path.expanduser("~"), f"scrcpy_quick_{timestamp}.{format_ext}")
            
            # 构建简化的录制命令 (根据官方文档格式)
            if format_ext == "mp4":
                cmd = [self.scrcpy_path, "--serial", self.selected_device.get(), "--record", filename]
            else:
                cmd = [self.scrcpy_path, "--serial", self.selected_device.get(), "-r", filename]
            
            self.log_message(f"⚡ 快速录制: {os.path.basename(filename)}")
            self.log_message(f"📁 保存到: {filename}")
            self.log_message(f"🎬 格式: {format_ext.upper()}")
            self.log_message("💡 使用简化命令，快速启动")
            
            # 启动录制进程
            self.recording_process = subprocess.Popen(
                cmd, creationflags=subprocess.CREATE_NO_WINDOW,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            self.is_recording = True
            self.recording_file = filename
            self.status_indicator.config(text="⚡ 快速录制中")
            self.update_status_display(f"⚡ 快速录制模式\n📁 {os.path.basename(filename)}\n🎬 格式: {format_ext.upper()}\n💡 简化命令，快速启动")
            self.log_message(f"✅ 快速录制已开始")
            
            self.start_recording_monitor()
            
        except Exception as e:
            messagebox.showerror("错误", f"快速录制失败: {e}")
            self.log_message(f"❌ 快速录制失败: {e}")

    def start_recording_monitor(self):
        def monitor_recording():
            try:
                while self.is_recording and self.recording_process:
                    if self.recording_process.poll() is not None:
                        self.root.after(0, self.on_recording_finished)
                        break
                    time.sleep(1)
            except Exception as e:
                self.log_message(f"❌ 录制监控错误: {e}")
        
        thread = threading.Thread(target=monitor_recording, daemon=True)
        thread.start()

    def on_recording_finished(self):
        self.is_recording = False
        
        if hasattr(self, 'recording_file') and os.path.exists(self.recording_file):
            file_size = os.path.getsize(self.recording_file)
            if file_size > 0:
                size_mb = file_size / (1024 * 1024)
                self.log_message(f"✅ 录制完成，文件大小: {size_mb:.1f}MB")
                self.update_status_display(f"✅ 录制完成\n📁 {os.path.basename(self.recording_file)}\n📊 文件大小: {size_mb:.1f}MB")
                
                if messagebox.askyesno("录制完成", 
                                     f"🎉 录制完成！\n📁 文件: {os.path.basename(self.recording_file)}\n📊 大小: {size_mb:.1f}MB\n\n是否打开文件所在目录？"):
                    try:
                        subprocess.run(['explorer', '/select,', self.recording_file.replace('/', '\\')], 
                                     creationflags=subprocess.CREATE_NO_WINDOW)
                    except Exception as e:
                        self.log_message(f"❌ 打开目录失败: {e}")
            else:
                self.log_message("⚠️ 录制文件为空")
                messagebox.showwarning("警告", "录制文件为空，录制可能失败")
        else:
            self.log_message("⚠️ 录制文件不存在")

    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_queue.put(log_entry)

    def update_log(self):
        try:
            while True:
                log_entry = self.log_queue.get_nowait()
                # 更新控制面板的日志
                if hasattr(self, 'control_log_text'):
                    self.control_log_text.insert(tk.END, log_entry)
                    self.control_log_text.see(tk.END)
        except queue.Empty:
            pass
        
        self.root.after(100, self.update_log)

    def clear_control_log(self):
        if hasattr(self, 'control_log_text'):
            self.control_log_text.delete(1.0, tk.END)
            self.log_message("🗑️ 运行日志已清空")

    def save_control_log(self):
        if not hasattr(self, 'control_log_text'):
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="保存运行日志"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.control_log_text.get(1.0, tk.END))
                self.log_message(f"💾 运行日志已保存")
            except Exception as e:
                messagebox.showerror("错误", f"保存日志失败: {e}")

    def on_closing(self):
        if self.scrcpy_process:
            self.scrcpy_process.terminate()
        if self.recording_process:
            self.recording_process.terminate()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = ModernScrcpyGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main() 