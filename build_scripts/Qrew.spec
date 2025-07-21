# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['qrew/main.py'],
    pathex=['/Users/juanloya/Documents/qrew/build_scripts'],
    binaries=[],
    datas=[('qrew/assets/*', 'assets'), ('qrew/settings.json', '.'), ('README.md', '.'), ('LICENSE', '.')],
    hiddenimports=['requests', 'flask', 'numpy', 'pandas', 'scipy', 'vlc', 'colour', 'PyQt5.sip'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Qrew',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='/Users/juanloya/Documents/qrew/build_scripts/assets/icons/qrew.png',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Qrew',
)

app = BUNDLE(coll, name="Qrew.app", icon="/Users/juanloya/Documents/qrew/build_scripts/assets/icons/qrew.png", bundle_identifier="com.yourcompany.qrew")
