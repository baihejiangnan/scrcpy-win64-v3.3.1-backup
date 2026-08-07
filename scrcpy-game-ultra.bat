@echo off
echo 启动超高性能游戏模式投屏...
echo 参数：270度旋转，最高画质，最低延迟，适合竞技游戏
scrcpy.exe --orientation=270 --max-fps=120 --video-bit-rate=8M --max-size=2560 --stay-awake --no-audio --disable-screensaver --render-driver=direct3d --v4l2-buffer=2
pause 