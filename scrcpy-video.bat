@echo off
echo 启动视频模式投屏...
echo 参数：正常方向，平衡性能，适合刷视频
scrcpy.exe --max-fps=30 --bit-rate=2M --max-size=1280 --stay-awake
pause 