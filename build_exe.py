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
        
        # 构建PyInstaller命令
        cmd = [
            "pyinstaller",
            "--onefile",
            "--console",
            "--name=ScrcpyGUI",
            "--add-data=scrcpy.exe;.",
            "--add-data=adb.exe;.",
            "--add-data=scrcpy-server;.",
            "scrcpy_gui.py"
        ]
        
        # 添加图标（如果存在）
        if os.path.exists("icon.png"):
            cmd.insert(-1, "--icon=icon.png")
        
        # 添加所有dll文件
        dll_files = glob.glob("*.dll")
        for dll in dll_files:
            cmd.insert(-1, f"--add-data={dll};.")
        
        print("开始构建exe文件...")
        print(f"执行命令: {' '.join(cmd)}")
        
        subprocess.check_call(cmd)
        
        print("构建完成！exe文件位置: dist/ScrcpyGUI.exe")
        
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
        
        # 创建使用说明
        create_usage_info()
        
        print("\n🎉 打包完成！")
        print("📁 所有文件都在 dist/ 目录中")
        print("🚀 您可以将整个 dist/ 目录复制到其他电脑上使用")
        print("💡 直接双击 dist/ScrcpyGUI.exe 即可运行")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"构建失败: PyInstaller 执行出错 (返回码: {e.returncode})")
        return False
    except Exception as e:
        print(f"构建过程中出错: {e}")
        return False

def create_usage_info():
    """在dist目录创建使用说明"""
    try:
        usage_text = """Scrcpy GUI 使用说明
===================

1. 双击 ScrcpyGUI.exe 启动程序
2. 连接Android设备并启用USB调试
3. 在程序中选择设备和模式
4. 点击"开始投屏"即可使用

注意事项：
- 确保Android设备已启用开发者选项和USB调试
- 首次连接需要在设备上授权USB调试
- 所有文件都需要在同一目录下

技术支持：
- 查看 README.md 获取详细说明
- 访问 https://github.com/Genymobile/scrcpy 获取官方支持
"""
        
        with open("dist/使用说明.txt", "w", encoding="utf-8") as f:
            f.write(usage_text)
        print("已创建使用说明文件: dist/使用说明.txt")
        
    except Exception as e:
        print(f"创建使用说明失败: {e}")

def main():
    print("=" * 50)
    print("Scrcpy GUI 打包工具")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        return
    
    print(f"Python版本: {sys.version}")
    
    # 检查当前目录
    current_files = os.listdir(".")
    print(f"当前目录文件数: {len(current_files)}")
    
    if not install_pyinstaller():
        input("按回车键退出...")
        return
    
    if build_exe():
        print("\n✅ 打包成功！")
        print("📦 可执行文件已生成在 dist/ 目录中")
    else:
        print("\n❌ 打包失败！")
        print("请检查错误信息并重试")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main() 