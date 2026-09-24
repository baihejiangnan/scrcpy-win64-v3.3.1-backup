"""Build the current Web UI executable and its external scrcpy runtime."""

from pathlib import Path
import shutil

import PyInstaller.__main__


ROOT = Path(__file__).resolve().parent
RUNTIME_FILES = (
    "adb.exe",
    "AdbWinApi.dll",
    "AdbWinUsbApi.dll",
    "scrcpy.exe",
    "scrcpy-server",
    "SDL2.dll",
    "avcodec-61.dll",
    "avformat-61.dll",
    "avutil-59.dll",
    "libusb-1.0.dll",
    "swresample-5.dll",
)


def main() -> None:
    required = [
        ROOT / "web-ui" / "launcher.py",
        ROOT / "web-ui" / "static",
        ROOT / "web-ui" / "wallpapers",
        ROOT / "icon.png",
        *(ROOT / name for name in RUNTIME_FILES),
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise SystemExit("缺少打包文件：" + ", ".join(missing))

    dist = ROOT / "dist"
    PyInstaller.__main__.run(
        [
            str(ROOT / "web-ui" / "launcher.py"),
            "--onefile",
            "--windowed",
            "--noconfirm",
            "--name=Scrcpy控制中心",
            f"--icon={ROOT / 'icon.png'}",
            f"--paths={ROOT / 'web-ui'}",
            f"--add-data={ROOT / 'web-ui' / 'static'};static",
            f"--add-data={ROOT / 'web-ui' / 'wallpapers'};wallpapers",
            f"--distpath={dist}",
            f"--workpath={ROOT / 'build'}",
            f"--specpath={ROOT / 'build'}",
        ]
    )
    for name in RUNTIME_FILES:
        shutil.copy2(ROOT / name, dist / name)
    print(f"打包完成：{dist / 'Scrcpy控制中心.exe'}")


if __name__ == "__main__":
    main()
