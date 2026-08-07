#!/usr/bin/env python3
import os
import subprocess
import sys
import shutil
import glob

def install_pyinstaller():
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller 安装成功")
        return True
    except Exception as e:
        print(f"PyInstaller 安装失败: {e}")
        return False

def build_exe():
    try:
        # 检查必要文件
        required_files = ["scrcpy_gui.py", "scrcpy.exe", "adb.exe"]
        missing_files = [f for f in required_files if not os.path.exists(f)]
        
        if missing_files:
            print(f"错误: 缺少必要文件: {', '.join(missing_files)}")
            return False
        
        # 构建PyInstaller命令 - 调试版本
        cmd = [
            "pyinstaller",
            "--onefile",
            "--console",  # 使用console模式便于调试
            "--name=ScrcpyGUI_Debug",
            "--add-data=scrcpy.exe;.",
            "--add-data=adb.exe;.",
            "--add-data=scrcpy-server;.",
            "--debug=all",  # 启用所有调试信息
            "scrcpy_gui.py"
        ]
        
        # 添加图标（如果存在）
        if os.path.exists("icon.png"):
            cmd.insert(-2, "--icon=icon.png")
        
        # 添加所有dll文件
        dll_files = glob.glob("*.dll")
        for dll in dll_files:
            cmd.insert(-2, f"--add-data={dll};.")
        
        print("开始构建调试版exe文件...")
        print(f"执行命令: {' '.join(cmd)}")
        
        subprocess.check_call(cmd)
        
        print("构建完成！exe文件位置: dist/ScrcpyGUI_Debug.exe")
        
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
        
        print("\n复制依赖文件到dist目录...")
        for file in files_to_copy:
            if os.path.exists(file):
                try:
                    shutil.copy2(file, "dist/")
                    print(f"已复制: {file}")
                except Exception as e:
                    print(f"复制文件 {file} 失败: {e}")
            else:
                print(f"警告: 文件 {file} 不存在，跳过")
        
        print("\n🎉 调试版打包完成！")
        print("📁 所有文件都在 dist/ 目录中")
        print("🚀 运行 dist/ScrcpyGUI_Debug.exe 查看调试信息")
        print("💡 如果有错误，控制台会显示详细信息")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"构建失败: PyInstaller 执行出错 (返回码: {e.returncode})")
        return False
    except Exception as e:
        print(f"构建过程中出错: {e}")
        return False

def main():
    print("=" * 50)
    print("Scrcpy GUI 调试版打包工具")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        return
    
    print(f"Python版本: {sys.version}")
    
    if not install_pyinstaller():
        input("按回车键退出...")
        return
    
    if build_exe():
        print("\n✅ 调试版打包成功！")
        print("📦 可执行文件已生成在 dist/ 目录中")
        print("🔍 运行后可以看到详细的错误信息")
    else:
        print("\n❌ 打包失败！")
        print("请检查错误信息并重试")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main() 