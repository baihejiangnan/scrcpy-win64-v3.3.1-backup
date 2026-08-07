#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代化Scrcpy GUI打包脚本
将Python程序打包成独立的exe文件
"""

import os
import sys
import subprocess
import shutil

def main():
    print("🔧 Scrcpy 现代化GUI打包工具")
    print("=" * 50)
    
    # 检查PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller已安装")
    except ImportError:
        print("❌ PyInstaller未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller安装完成")
    
    # 检查源文件
    source_file = "scrcpy_gui_modern.py"
    if not os.path.exists(source_file):
        print(f"❌ 找不到源文件: {source_file}")
        return
    
    print(f"✅ 找到源文件: {source_file}")
    
    # 清理旧的构建文件
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️ 清理目录: {dir_name}")
    
    # 构建PyInstaller命令
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个exe文件
        "--windowed",                   # 不显示命令行窗口
        "--name=Scrcpy现代化控制中心",    # 设置exe文件名
        "--icon=NONE",                  # 暂时不设置图标
        "--clean",                      # 清理临时文件
        "--distpath=dist",              # 输出目录
        "--workpath=build",             # 工作目录
        source_file
    ]
    
    print("🚀 开始打包...")
    print(f"📝 执行命令: {' '.join(cmd)}")
    print()
    
    # 执行打包
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 打包成功！")
        print()
        
        # 检查输出文件
        exe_path = os.path.join("dist", "Scrcpy现代化控制中心.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"📁 输出文件: {exe_path}")
            print(f"📊 文件大小: {file_size:.1f} MB")
            print()
            
            # 创建启动说明
            readme_content = """🎮 Scrcpy 现代化投屏控制中心 v2.0

📋 使用说明：
1. 确保手机已开启USB调试
2. 用USB线连接手机到电脑
3. 运行"Scrcpy现代化控制中心.exe"
4. 在界面中选择设备并开始投屏

✨ 新功能特性：
• 现代化美观界面设计
• 卡片式布局更清晰
• 更好的视觉效果
• 优化的用户体验

📞 技术支持：
如遇问题请检查：
- USB调试是否开启
- 设备驱动是否正常
- 防火墙是否阻止程序运行

版本：v2.0 Modern Edition
"""
            
            with open("dist/使用说明.txt", "w", encoding="utf-8") as f:
                f.write(readme_content)
            
            print("📝 已创建使用说明文件")
            print()
            print("🎉 打包完成！可以在dist目录中找到exe文件")
            
        else:
            print("❌ 未找到输出文件")
    else:
        print("❌ 打包失败！")
        print("错误信息:")
        print(result.stderr)
    
    # 清理spec文件
    spec_file = "Scrcpy现代化控制中心.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
        print(f"🗑️ 清理文件: {spec_file}")

if __name__ == "__main__":
    main()
    input("\n按回车键退出...") 