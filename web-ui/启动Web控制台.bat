@echo off
chcp 65001 >nul
title Scrcpy Web 控制中心
echo.
echo ==========================================
echo    Scrcpy Web 控制中心 v3.0
echo ==========================================
echo.
echo 正在启动 Web 控制台...
echo 启动后请在浏览器打开: http://localhost:7100/
echo.

cd /d "%~dp0"
start "" "http://localhost:7100/"
python server.py --port 7100

if %ERRORLEVEL% neq 0 (
    echo.
    echo 启动失败，请检查 Python 环境是否正确安装
    echo.
    pause
)
