# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['potdict.py'],
    pathex=[],
    binaries=[],
    
    datas=[('./data/html/400.html', './data/html/'), ('./data/html/homepage.html', './data/html/'), 
    ('./data/html/not_found.html', './data/html/'), ('./data/html/result.html', './data/html/'), 
    ('./data/default_settings.json', './data'), ('./data/ico.ico', './data'), ('./scr/__init__.py', './scr'), 
    ('./scr/listener.py', './scr'), ('./scr/logger.py', './scr'), ('./scr/dict.py', './scr')],
    
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
    name='PotDict',
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
    icon=['./data/ico.ico'],
)
