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

ICON_PATHS = {
    "darwin": ICONS_DIR / "Qrew.icns",
    "windows": ICONS_DIR / "Qrew_desktop.ico",
    "linux": ICONS_DIR / "Qrew_desktop_500x500.png",
}

# macOS Bundle Configuration
MACOS_BUNDLE_INFO = {
    "CFBundleName": APP_NAME,
    "CFBundleDisplayName": APP_NAME,
    "CFBundleIdentifier": BUNDLE_IDENTIFIER,
    "CFBundleVersion": APP_VERSION,
    "CFBundleShortVersionString": APP_VERSION,
    "CFBundlePackageType": "APPL",
    "CFBundleSignature": "????",
    "CFBundleExecutable": APP_NAME,
    "CFBundleIconFile": "Qrew.icns",
    "CFBundleIconName": "Qrew",  # Add this line
    "NSHumanReadableCopyright": (f"© {datetime.datetime.now().year} {APP_AUTHOR}"),
    "NSHighResolutionCapable": True,
    "LSMinimumSystemVersion": "10.15",  # Minimum macOS version
    "NSMainNibFile": "MainMenu",
    "NSPrincipalClass": "NSApplication",
}

PYINSTALLER_OPTIONS = [
    "--name",
    APP_NAME,
    "--onedir",
    "--windowed",
    "--clean",
    "--noconfirm",
    f"--distpath={DIST_DIR}",
    f"--workpath={BUILD_DIR}",
]

# Fix: Correct data files paths relative to project root
DATA_FILES = [
    ("qrew/assets/*", "assets"),
    ("qrew/settings.json", "."),
    ("README.md", "."),
    ("LICENSE", "."),
]

HIDDEN_IMPORTS = [
    "requests",
    "flask",
    "gevent",
    "numpy",
    "pandas",
    "vlc",
    "colour",
    "PyQt5.sip",
    "PyQt5.QtCore",
    "PyQt5.QtGui",
    "PyQt5.QtWidgets",
]


def get_icon_for_platform():
    """
    Get icons for platform
    """
    return str(ICON_PATHS.get(PLATFORM, ICON_PATHS["linux"]))


def get_macos_bundle_info():
    """
    Generate macOS bundle info dictionary
    """
    return MACOS_BUNDLE_INFO


def ensure_directories():
    """
    Sanity check for app program directories
    """
    BUILD_DIR.mkdir(exist_ok=True)
    DIST_DIR.mkdir(exist_ok=True)
    ASSETS_DIR.mkdir(exist_ok=True)
    ICONS_DIR.mkdir(exist_ok=True)
