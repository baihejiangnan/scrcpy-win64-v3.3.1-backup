#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代化Scrcpy GUI正式版打包脚本
基于调试版改进，使用windowed模式
"""

import os
import subprocess
import sys
import shutil
import glob

def install_pyinstaller():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller 安装成功")
        return True
    except Exception as e:
        print(f"❌ PyInstaller 安装失败: {e}")
        return False

def build_exe():
    try:
        # 检查必要文件
        required_files = ["scrcpy_gui_modern.py", "scrcpy.exe", "adb.exe"]
        missing_files = [f for f in required_files if not os.path.exists(f)]
        
        if missing_files:
            print(f"❌ 错误: 缺少必要文件: {', '.join(missing_files)}")
            return False
        
        print("✅ 所有必要文件都存在")
        
        # 构建PyInstaller命令 - 正式版本
        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",  # 使用windowed模式，不显示控制台
            "--name=Scrcpy现代化控制中心",
            "--add-data=scrcpy.exe;.",
            "--add-data=adb.exe;.",
            "--add-data=scrcpy-server;.",
            "--hidden-import=tkinter",
            "--hidden-import=tkinter.ttk",
            "--hidden-import=tkinter.filedialog",
            "--hidden-import=tkinter.messagebox",
            "--hidden-import=tkinter.scrolledtext",
            "--hidden-import=queue",
            "--hidden-import=threading",
            "--hidden-import=subprocess",
            "--hidden-import=datetime",
            "scrcpy_gui_modern.py"
        ]
        
        # 添加图标（如果存在）
        if os.path.exists("icon.png"):
            cmd.insert(-2, "--icon=icon.png")
        
        # 添加所有dll文件
        dll_files = glob.glob("*.dll")
        for dll in dll_files:
            cmd.insert(-2, f"--add-data={dll};.")
            print(f"📋 添加DLL文件: {dll}")
        
        print("🚀 开始构建现代化GUI正式版exe文件...")
        print(f"📝 执行命令: {' '.join(cmd[:8])}...")
        print()
        
        subprocess.check_call(cmd)
        
        print("✅ 构建完成！exe文件位置: dist/Scrcpy现代化控制中心.exe")
        
        # 复制依赖文件到dist目录
        files_to_copy = [
            "scrcpy.exe", "adb.exe", "scrcpy-server",
            "AdbWinApi.dll", "AdbWinUsbApi.dll", "avcodec-61.dll",
            "avformat-61.dll", "avutil-59.dll", "libusb-1.0.dll",
            "SDL2.dll", "swresample-5.dll"
        ]
        
        # 添加图标文件
        if os.path.exists("icon.png"):
            files_to_copy.append("icon.png")
        
        print("\n📋 复制依赖文件到dist目录...")
        copied_count = 0
        for file in files_to_copy:
            if os.path.exists(file):
                try:
                    shutil.copy2(file, "dist/")
                    print(f"✅ 已复制: {file}")
                    copied_count += 1
                except Exception as e:
                    print(f"❌ 复制文件 {file} 失败: {e}")
            else:
                print(f"⚠️ 警告: 文件 {file} 不存在，跳过")
        
        print(f"\n📊 成功复制 {copied_count} 个依赖文件")
        
        # 创建详细的使用说明
        readme_content = """🎮 Scrcpy 现代化投屏控制中心 v2.0 - 正式版

📋 使用说明：
1. 确保手机已开启USB调试
2. 用USB线连接手机到电脑
3. 双击运行"Scrcpy现代化控制中心.exe"
4. 在界面中选择设备并开始投屏

📁 文件说明：
• Scrcpy现代化控制中心.exe - 主程序（正式版）
• scrcpy.exe - Scrcpy核心程序
• adb.exe - Android调试桥
• scrcpy-server - 服务端程序
• *.dll - 必需的动态链接库

✨ 正式版特性：
• 现代化美观界面设计
• 卡片式布局更清晰
• 更好的视觉效果
• 优化的用户体验
• 无控制台窗口，界面简洁

🔧 故障排除：
如果程序无法启动：
1. 确保所有dll文件都在同一目录
2. 检查Windows Defender是否误报
3. 尝试以管理员身份运行
4. 确保Visual C++ Redistributable已安装
5. 如需查看错误信息，请使用调试版

📞 技术支持：
如遇问题请检查：
- USB调试是否开启
- 设备驱动是否正常
- 防火墙是否阻止程序运行
- 杀毒软件是否误报

💡 如果遇到问题，建议先运行调试版查看详细错误信息

版本：v2.0 Modern Edition Release
"""
        
        with open("dist/使用说明.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        # 创建启动批处理文件
        start_bat_content = """@echo off
chcp 65001 >nul
title Scrcpy现代化控制中心

echo.
echo 🎮 启动Scrcpy现代化控制中心...
echo ✨ 现代化界面设计，更美观的投屏体验
echo.

start "" "Scrcpy现代化控制中心.exe"

echo ✅ 程序已启动
timeout /t 2 /nobreak >nul
"""
        
        with open("dist/启动现代化GUI.bat", "w", encoding="utf-8") as f:
            f.write(start_bat_content)
        
        # 创建快速启动脚本
        quick_start_content = """@echo off
"Scrcpy现代化控制中心.exe"
"""
        
        with open("dist/快速启动.bat", "w", encoding="utf-8") as f:
            f.write(quick_start_content)
        
        print("📝 已创建使用说明和启动脚本")
        
        # 显示dist目录内容
        print("\n📂 dist目录内容:")
        total_size = 0
        for item in sorted(os.listdir("dist")):
            item_path = os.path.join("dist", item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path) / (1024 * 1024)
                total_size += size
                print(f"   📄 {item} ({size:.1f} MB)")
        
        print(f"\n📊 总大小: {total_size:.1f} MB")
        print("\n🎉 正式版打包完成！")
        print("📁 所有文件都在 dist/ 目录中")
        print("🚀 双击 dist/Scrcpy现代化控制中心.exe 即可启动")
        print("💡 如遇问题，请使用调试版查看详细错误信息")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: PyInstaller 执行出错 (返回码: {e.returncode})")
        return False
    except Exception as e:
        print(f"❌ 构建过程中出错: {e}")
        return False

def main():
    print("=" * 60)
    print("🔧 Scrcpy 现代化GUI 正式版打包工具")
    print("=" * 60)
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ 错误: 需要Python 3.7或更高版本")
        return
    
    print(f"🐍 Python版本: {sys.version}")
    
    # 检查或安装PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller已安装")
    except ImportError:
        print("⚠️ PyInstaller未安装，正在安装...")
        if not install_pyinstaller():
            input("按回车键退出...")
            return
    
    # 清理旧的构建文件
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️ 清理目录: {dir_name}")
    
    if build_exe():
        print("\n✅ 正式版打包成功！")
        print("📦 可执行文件已生成在 dist/ 目录中")
        print("🎮 双击exe文件即可启动现代化GUI")
        print("\n💡 正式版特点:")
        print("   • 无控制台窗口，界面简洁")
        print("   • 现代化设计，用户体验更佳")
        print("   • 包含所有必要依赖文件")
        print("   • 可独立运行，无需Python环境")
    else:
        print("\n❌ 打包失败！")
        print("请检查错误信息并重试")
    
    # 清理spec文件
    spec_files = glob.glob("*.spec")
    for spec_file in spec_files:
        os.remove(spec_file)
        print(f"🗑️ 清理文件: {spec_file}")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main() 