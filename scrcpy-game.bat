@echo off
echo 启动游戏模式投屏...
echo 参数：270度旋转，高帧率，低延迟，适合游戏
scrcpy.exe --orientation=270 --max-fps=60 --video-bit-rate=4M --max-size=1920 --stay-awake --no-audio --disable-screensaver
pause 