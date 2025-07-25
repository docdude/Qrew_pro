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
    binaries=[],
    datas=[(r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._BDL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._BDR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._C.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._FDL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._FDR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._FHL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._FHR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._FL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._FR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._FWL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._FWR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._RHL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._RHR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._SBL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._SBR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._SDL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._SDR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._SHL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._SHR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._SLA.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._SRA.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._SW1.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._SW2.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._SW3.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._SW4.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._TFL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._TFR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._TML.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._TMR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._TRL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/._TRR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/BDL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/BDR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/C.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/FDL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/FDR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/FHL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/FHR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/FL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/FR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/FWL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/FWR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/gear@2x.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/RHL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/RHR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/SBL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/SBR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/SDL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/SDR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/SHL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/SHR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/SLA.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/SRA.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/SW1.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/SW2.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/SW3.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/SW4.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/TFL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/TFR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/TML.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/TMR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/TRL.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/assets/icons/TRR.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/assets/icons/._Qrew_desktop_500x500.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/assets/icons/Qrew_desktop_500x500.png', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/assets/icons/._Qrew_desktop_500x500.svg', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/assets/icons/Qrew_desktop_500x500.svg', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/assets/icons/Qrew_desktop.ico', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/assets/icons/._Qrew.icns', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/assets/icons/Qrew.icns', 'assets/icons'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/settings.json', '.'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/settings.json', 'qrew'), (r'C:/Users/centralmd/Documents/Qrew_pro/qrew/settings.json', '.')],
    hiddenimports=['requests', 'flask', 'gevent', 'gevent.socket', 'gevent.select', 'gevent._socket3', 'gevent.threading', 'gevent.greenlet', 'gevent.event', 'gevent.timeout', 'gevent.hub', 'gevent.pool', 'gevent.queue', 'gevent._util', 'gevent.resolver', 'gevent.resolver.thread', 'gevent.resolver.blocking', 'numpy', 'pandas', 'vlc', 'colour', 'PyQt5.sip', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'socket', 'select', '_socket', 'errno', 'fcntl', 'signal', 'time', 'threading', '_thread', 'Foundation', 'CoreFoundation', 'AppKit', 'qrew', 'qrew.Qrew', 'qrew.Qrew_api_helper', 'qrew.Qrew_message_handlers', 'qrew.Qrew_common', 'qrew.Qrew_styles', 'qrew.Qrew_button', 'qrew.Qrew_dialogs', 'qrew.Qrew_workers_v2', 'qrew.Qrew_settings', 'qrew.Qrew_measurement_metrics', 'qrew.Qrew_micwidget_icons', 'qrew.Qrew_vlc_helper_v2', 'qrew.Qrew_messagebox', 'qrew.Qrew_resources'],
    excludes=['scipy', 'scipy.special', 'scipy.special._cdflib', 'scipy.sparse', 'scipy.linalg', 'scipy.integrate', 'scipy.interpolate', 'scipy.optimize', 'scipy.stats', 'scipy.signal', 'scipy.ndimage', 'scipy.spatial', 'scipy.cluster', 'scipy.fft', 'scipy.fftpack', 'scipy.io', 'scipy.misc', 'Cocoa', 'CoreGraphics', 'Quartz', 'WebKit', 'ScriptingBridge', 'LaunchServices', 'CoreData', 'CoreText', 'CoreImage', 'ImageIO', 'AVFoundation', 'AVKit', 'win32api', 'win32con', 'win32gui', 'win32process', 'win32security', 'win32service', 'win32event', 'win32file', 'win32pipe', 'pywintypes', 'pythoncom', 'winxpgui', 'winsound', 'winreg', 'pwd', 'grp', 'spwd', 'termios', 'tty', 'pty', 'fcntl', 'tkinter', 'test', 'unittest', 'pdb', 'pydoc', 'doctest', 'distutils', 'setuptools', 'pkg_resources', 'wheel', 'pip', 'matplotlib', 'IPython', 'jupyter', 'notebook', 'sklearn', 'scikit-learn', 'PyQt5.QtQuick', 'PyQt5.QtQml', 'PyQt5.QtWebSockets', 'PyQt5.QtDBus', 'PyQt5.QtPrintSupport', 'PyQt5.QtMultimedia', 'PyQt5.QtMultimediaWidgets', 'PyQt5.QtOpenGL', 'PyQt5.QtPositioning', 'PyQt5.QtQuickWidgets', 'PyQt5.QtSensors', 'PyQt5.QtSerialPort', 'PyQt5.QtSql', 'PyQt5.QtTest', 'PyQt5.QtWebKit', 'PyQt5.QtWebKitWidgets', 'PyQt5.QtXml', 'PyQt5.QtXmlPatterns', 'xml.etree.cElementTree', 'xml.dom', 'xml.parsers.expat', 'smtplib', 'poplib', 'imaplib', 'curses', 'readline', 'sqlite3', '__pycache__', '*.pyc', '*.pyo', '*.pyd'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['C:/Users/centralmd/Documents/Qrew_pro/build_scripts/vlc_hook.py'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Qrew',
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
    icon=r'C:/Users/centralmd/Documents/Qrew_pro/assets/icons/Qrew_desktop.ico' if r'C:/Users/centralmd/Documents/Qrew_pro/assets/icons/Qrew_desktop.ico' else None,
)
