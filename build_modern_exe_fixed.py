#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
构建现代化Scrcpy GUI的可执行文件 - 修复版本
支持Python 3.8+
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_requirements():
    """检查必要的依赖"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller 版本: {PyInstaller.__version__}")
    except ImportError:
        print("❌ PyInstaller 未安装")
        print("请运行: pip install pyinstaller")
        return False
    
    # 检查源文件
    if not os.path.exists("scrcpy_gui_modern.py"):
        print("❌ 找不到 scrcpy_gui_modern.py")
        return False
    
    print("✅ 所有依赖检查通过")
    return True

def clean_build():
    """清理之前的构建文件"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️ 已清理目录: {dir_name}")
    
    import glob
    for pattern in files_to_clean:
        for file in glob.glob(pattern):
            os.remove(file)
            print(f"🗑️ 已清理文件: {file}")

def build_exe():
    """构建可执行文件"""
    print("🚀 开始构建现代化Scrcpy GUI v2.1...")
    
    # PyInstaller 命令
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个文件
        "--windowed",                   # 无控制台窗口
        "--name=ScrcpyModernGUI_v2.1",  # 可执行文件名
        "--icon=icon.png",              # 图标文件（如果存在）
        "--add-data=adb.exe;.",         # 包含adb.exe
        "--add-data=AdbWinApi.dll;.",   # 包含ADB相关DLL
        "--add-data=AdbWinUsbApi.dll;.",
        "--add-data=scrcpy.exe;.",      # 包含scrcpy.exe
        "--add-data=scrcpy-server;.",   # 包含scrcpy-server
        "--add-data=avcodec-61.dll;.",  # 包含所有必要的DLL
        "--add-data=avformat-61.dll;.",
        "--add-data=avutil-59.dll;.",
        "--add-data=libusb-1.0.dll;.",
        "--add-data=SDL2.dll;.",
        "--add-data=swresample-5.dll;.",
        "--hidden-import=tkinter",      # 确保tkinter被包含
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.scrolledtext",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=subprocess",
        "--hidden-import=threading",
        "--hidden-import=queue",
        "--hidden-import=re",
        "--hidden-import=datetime",
        "--clean",                      # 清理临时文件
        "scrcpy_gui_modern.py"          # 源文件
    ]
    
    # 如果图标文件不存在，移除图标参数
    if not os.path.exists("icon.png"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
        print("⚠️ 图标文件不存在，跳过图标设置")
    
    try:
        print("📦 正在打包...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 打包成功!")
        
        # 检查生成的文件
        exe_path = "dist/ScrcpyModernGUI_v2.1.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"📁 生成的文件: {exe_path}")
            print(f"📊 文件大小: {size_mb:.1f} MB")
            
            # 复制到当前目录
            shutil.copy2(exe_path, "ScrcpyModernGUI_v2.1.exe")
            print("✅ 已复制到当前目录: ScrcpyModernGUI_v2.1.exe")
            
            return True
        else:
            print("❌ 未找到生成的exe文件")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def create_startup_script():
    """创建启动脚本"""
    script_content = '''@echo off
echo 🎮 启动Scrcpy现代化控制中心 v2.1...
echo.
echo 💡 使用说明：
echo 1. 确保手机已开启USB调试
echo 2. 使用USB线连接手机到电脑
echo 3. 或者使用无线连接功能
echo 4. 选择投屏模式开始使用
echo.
pause
ScrcpyModernGUI_v2.1.exe
'''
    
    with open("启动现代化GUI_v2.1.bat", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print("✅ 已创建启动脚本: 启动现代化GUI_v2.1.bat")

def create_readme():
    """创建使用说明"""
    readme_content = """# Scrcpy 现代化控制中心 v2.1

## 🎮 功能特色

### 📱 设备管理
- 自动检测USB连接的设备
- 支持多设备同时管理
- 区分有线和无线设备显示

### 📶 无线连接
- 一键启用TCP/IP模式
- 支持IP地址无线连接
- 自动验证连接状态

### ⚙️ 投屏模式
- **🎮 游戏模式**: 270°横屏，60fps，4M码率，专为游戏优化
- **⚡ 高性能模式**: 120fps极致流畅，8M超高画质
- **📺 视频模式**: 30fps节能，2M平衡画质，保留音频
- **🔧 自定义模式**: 完全自定义所有参数

### 🎯 高级功能
- **分辨率控制**: 原始/720p/1080p/1440p/4K选择
- **显示选项**: 显示触摸、窗口置顶、全屏显示
- **设备控制**: 防止休眠、关闭屏幕、禁用控制
- **音频选项**: 音频开关、屏保控制

### 🎬 录制功能
- 投屏+录制同时进行
- 仅录制模式（后台录制）
- 支持MP4/MKV/AVI格式
- 录制完成自动提示

### 🚀 快捷操作
- **📱 APK安装**: 拖拽或选择APK文件安装
- **📂 文件传输**: 双向文件传输功能
- **📷 设备截图**: 一键截图保存

## 🔧 使用方法

### 有线连接
1. 开启手机USB调试模式
2. 使用USB线连接手机
3. 在设备列表中选择设备
4. 点击"连接"按钮
5. 选择投屏模式开始使用

### 无线连接
1. 先用USB线连接设备
2. 在设备列表中选择设备
3. 点击"启用TCP"按钮
4. 输入手机IP地址
5. 点击"无线连接"
6. 拔掉USB线，享受无线投屏

### 参数说明
- **旋转**: 0°/90°/180°/270°屏幕旋转
- **帧率**: 15-120fps，影响流畅度
- **比特率**: 1M-12M，影响画质和网络占用
- **分辨率**: 限制最大分辨率，降低延迟

## 📋 系统要求
- Windows 10/11
- USB调试已开启的Android设备
- 同一网络环境（无线连接时）

## 🆘 故障排除

### 设备连接问题
- 确认USB调试已开启
- 检查USB驱动是否正确安装
- 尝试更换USB线或端口

### 无线连接问题
- 确保设备在同一WiFi网络
- 检查IP地址是否正确
- 确认已先启用TCP/IP模式

### 投屏质量问题
- 降低分辨率和帧率
- 减少比特率设置
- 关闭不必要的高级选项

## 📝 更新日志

### v2.1 新增功能
- ✨ 无线连接支持
- ✨ 多设备管理
- ✨ APK安装功能
- ✨ 文件传输功能
- ✨ 设备截图功能
- ✨ 更多分辨率选项
- ✨ 增强的高级选项
- 🐛 修复分辨率设置问题
- 🎨 优化界面布局

---
💡 **提示**: 首次使用建议先阅读此说明文档
"""
    
    with open("现代化界面使用说明_v2.1.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ 已创建使用说明: 现代化界面使用说明_v2.1.md")

def main():
    """主函数"""
    print("🎮 Scrcpy 现代化GUI v2.1 构建工具")
    print("=" * 50)
    
    # 检查依赖
    if not check_requirements():
        return False
    
    # 清理之前的构建
    clean_build()
    
    # 构建exe
    if not build_exe():
        return False
    
    # 创建启动脚本和说明文档
    create_startup_script()
    create_readme()
    
    print("\n🎉 构建完成!")
    print("📁 生成的文件:")
    print("  - ScrcpyModernGUI_v2.1.exe (主程序)")
    print("  - 启动现代化GUI_v2.1.bat (启动脚本)")
    print("  - 现代化界面使用说明_v2.1.md (使用说明)")
    print("\n💡 提示: 双击启动脚本或直接运行exe文件")
    
    return True

if __name__ == "__main__":
    success = main()
    input("\n按回车键退出...")
    sys.exit(0 if success else 1) 