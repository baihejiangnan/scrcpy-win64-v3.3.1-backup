@echo off
chcp 65001 >nul
title Scrcpy现代化控制中心
echo.
echo ==========================================
echo    🎮 Scrcpy 现代化投屏控制中心 v2.0
echo ==========================================
echo.
echo 正在启动现代化界面...
echo.

python scrcpy_gui_modern.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ 启动失败，请检查Python环境是否正确安装
    echo.
    pause
) 