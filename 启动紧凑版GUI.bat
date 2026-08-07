@echo off
chcp 65001 >nul
title 启动Scrcpy现代化控制中心 v2.1 - 紧凑版

echo.
echo 🎮 Scrcpy 现代化控制中心 v2.1 - 紧凑版
echo ===============================================
echo.
echo 💡 界面优化说明：
echo • 窗口尺寸：1000x750（更紧凑）
echo • 减少了内边距和间距
echo • 优化了按钮和控件大小
echo • 保持所有功能完整
echo.
echo 🚀 正在启动GUI...
echo.

python scrcpy_gui_modern.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 启动失败！
    echo 💡 可能的解决方案：
    echo 1. 确保Python已安装
    echo 2. 确保tkinter模块可用
    echo 3. 检查文件是否完整
    echo.
    pause
) else (
    echo.
    echo 👋 程序已关闭，感谢使用！
)

pause 