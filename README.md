# Scrcpy 投屏工具使用指南

## 简介
Scrcpy 是一个开源的 Android 投屏工具，可以将 Android 设备的屏幕镜像到电脑上，支持鼠标和键盘操作。

**版本**: v3.3.1  
**系统**: Windows 64位

## 🎮 图形化控制软件（推荐）

我们提供了两个版本的图形化控制软件，让您可以通过可视化界面轻松控制scrcpy。

### ✨ 现代化GUI v2.0（推荐）

**全新设计的现代化界面** - `scrcpy_gui_modern.py`

#### 🎨 界面特色
- **现代化扁平设计** - 采用简洁的扁平化设计风格
- **卡片式布局** - 信息层次清晰，操作区域分组明确
- **统一色彩方案** - 使用微软Fluent Design色彩体系
- **优雅字体** - 统一使用Segoe UI字体，提升视觉效果
- **响应式布局** - 窗口大小自适应，支持高DPI显示

#### 🚀 现代化GUI启动方式
```bash
# 方法一：批处理启动（推荐）
启动现代化GUI.bat

# 方法二：直接运行
python scrcpy_gui_modern.py

# 方法三：打包成exe
python build_modern_exe.py
```

### 🔧 经典GUI v1.0

**功能完整的经典版本** - `scrcpy_gui.py`

#### 启动方式
- **双击 `启动GUI.bat`** - 启动经典图形化控制界面
- **运行 `python scrcpy_gui.py`** - 直接运行Python程序

### 🌟 GUI功能特性（两版本通用）
- 📱 **设备管理** - 自动检测和连接Android设备
- 🎯 **模式选择** - 游戏模式、高性能模式、视频模式、自定义模式
- 🎬 **录制功能** - 支持投屏录制，可选择保存位置
- ⚙️ **参数配置** - 可视化配置所有scrcpy参数
- 📊 **实时日志** - 显示运行状态和错误信息
- 🎨 **人性化界面** - 简洁直观的操作界面

### GUI使用步骤
1. **启动程序** - 双击对应的启动文件
2. **连接设备** - 在设备管理区域选择并连接设备
3. **选择模式** - 选择预设模式或自定义参数
4. **开始投屏** - 点击"开始投屏"按钮
5. **录制功能** - 可选择开始/停止录制

### 打包成exe
```bash
# 经典版本打包
python build_exe.py

# 现代化版本打包
python build_modern_exe.py
```
打包后的exe文件将保存在 `dist/` 目录中。

## 快速开始

### 1. 准备工作
- 确保 Android 设备已启用**开发者选项**
- 启用**USB调试**
- 用 USB 线连接设备到电脑
- 在设备上允许 USB 调试

### 2. 启动方式

#### 基础启动
- **`scrcpy-console.bat`** - 控制台模式启动
- **`scrcpy-noconsole.vbs`** - 无控制台模式启动

#### 专用模式启动
- **`scrcpy-game.bat`** - 游戏模式（270°旋转，60fps）
- **`scrcpy-video.bat`** - 视频模式（正常方向，30fps）
- **`scrcpy-game-ultra.bat`** - 超高性能游戏模式（270°旋转，120fps）

## 批处理文件详解

### 游戏模式 (`scrcpy-game.bat`)
```
参数说明：
--orientation=270     # 逆时针旋转90度，适合横屏游戏
--max-fps=60         # 60帧率，流畅游戏体验
--video-bit-rate=4M  # 4M比特率，高质量画面
--max-size=1920      # 最大宽度1920像素
--stay-awake         # 保持设备唤醒
--no-audio           # 禁用音频，减少延迟
--disable-screensaver # 禁用屏保
```

### 视频模式 (`scrcpy-video.bat`)
```
参数说明：
--max-fps=30         # 30帧率，适合视频观看
--video-bit-rate=2M  # 2M比特率，平衡画质和性能
--max-size=1280      # 最大宽度1280像素
--stay-awake         # 保持设备唤醒
```

### 超高性能游戏模式 (`scrcpy-game-ultra.bat`)
```
参数说明：
--orientation=270     # 逆时针旋转90度
--max-fps=120        # 120帧率，极低延迟
--video-bit-rate=8M  # 8M比特率，最高画质
--max-size=2560      # 支持4K显示器
--stay-awake         # 保持设备唤醒
--no-audio           # 禁用音频
--disable-screensaver # 禁用屏保
--render-driver=direct3d # Direct3D渲染
--v4l2-buffer=2      # 优化缓冲区
```

## 常用参数说明

### 显示参数
- `--orientation=270` - 旋转270度（逆时针90度）
- `--orientation=90` - 旋转90度（顺时针90度）
- `--orientation=180` - 旋转180度
- `--max-size=1920` - 限制最大宽度
- `--max-fps=60` - 限制最大帧率
- `--show-touches` - 显示触摸点

### 性能参数
- `--video-bit-rate=4M` - 设置视频比特率（影响画质）
- `--no-audio` - 禁用音频传输
- `--stay-awake` - 保持设备唤醒
- `--disable-screensaver` - 禁用屏保

### 录制参数
- `--record=file.mp4` - 录制屏幕到文件
- `--record-format=mp4` - 设置录制格式

## 录制功能详解

### 投屏状态下录制
```bash
# 基本录制命令
scrcpy.exe --record=output.mp4

# 带参数的录制
scrcpy.exe --orientation=270 --max-fps=60 --record=game.mp4

# 录制到指定目录
scrcpy.exe --record=C:\Videos\screen_record.mp4
```

### 非投屏状态下录制
```bash
# 仅录制不显示窗口
scrcpy.exe --record=output.mp4 --no-display

# 后台录制
scrcpy.exe --record=output.mp4 --no-display --stay-awake
```

### 录制参数说明
- `--record=file.mp4` - 指定录制文件路径
- `--record-format=mp4` - 设置录制格式（mp4/mkv）
- `--no-display` - 仅录制不显示窗口
- `--stay-awake` - 录制时保持设备唤醒

## 操作说明

### 鼠标操作
- **点击** - 模拟触摸
- **拖拽** - 滚动或拖拽
- **右键** - 返回键

### 键盘快捷键
- `Ctrl+C` - 退出scrcpy
- `Ctrl+Shift+O` - 切换屏幕方向
- `Ctrl+Shift+P` - 截图
- `Ctrl+Shift+R` - 录制开始/停止

### 手势操作
- **双指缩放** - 在投屏窗口上使用鼠标滚轮
- **长按** - 右键点击

## 故障排除

### 连接问题
1. **设备未识别**
   - 检查USB调试是否启用
   - 重新插拔USB线
   - 在设备上重新授权USB调试

2. **投屏黑屏**
   - 检查设备是否锁屏
   - 尝试唤醒设备
   - 重新启动scrcpy

3. **画面卡顿**
   - 降低比特率：`--video-bit-rate=2M`
   - 降低帧率：`--max-fps=30`
   - 检查USB连接质量

### 录制问题
1. **录制文件损坏**
   - 确保有足够的磁盘空间
   - 检查文件路径权限
   - 使用绝对路径

2. **录制质量差**
   - 提高比特率：`--video-bit-rate=6M`
   - 提高帧率：`--max-fps=60`
   - 检查设备性能

### 性能优化
- 使用USB 3.0接口
- 关闭设备上的其他应用
- 降低投屏分辨率
- 禁用音频传输

## 系统要求
- Windows 10/11
- Android 5.0+
- USB 2.0+ 接口
- 至少 2GB 可用内存
- Python 3.7+（用于GUI程序）

## 文件说明
- `scrcpy.exe` - 主程序
- `adb.exe` - Android调试桥
- `scrcpy-server` - 服务器端程序
- `*.dll` - 依赖库文件
- `*.bat` - 批处理启动文件
- `scrcpy_gui.py` - 图形化控制程序
- `启动GUI.bat` - GUI启动脚本
- `build_exe.py` - 打包脚本

## 技术支持
- 官方网站：https://github.com/Genymobile/scrcpy
- 问题反馈：https://github.com/Genymobile/scrcpy/issues

---
**注意**: 使用前请确保已获得设备所有者的授权，并遵守相关法律法规。 