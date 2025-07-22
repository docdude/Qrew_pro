"""
Universal build script for Qrew
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from build_scripts.build_config import *
except ImportError:
    print(
        "Error: Could not import build_config. Make sure build_scripts/build_config.py exists."
    )
    sys.exit(1)


def run_command(cmd, cwd=None, timeout=600):
    """Run a command with proper error handling and timeout"""
    print(f"Running: {' '.join(cmd)}")
    print(f"Working directory: {cwd or os.getcwd()}")

    try:
        result = subprocess.run(
            cmd, cwd=cwd, check=True, capture_output=True, text=True, timeout=timeout
        )
        if result.stdout:
            print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.TimeoutExpired:
        print(f"❌ Command timed out after {timeout} seconds")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def install_build_dependencies():
    """Install build dependencies based on platform"""
    print("Installing build dependencies...")

    dependencies = ["pyinstaller>=5.0", "wheel", "setuptools>=60.0", "Pillow>=8.0"]

    if IS_MACOS:
        dependencies.extend(["dmgbuild>=1.5.0"])
    elif IS_WINDOWS:
        dependencies.extend(["pywin32>=227"])
    elif IS_LINUX:
        dependencies.extend(["python3-distutils"])

    cmd = [sys.executable, "-m", "pip", "install"] + dependencies
    return run_command(cmd)


def clean_build():
    """Clean previous build artifacts safely"""
    print("Cleaning previous builds...")

    # Remove build and dist directories if they exist
    for path in [BUILD_DIR, DIST_DIR]:
        try:
            if path.exists() and path.is_dir():
                shutil.rmtree(path)
                print(f"Removed {path}")
        except Exception as e:
            print(f"Failed to remove {path}: {e}")

    # Remove .spec files in the root directory
    for spec_file in ROOT_DIR.glob("*.spec"):
        try:
            spec_file.unlink()
            print(f"Removed {spec_file}")
        except Exception as e:
            print(f"Failed to remove {spec_file}: {e}")

    # Recreate necessary directories
    ensure_directories()


def ensure_macos_icon():
    """Ensure macOS icon exists and is in correct format"""
    if not IS_MACOS:
        return True

    icns_path = ICONS_DIR / "Qrew.icns"
    appiconset_path = ICONS_DIR / "Qrew.appiconset"
    png_path = ICONS_DIR / "Qrew_desktop_500x500.png"

    # If ICNS already exists, we're good
    if icns_path.exists():
        print(f"✅ Found existing ICNS: {icns_path}")
        return True

    # Try to convert appiconset to icns
    if appiconset_path.exists() and (appiconset_path / "Contents.json").exists():
        print(f"Converting {appiconset_path} to {icns_path}")
        try:
            result = subprocess.run(
                ["iconutil", "-c", "icns", str(appiconset_path), "-o", str(icns_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"✅ Created {icns_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to convert appiconset: {e}")
            print(f"Stderr: {e.stderr}")

    # Try to create iconset from PNG
    if png_path.exists():
        print(f"Creating iconset from {png_path}")
        return create_iconset_from_png(png_path, icns_path)

    print("⚠️  No suitable icon found, continuing without icon")
    return False


def create_iconset_from_png(png_path, icns_path):
    """Create iconset and icns from PNG file"""
    try:
        from PIL import Image

        iconset_path = icns_path.parent / (icns_path.stem + ".iconset")
        iconset_path.mkdir(exist_ok=True)

        # Load source image
        source_img = Image.open(png_path)

        # Icon sizes for macOS
        sizes = [
            (16, "icon_16x16.png"),
            (32, "icon_16x16@2x.png"),
            (32, "icon_32x32.png"),
            (64, "icon_32x32@2x.png"),
            (128, "icon_128x128.png"),
            (256, "icon_128x128@2x.png"),
            (256, "icon_256x256.png"),
            (512, "icon_256x256@2x.png"),
            (512, "icon_512x512.png"),
            (1024, "icon_512x512@2x.png"),
        ]

        # Generate all icon sizes
        for size, filename in sizes:
            resized = source_img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(iconset_path / filename, "PNG")

        # Convert to ICNS
        result = subprocess.run(
            ["iconutil", "-c", "icns", str(iconset_path), "-o", str(icns_path)],
            check=True,
            capture_output=True,
            text=True,
        )

        print(f"✅ Created ICNS from PNG: {icns_path}")
        return True

    except ImportError:
        print("❌ Pillow not installed, cannot convert PNG to iconset")
        return False
    except Exception as e:
        print(f"❌ Failed to create iconset: {e}")
        return False


def check_python_environment():
    """Check Python environment and dependencies"""
    print("Checking Python environment...")

    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")

    # Check if main module can be imported
    try:
        sys.path.insert(0, str(ROOT_DIR))
        from qrew.main import main

        print("✅ Main module import successful")
        return True
    except ImportError as e:
        print(f"❌ Cannot import main module: {e}")
        return False


def build_pyinstaller():
    """Build application using PyInstaller"""
    print("Building with PyInstaller...")

    # Check Python environment
    if not check_python_environment():
        return False

    # Ensure macOS icon if needed
    if IS_MACOS:
        ensure_macos_icon()

    # Test PyInstaller installation
    print("Testing PyInstaller installation...")
    if not run_command(
        [sys.executable, "-m", "PyInstaller", "--version"], cwd=ROOT_DIR
    ):
        print("❌ PyInstaller not working properly")
        return False

    # Generate spec file
    spec_content = generate_pyinstaller_spec()
    spec_file = ROOT_DIR / f"{APP_NAME}.spec"

    with open(spec_file, "w") as f:
        f.write(spec_content)
    print(f"✅ Generated spec file: {spec_file}")

    # Run PyInstaller
    print("Starting PyInstaller build...")
    cmd = [sys.executable, "-m", "PyInstaller", "--log-level=INFO", str(spec_file)]

    success = run_command(cmd, cwd=ROOT_DIR, timeout=900)  # 15 minutes timeout

    if success:
        print("✅ PyInstaller build completed successfully")

        # Verify output
        if IS_MACOS:
            app_path = DIST_DIR / f"{APP_NAME}.app"
            if app_path.exists():
                print(f"✅ macOS app bundle created: {app_path}")
            else:
                print("❌ macOS app bundle not found")
                return False
        else:
            exe_dir = DIST_DIR / APP_NAME
            if exe_dir.exists():
                print(f"✅ Application directory created: {exe_dir}")
            else:
                print("❌ Application directory not found")
                return False

    return success


def generate_pyinstaller_spec():
    """Generate PyInstaller spec file with proper configuration"""
    icon_path = get_icon_for_platform()

    # Data files - only include files that exist
    data_files = []

    # Add qrew package files
    qrew_assets = ROOT_DIR / "qrew" / "assets"
    if qrew_assets.exists():
        data_files.append(f"('{qrew_assets}', 'assets')")

    # Add all qrew python files individually
    qrew_py_files = []
    qrew_dir = ROOT_DIR / "qrew"
    if qrew_dir.exists():
        for py_file in qrew_dir.glob("*.py"):
            if py_file.name != "__pycache__":
                qrew_py_files.append(f"('{py_file}', 'qrew')")

    # Add other data files
    for file_path in [ROOT_DIR / "README.md", ROOT_DIR / "LICENSE"]:
        if file_path.exists():
            data_files.append(f"('{file_path}', '.')")

    data_files_str = "[" + ", ".join(data_files + qrew_py_files) + "]"

    # Hidden imports - comprehensive list
    hidden_imports = [
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
        "requests",
        "flask",
        "numpy",
        "pandas",
        "gevent",
        "vlc",
        "colour",
        "PyQt5.sip",
        "PyQt5.QtCore",
        "PyQt5.QtGui",
        "PyQt5.QtWidgets",
    ]

    excludes_list = [
        "tkinter",
        "matplotlib",
        "IPython",
        "PyQt5.QtQuick",
        "PyQt5.QtQml",
        "PyQt5.QtWebSockets",
        "PyQt5.QtDBus",
        "PyQt5.QtPrintSupport",
    ]

    # macOS bundle info
    bundle_section = ""
    if IS_MACOS:
        bundle_info = get_macos_bundle_info()
        bundle_section = f"""
app = BUNDLE(
    coll,
    name='{APP_NAME}.app',
    icon='{icon_path}' if '{icon_path}' else None,
    bundle_identifier='{BUNDLE_IDENTIFIER}',
    info_plist={bundle_info}
)"""

    return f"""# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Ensure qrew package can be found
sys.path.insert(0, str(Path.cwd() / 'qrew'))
sys.path.insert(0, str(Path.cwd()))

block_cipher = None

a = Analysis(
    ['qrew/main.py'],
    pathex=['{ROOT_DIR}', '{ROOT_DIR / "qrew"}'],
    binaries=[],
    datas={data_files_str},
    hiddenimports={hidden_imports},
    excludes={excludes_list},
    hookspath=[],
    hooksconfig={{}},
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
    name='{APP_NAME}',
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
    icon='{icon_path}' if '{icon_path}' else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='{APP_NAME}',
){bundle_section}
"""


def main():
    """Main build function"""
    parser = argparse.ArgumentParser(description="Build Qrew installers")
    parser.add_argument("--clean", action="store_true", help="Clean before building")
    parser.add_argument(
        "--deps", action="store_true", help="Install build dependencies"
    )
    parser.add_argument(
        "--platform", action="store_true", help="Build platform-specific installer"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    print(f"🚀 Building Qrew for {PLATFORM}")
    print(f"📁 Root directory: {ROOT_DIR}")
    print(f"🔧 Build directory: {BUILD_DIR}")
    print(f"📦 Distribution directory: {DIST_DIR}")

    # Install dependencies if requested
    if args.deps:
        print("📥 Installing build dependencies...")
        if not install_build_dependencies():
            print("❌ Failed to install build dependencies")
            sys.exit(1)
        print("✅ Build dependencies installed successfully")

    # Clean build if requested
    if args.clean:
        clean_build()

    # Ensure directories exist
    ensure_directories()

    # Build with PyInstaller
    if not build_pyinstaller():
        print("❌ PyInstaller build failed")
        sys.exit(1)

    # Build platform-specific installer if requested
    if args.platform:
        print(f"🔧 Building {PLATFORM} platform installer...")

        if IS_MACOS:
            try:
                from build_macos import build_macos_installer

                if build_macos_installer():
                    print("✅ macOS installer created successfully")
                else:
                    print("❌ macOS installer creation failed")
            except ImportError as e:
                print(f"❌ Could not import macOS build module: {e}")

        elif IS_WINDOWS:
            try:
                from build_windows import build_windows_installer

                if build_windows_installer():
                    print("✅ Windows installer created successfully")
                else:
                    print("❌ Windows installer creation failed")
            except ImportError as e:
                print(f"❌ Could not import Windows build module: {e}")

        elif IS_LINUX:
            try:
                from build_linux import build_linux_installer

                if build_linux_installer():
                    print("✅ Linux packages created successfully")
                else:
                    print("❌ Linux package creation failed")
            except ImportError as e:
                print(f"❌ Could not import Linux build module: {e}")

    # Print summary
    print("\n" + "=" * 50)
    print("🎉 BUILD COMPLETED")
    print("=" * 50)

    if DIST_DIR.exists():
        print("📦 Output files:")
        for item in DIST_DIR.iterdir():
            if item.is_file():
                size_mb = item.stat().st_size / (1024 * 1024)
                print(f"  📄 {item.name} ({size_mb:.1f} MB)")
            elif item.is_dir():
                print(f"  📁 {item.name}/")

    if IS_MACOS:
        app_path = DIST_DIR / f"{APP_NAME}.app"
        if app_path.exists():
            print(f"\n🍎 macOS app created: {app_path}")
            print(f"🚀 Test with: open {app_path}")


if __name__ == "__main__":
    main()
