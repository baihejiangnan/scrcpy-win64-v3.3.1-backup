# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\Scrcpy\\scrcpy-win64-v3.3.1\\web-ui\\launcher.py'],
    pathex=['D:\\Scrcpy\\scrcpy-win64-v3.3.1\\web-ui'],
    binaries=[],
    datas=[('D:\\Scrcpy\\scrcpy-win64-v3.3.1\\web-ui\\static', 'static'), ('D:\\Scrcpy\\scrcpy-win64-v3.3.1\\web-ui\\wallpapers', 'wallpapers')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Scrcpy控制中心-fixed',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['D:\\Scrcpy\\scrcpy-win64-v3.3.1\\icon.png'],
)
