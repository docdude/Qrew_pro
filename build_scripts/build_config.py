"""
Build configuration for Qrew installers
"""

import datetime
import platform
from pathlib import Path

APP_NAME = "Qrew"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Automated Loudspeaker Measurement System"
APP_AUTHOR = "Your Name"
APP_URL = "https://github.com/docdude/Qrew_pro"
BUNDLE_IDENTIFIER = "com.docdude.Qrew"

# Fix: Use project root instead of build_scripts directory
ROOT_DIR = Path(__file__).parent.parent  # Go up one level from build_scripts
BUILD_DIR = ROOT_DIR / "build"
DIST_DIR = ROOT_DIR / "dist"
ASSETS_DIR = ROOT_DIR / "assets"
ICONS_DIR = ASSETS_DIR / "icons"

PLATFORM = platform.system().lower()
IS_MACOS = PLATFORM == "darwin"
IS_WINDOWS = PLATFORM == "windows"
IS_LINUX = PLATFORM == "linux"

# Updated icon paths with fallbacks
ICON_PATHS = {
    "darwin": ICONS_DIR / "Qrew.icns",
    "windows": ICONS_DIR / "Qrew_desktop.ico",
    "linux": ICONS_DIR / "Qrew_desktop_500x500.png",
}

# Fallback icon paths
ICON_FALLBACKS = {
    "darwin": [
        ICONS_DIR / "Qrew.icns",
        ICONS_DIR / "Qrew_desktop_500x500.png",  # Will be converted
        ICONS_DIR / "Qrew.png",
    ],
    "windows": [
        ICONS_DIR / "Qrew_desktop.ico",
        ICONS_DIR / "Qrew.ico",
        ICONS_DIR / "Qrew_desktop_500x500.png",
    ],
    "linux": [
        ICONS_DIR / "Qrew_desktop_500x500.png",
        ICONS_DIR / "Qrew.png",
        ICONS_DIR / "Qrew_desktop_500x500.svg",
    ],
}

# macOS Bundle Configuration with proper icon reference
MACOS_BUNDLE_INFO = {
    "CFBundleName": APP_NAME,
    "CFBundleDisplayName": APP_NAME,
    "CFBundleIdentifier": BUNDLE_IDENTIFIER,
    "CFBundleVersion": APP_VERSION,
    "CFBundleShortVersionString": APP_VERSION,
    "CFBundlePackageType": "APPL",
    "CFBundleSignature": "????",
    "CFBundleExecutable": APP_NAME,
    "CFBundleIconFile": "Qrew.icns",  # This should match the icon in Resources
    "CFBundleIconName": "Qrew",
    "NSHumanReadableCopyright": f"© {datetime.datetime.now().year} {APP_AUTHOR}",
    "NSHighResolutionCapable": True,
    "LSMinimumSystemVersion": "10.15",
    "NSMainNibFile": "MainMenu",
    "NSPrincipalClass": "NSApplication",
    "LSUIElement": False,  # Show in dock
    "LSApplicationCategoryType": "public.app-category.utilities",
    "NSRequiresAquaSystemAppearance": False,  # Support dark mode
}

# Essential files only - no source code in packages
ESSENTIAL_DATA_FILES = [
    # Only include essential runtime assets
    ("qrew/assets/icons/*.png", "assets/icons"),
    ("assets/icons/*.png", "assets/icons"),
    ("assets/icons/*.svg", "assets/icons"),
    ("assets/icons/*.ico", "assets/icons"),
    ("assets/icons/*.icns", "assets/icons"),
    # CRITICAL: Include settings.json for proper configuration
    ("qrew/settings.json", "."),
    # Don't include source files or development assets
]

HIDDEN_IMPORTS = [
    "requests",
    "flask",
    "gevent",
    "gevent.socket",
    "gevent.select",
    "gevent._socket3",
    "gevent.threading",
    "gevent.greenlet",
    "gevent.event",
    "gevent.timeout",
    "gevent.hub",
    "gevent.pool",
    "gevent.queue",
    "gevent._util",
    "gevent.resolver",
    "gevent.resolver.thread",
    "gevent.resolver.blocking",
    "numpy",
    "pandas",
    "vlc",
    "colour",
    "PyQt5.sip",
    "PyQt5.QtCore",
    "PyQt5.QtGui",
    "PyQt5.QtWidgets",
    # Critical macOS networking dependencies for gevent
    "socket",
    "select",
    "_socket",
    "errno",
    "fcntl",
    "signal",
    "time",
    "threading",
    "_thread",
    "Foundation",  # Critical for macOS networking!
    "CoreFoundation",  # Also needed
    "AppKit",  # Keep this for NSApp.requestUserAttention_
    # Qrew modules
    "qrew",
    "qrew.Qrew",
    "qrew.Qrew_api_helper",
    "qrew.Qrew_message_handlers",
    "qrew.Qrew_common",
    "qrew.Qrew_styles",
    "qrew.Qrew_button",
    "qrew.Qrew_dialogs",
    "qrew.Qrew_workers_v2",
    "qrew.Qrew_settings",
    "qrew.Qrew_measurement_metrics",
    "qrew.Qrew_micwidget_icons",
    "qrew.Qrew_vlc_helper_v2",
    "qrew.Qrew_messagebox",
    "qrew.Qrew_resources",
]

# Aggressive exclusions to reduce size
EXCLUDES = [
    # SCIPY - This is the main culprit for your warnings
    "scipy",
    "scipy.special",
    "scipy.special._cdflib",
    "scipy.sparse",
    "scipy.linalg",
    "scipy.integrate",
    "scipy.interpolate",
    "scipy.optimize",
    "scipy.stats",
    "scipy.signal",
    "scipy.ndimage",
    "scipy.spatial",
    "scipy.cluster",
    "scipy.fft",
    "scipy.fftpack",
    "scipy.io",
    "scipy.misc",
    #  IMPORTANT: Don't exclude Foundation/CoreFoundation - needed for gevent networking!
    # "PyObjC",
    # "objc",
    # "AppKit",  # Needed for notifications
    # "Foundation",  # CRITICAL - needed by gevent for macOS networking!
    # "CoreFoundation",  # CRITICAL - also needed for networking
    "Cocoa",
    "CoreGraphics",
    "Quartz",
    "WebKit",
    "ScriptingBridge",
    "LaunchServices",
    "CoreData",
    "CoreText",
    "CoreImage",
    "ImageIO",
    "AVFoundation",
    "AVKit",
    #  NEW: Platform-specific modules that cause cross-platform issues
    "win32api",
    "win32con",
    "win32gui",
    "win32process",
    "win32security",
    "win32service",
    "win32event",
    "win32file",
    "win32pipe",
    "pywintypes",
    "pythoncom",
    "winxpgui",
    "winsound",
    #  "msvcrt",
    "winreg",
    # Linux-specific that might cause issues on macOS builds
    "pwd",
    "grp",
    "spwd",
    "termios",
    "tty",
    "pty",
    "fcntl",  # DON'T EXCLUDE - needed by gevent
    # "resource",  # DON'T EXCLUDE - might be needed
    # Development tools
    "tkinter",  # This was causing warnings too
    "test",
    "unittest",
    "pdb",
    "pydoc",
    "doctest",
    "distutils",
    "setuptools",
    "pkg_resources",
    "wheel",
    "pip",
    # Large unused libraries
    "matplotlib",
    "IPython",
    "jupyter",
    "notebook",
    "sklearn",
    "scikit-learn",
    # Unused Qt modules
    "PyQt5.QtQuick",
    "PyQt5.QtQml",
    "PyQt5.QtWebSockets",
    "PyQt5.QtDBus",
    "PyQt5.QtPrintSupport",
    "PyQt5.QtMultimedia",
    "PyQt5.QtMultimediaWidgets",
    "PyQt5.QtOpenGL",
    "PyQt5.QtPositioning",
    "PyQt5.QtQuickWidgets",
    "PyQt5.QtSensors",
    "PyQt5.QtSerialPort",
    "PyQt5.QtSql",
    "PyQt5.QtTest",
    "PyQt5.QtWebKit",
    "PyQt5.QtWebKitWidgets",
    "PyQt5.QtXml",
    "PyQt5.QtXmlPatterns",
    # XML parsers we don't need
    "xml.etree.cElementTree",
    "xml.dom",
    "xml.parsers.expat",
    # Network modules we might not need - BE CAREFUL HERE!
    # "email",  # might be needed
    "smtplib",
    "poplib",
    "imaplib",
    # Other large modules often not needed
    "curses",
    "readline",
    "sqlite3",
    # "ssl",  # Keep for HTTPS if needed
    # Pandas optional dependencies that pull in scipy
    #  "pandas.plotting",
    # "pandas.io.formats.style",
    # Source code modules that shouldn't be in final package
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
]


def get_icon_for_platform():
    """Get the best available icon for the current platform"""
    fallbacks = ICON_FALLBACKS.get(PLATFORM, [])

    for icon_path in fallbacks:
        if icon_path and icon_path.exists():
            print(f"Using icon: {icon_path}")
            return icon_path

    print(f"WARNING: No icon found for platform {PLATFORM}")
    return None


def get_macos_bundle_info():
    """Generate macOS bundle info dictionary"""
    return MACOS_BUNDLE_INFO


def ensure_directories():
    """Ensure build directories exist"""
    BUILD_DIR.mkdir(exist_ok=True)
    DIST_DIR.mkdir(exist_ok=True)
    ASSETS_DIR.mkdir(exist_ok=True)
    ICONS_DIR.mkdir(exist_ok=True)
    return True
