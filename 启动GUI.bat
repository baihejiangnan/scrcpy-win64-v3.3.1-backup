@echo off
echo 启动 Scrcpy 图形化控制中心...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    pause
    exit /b 1
)

REM 检查必要文件
if not exist "scrcpy_gui.py" (
    echo 错误: 未找到 scrcpy_gui.py 文件
    pause
    exit /b 1
)

if not exist "scrcpy.exe" (
    echo 错误: 未找到 scrcpy.exe 文件
    pause
    exit /b 1
)

echo 正在启动GUI程序...
python scrcpy_gui.py

if errorlevel 1 (
    echo.
    echo 程序运行出错，请检查错误信息
    pause
) 