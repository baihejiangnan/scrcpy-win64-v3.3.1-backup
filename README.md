# Scrcpy 控制中心

这是一个 Windows 上的 Android 投屏控制台。当前使用的打包程序是根目录的 `Scrcpy控制中心.exe`，对应源码为 `web-ui/launcher.py`、`web-ui/server.py` 和 `web-ui/static/`。

## 日常使用

1. 在手机上开启开发者选项和 USB 调试。
2. 用数据线连接电脑，在手机上允许 USB 调试授权。
3. 双击 `Scrcpy控制中心.exe`，在界面中选择设备并开始投屏。

窗口默认以紧凑尺寸打开，顶部有三个页面：**常用设置**集中设备、开始投屏和投屏设置；**运行日志**用于查看、保存和清空日志；**录制与文件**集中录制、截图、文件操作和产出文件。无线连接收在常用设置页的可展开区域，投屏窗口快捷键参考收在录制与文件页底部。

`Scrcpy控制中心.exe` 与根目录中的 `adb.exe`、`scrcpy.exe`、`scrcpy-server` 和 DLL 共同构成可运行版本；复制到其他位置时，应将这些文件放在同一目录。运行时生成的下载文件和壁纸放在 `web-ui-data/`，不要把它当作构建缓存清理。

## 项目文件

| 路径 | 用途 |
| --- | --- |
| `Scrcpy控制中心.exe`、根目录的 scrcpy/adb 文件 | 当前使用的程序及运行依赖 |
| `web-ui/launcher.py`、`web-ui/server.py`、`web-ui/static/` | 当前版本源码 |
| `web-ui/wallpapers/` | 打包时使用的默认壁纸 |
| `web-ui-data/` | exe 运行时的下载文件与壁纸 |
| `build_exe.py`、`requirements.txt`、`icon.png` | 重新打包所需文件 |

## 从源码运行

在项目根目录执行：

```powershell
python -m pip install -r requirements.txt
python web-ui/launcher.py
```

源码模式的下载目录为 `web-ui/downloads/`；打包程序使用 `web-ui-data/downloads/`。不需要原生窗口时，可运行 `python web-ui/server.py --port 7100`，再访问 `http://127.0.0.1:7100/`。

## 检查与打包

```powershell
python -m unittest discover -s web-ui -p test_server.py
python build_exe.py
```

打包结果位于 `dist/`，其中包含 exe 和外部运行依赖。此命令不会替换根目录正在使用的 exe；确认新版本可用后再手动替换。
