# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Ensure qrew package can be found
sys.path.insert(0, r'/Users/juanloya/Documents/qrew/qrew')
sys.path.insert(0, r'/Users/juanloya/Documents/qrew')

block_cipher = None


a = Analysis(
    [r'/Users/juanloya/Documents/qrew/qrew/main.py'],
    pathex=[r'/Users/juanloya/Documents/qrew', r'/Users/juanloya/Documents/qrew/qrew'],
    binaries=[],
    datas=[(r'/Users/juanloya/Documents/qrew/qrew/assets', 'assets'), (r'/Users/juanloya/Documents/qrew/README.md', '.'), (r'/Users/juanloya/Documents/qrew/LICENSE', '.'), (r'/Users/juanloya/Documents/qrew/qrew/mic_pos.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_measurement_metrics.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_message_handlers.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew3.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_vlc_helper.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew2.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/__init__.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_workers.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_dialogs.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_settings.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/mic_widget.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_styles.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/coordinate_picker.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_resources.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew4.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_filedialog.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_vlc_helper_v2.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_button.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_common.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_v1.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/main.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_gridwidget.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/__main__.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_workers_v2.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_micwidget_icons.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_messagebox.py', 'qrew'), (r'/Users/juanloya/Documents/qrew/qrew/Qrew_api_helper.py', 'qrew')],
    hiddenimports=['qrew', 'qrew.Qrew', 'qrew.Qrew_api_helper', 'qrew.Qrew_message_handlers', 'qrew.Qrew_common', 'qrew.Qrew_styles', 'qrew.Qrew_button', 'qrew.Qrew_dialogs', 'qrew.Qrew_workers_v2', 'qrew.Qrew_settings', 'qrew.Qrew_measurement_metrics', 'qrew.Qrew_micwidget_icons', 'qrew.Qrew_vlc_helper_v2', 'qrew.Qrew_messagebox', 'qrew.Qrew_resources', 'requests', 'flask', 'gevent', 'numpy', 'pandas', 'vlc', 'colour', 'PyQt5.sip', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
    excludes=['tkinter', 'matplotlib', 'IPython', 'PyQt5.QtQuick', 'PyQt5.QtQml', 'PyQt5.QtWebSockets', 'PyQt5.QtDBus', 'PyQt5.QtPrintSupport', 'test', 'unittest', 'pdb', 'pydoc'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
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
    upx=False,  # Disable UPX to avoid compatibility issues
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'/Users/juanloya/Documents/qrew/assets/icons/Qrew.icns' if r'/Users/juanloya/Documents/qrew/assets/icons/Qrew.icns' else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Qrew',
)
app = BUNDLE(
    coll,
    name='Qrew.app',
    icon=r'/Users/juanloya/Documents/qrew/assets/icons/Qrew.icns' if r'/Users/juanloya/Documents/qrew/assets/icons/Qrew.icns' else None,
    bundle_identifier='com.docdude.Qrew',
    info_plist={'CFBundleName': 'Qrew', 'CFBundleDisplayName': 'Qrew', 'CFBundleIdentifier': 'com.docdude.Qrew', 'CFBundleVersion': '1.0.0', 'CFBundleShortVersionString': '1.0.0', 'CFBundlePackageType': 'APPL', 'CFBundleSignature': '????', 'CFBundleExecutable': 'Qrew', 'CFBundleIconFile': 'Qrew.icns', 'CFBundleIconName': 'Qrew', 'NSHumanReadableCopyright': '© 2025 Your Name', 'NSHighResolutionCapable': True, 'LSMinimumSystemVersion': '10.15', 'NSMainNibFile': 'MainMenu', 'NSPrincipalClass': 'NSApplication'}
)
