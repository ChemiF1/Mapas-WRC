# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\mapasWRC.py'],
    pathex=[],
    binaries=[],
    datas=[('./resources/icon.ico', './resources/'), ('./resources/logoDP.png', '.')],
    hiddenimports=['fiona._shim','pkg_resources.extern'],
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
    name='mapasWRC',
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
    icon=['resources\\icon.ico'],
)
