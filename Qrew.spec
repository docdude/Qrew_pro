# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Ensure qrew package can be found
sys.path.insert(0, r'C:/Users/centralmd/Documents/Qrew_pro/qrew')
sys.path.insert(0, r'C:/Users/centralmd/Documents/Qrew_pro')

block_cipher = None


a = Analysis(
    [r'C:/Users/centralmd/Documents/Qrew_pro/qrew/main.py'],
    pathex=[r'C:/Users/centralmd/Documents/Qrew_pro', r'C:/Users/centralmd/Documents/Qrew_pro/qrew'],
    binaries=[
    (r'C:/Users/centralmd/Downloads/vlc-3.0.21-win64/vlc-3.0.21/libvlc.dll', '.'),
    (r'C:/Users/centralmd/Downloads/vlc-3.0.21-win64/vlc-3.0.21/libvlccore.dll', '.'),
],
    datas=[(r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets', 'assets'), (r'C:/Users/centralmd/Documents/Qrew_pro/README.md', '.'), (r'C:/Users/centralmd/Documents/Qrew_pro/LICENSE', '.'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/coordinate_picker.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/main.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/mic_pos.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/mic_widget.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew2.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew3.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew4.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_api_helper.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_button.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_common.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_dialogs.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_filedialog.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_find_vlc.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_gridwidget.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_measurement_metrics.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_messagebox.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_message_handlers.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_micwidget_icons.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_resources.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_settings.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_styles.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_v1.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_vlc_helper.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_vlc_helper_v2.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_workers.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/Qrew_workers_v2.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/__init__.py', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/__main__.py', 'qrew')],
    hiddenimports=['qrew', 'qrew.Qrew', 'qrew.Qrew_api_helper', 'qrew.Qrew_message_handlers', 'qrew.Qrew_common', 'qrew.Qrew_styles', 'qrew.Qrew_button', 'qrew.Qrew_dialogs', 'qrew.Qrew_workers_v2', 'qrew.Qrew_settings', 'qrew.Qrew_measurement_metrics', 'qrew.Qrew_micwidget_icons', 'qrew.Qrew_vlc_helper_v2', 'qrew.Qrew_messagebox', 'qrew.Qrew_resources', 'requests', 'flask', 'gevent', 'numpy', 'pandas', 'vlc', 'colour', 'PyQt5.sip', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets'],
    excludes=['tkinter', 'matplotlib', 'IPython', 'PyQt5.QtQuick', 'PyQt5.QtQml', 'PyQt5.QtWebSockets', 'PyQt5.QtDBus', 'PyQt5.QtPrintSupport', 'test', 'unittest', 'pdb', 'pydoc', 'doctest', 'xml.etree', 'xml.parsers', 'setuptools', 'pkg_resources', 'wheel', 'pip'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[r'C:/Users/centralmd/Documents/Qrew_pro/build_scripts/vlc_hook.py'],
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
    strip=False,  # Strip debug symbols on Linux
    upx=False,     # Enable UPX compression on Linux
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'C:/Users/centralmd/Documents/Qrew_pro/assets/icons/Qrew_desktop.ico' if r'C:/Users/centralmd/Documents/Qrew_pro/assets/icons/Qrew_desktop.ico' else None,
    version=r'C:/Users/centralmd/Documents/Qrew_pro/assets/file_version_info.txt' if r'C:/Users/centralmd/Documents/Qrew_pro/assets/file_version_info.txt' and os.path.exists(r'C:/Users/centralmd/Documents/Qrew_pro/assets/file_version_info.txt') else None,

)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,  # Strip binaries
    upx=False,      # Compress binaries
    upx_exclude=[],
    name='Qrew',
)
