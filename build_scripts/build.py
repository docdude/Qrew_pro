"""
Universal build script for Qrew
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse
import time
import platform as platform_module

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from build_scripts.build_config import *
except ImportError:
    print(
        "ERROR: Could not import build_config. Make sure build_scripts/build_config.py exists."
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
        print(f"ERROR: Command timed out after {timeout} seconds")
        return False
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
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


def check_build_environment():
    """Check build environment and dependencies"""
    print("Checking build environment...")

    # Check Python version
    py_version = sys.version_info
    if py_version < (3, 8):
        print(
            f"WARNING: Python {py_version.major}.{py_version.minor} may not be fully supported"
        )

    # Check platform
    print(f"Platform: {platform_module.system()} {platform_module.release()}")
    print(f"Architecture: {platform_module.machine()}")

    # Check disk space
    if hasattr(shutil, "disk_usage"):
        total, used, free = shutil.disk_usage(ROOT_DIR)
        free_gb = free // (1024**3)
        print(f"Available disk space: {free_gb} GB")
        if free_gb < 2:
            print("WARNING: Low disk space may cause build to fail")

    # Check required directories
    required_dirs = [ROOT_DIR / "qrew", ASSETS_DIR, ICONS_DIR]
    for dir_path in required_dirs:
        if not dir_path.exists():
            print(f"ERROR: Required directory not found: {dir_path}")
            return False

    return True


def clean_build():
    """Clean previous build artifacts safely"""
    print("Cleaning previous builds...")

    # Remove build and dist directories if they exist
    for path in [BUILD_DIR, DIST_DIR]:
        try:
            if path.exists() and path.is_dir():
                print(f"Removing {path}...")
                shutil.rmtree(path)
                print(f"SUCCESS: Removed {path}")
        except Exception as e:
            print(f"WARNING: Failed to remove {path}: {e}")

    # Remove .spec files in the root directory
    for spec_file in ROOT_DIR.glob("*.spec"):
        try:
            spec_file.unlink()
            print(f"SUCCESS: Removed {spec_file}")
        except Exception as e:
            print(f"WARNING: Failed to remove {spec_file}: {e}")

    # Clean Python cache
    for cache_dir in ROOT_DIR.rglob("__pycache__"):
        try:
            shutil.rmtree(cache_dir)
            print(f"SUCCESS: Removed cache {cache_dir}")
        except Exception as e:
            print(f"WARNING: Failed to remove cache {cache_dir}: {e}")

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
        print(f"SUCCESS: Found existing ICNS: {icns_path}")
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
            print(f"SUCCESS: Created {icns_path}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to convert appiconset: {e}")
            if e.stderr:
                print(f"Stderr: {e.stderr}")

    # Try to create iconset from PNG
    if png_path.exists():
        print(f"Creating iconset from {png_path}")
        return create_iconset_from_png(png_path, icns_path)

    print("WARNING: No suitable icon found, continuing without icon")
    return False


def create_iconset_from_png(png_path, icns_path):
    """Create iconset and icns from PNG file"""
    try:
        from PIL import Image

        iconset_path = icns_path.parent / (icns_path.stem + ".iconset")
        iconset_path.mkdir(exist_ok=True)

        # Load source image
        source_img = Image.open(png_path)
        print(f"Loaded source image: {png_path} ({source_img.size})")

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

        print(f"Generated {len(sizes)} icon sizes")

        # Convert to ICNS
        result = subprocess.run(
            ["iconutil", "-c", "icns", str(iconset_path), "-o", str(icns_path)],
            check=True,
            capture_output=True,
            text=True,
        )

        print(f"SUCCESS: Created ICNS from PNG: {icns_path}")
        return True

    except ImportError:
        print("ERROR: Pillow not installed, cannot convert PNG to iconset")
        return False
    except Exception as e:
        print(f"ERROR: Failed to create iconset: {e}")
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

        print("SUCCESS: Main module import successful")
        return True
    except ImportError as e:
        print(f"ERROR: Cannot import main module: {e}")
        print("This may indicate missing dependencies or incorrect project structure")
        return False


def verify_qrew_modules():
    """Verify all required Qrew modules can be imported"""
    print("Verifying Qrew modules...")

    required_modules = [
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

    missing_modules = []

    for module_name in required_modules:
        try:
            __import__(module_name)
            print(f"SUCCESS: {module_name}")
        except ImportError as e:
            print(f"WARNING: {module_name} - {e}")
            missing_modules.append(module_name)

    if missing_modules:
        print(f"WARNING: {len(missing_modules)} modules could not be imported")
        return False

    print("SUCCESS: All required modules verified")
    return True


def build_pyinstaller():
    """Build application using PyInstaller"""
    print("Building with PyInstaller...")

    # Check Python environment
    if not check_python_environment():
        return False

    # Verify Qrew modules
    if not verify_qrew_modules():
        print("WARNING: Some modules missing, build may fail")

    # Ensure macOS icon if needed
    if IS_MACOS:
        ensure_macos_icon()

    # Test PyInstaller installation
    print("Testing PyInstaller installation...")
    if not run_command(
        [sys.executable, "-m", "PyInstaller", "--version"], cwd=ROOT_DIR
    ):
        print("ERROR: PyInstaller not working properly")
        return False

    # Generate spec file
    print("Generating PyInstaller spec file...")
    spec_content = generate_pyinstaller_spec()
    spec_file = ROOT_DIR / f"{APP_NAME}.spec"

    with open(spec_file, "w") as f:
        f.write(spec_content)
    print(f"SUCCESS: Generated spec file: {spec_file}")

    # Run PyInstaller
    print("Starting PyInstaller build...")
    start_time = time.time()

    cmd = [sys.executable, "-m", "PyInstaller", "--log-level=INFO", str(spec_file)]
    success = run_command(cmd, cwd=ROOT_DIR, timeout=1200)  # 20 minutes timeout

    build_time = time.time() - start_time
    print(f"Build took {build_time:.1f} seconds")

    if success:
        print("SUCCESS: PyInstaller build completed successfully")

        # Verify output and report sizes
        if IS_MACOS:
            app_path = DIST_DIR / f"{APP_NAME}.app"
            if app_path.exists():
                size = get_directory_size(app_path)
                print(f"SUCCESS: macOS app bundle created: {app_path} ({size:.1f} MB)")

                # Verify app structure
                if verify_macos_app_structure(app_path):
                    print("SUCCESS: App bundle structure verified")
                else:
                    print("WARNING: App bundle structure issues detected")

            else:
                print("ERROR: macOS app bundle not found")
                return False
        else:
            exe_dir = DIST_DIR / APP_NAME
            if exe_dir.exists():
                size = get_directory_size(exe_dir)
                print(
                    f"SUCCESS: Application directory created: {exe_dir} ({size:.1f} MB)"
                )
            else:
                print("ERROR: Application directory not found")
                return False

    return success


def get_directory_size(path):
    """Get directory size in MB"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except:
                pass
    return total_size / (1024 * 1024)


def verify_macos_app_structure(app_path):
    """Verify macOS app bundle structure"""
    required_paths = [
        app_path / "Contents" / "Info.plist",
        app_path / "Contents" / "MacOS" / APP_NAME,
        app_path / "Contents" / "Resources",
    ]

    for path in required_paths:
        if not path.exists():
            print(f"ERROR: Required app component missing: {path}")
            return False

    return True


def generate_pyinstaller_spec():
    """Generate PyInstaller spec file with proper configuration"""
    icon_path = get_icon_for_platform()

    # Convert paths to strings for proper formatting
    root_dir_str = str(ROOT_DIR).replace("\\", "/")
    qrew_dir_str = str(ROOT_DIR / "qrew").replace("\\", "/")

    # Data files - only include files that exist
    data_files = []

    # Add qrew package assets
    qrew_assets = ROOT_DIR / "qrew" / "assets"
    if qrew_assets.exists():
        assets_str = str(qrew_assets).replace("\\", "/")
        data_files.append(f"(r'{assets_str}', 'assets')")

    # Add all qrew python files individually
    qrew_py_files = []
    qrew_dir = ROOT_DIR / "qrew"
    if qrew_dir.exists():
        for py_file in qrew_dir.glob("*.py"):
            if py_file.name != "__pycache__":
                py_file_str = str(py_file).replace("\\", "/")
                qrew_py_files.append(f"(r'{py_file_str}', 'qrew')")

    # Add documentation files
    for file_path in [ROOT_DIR / "README.md", ROOT_DIR / "LICENSE"]:
        if file_path.exists():
            file_str = str(file_path).replace("\\", "/")
            data_files.append(f"(r'{file_str}', '.')")

    data_files_str = "[" + ", ".join(data_files + qrew_py_files) + "]"

    # Hidden imports - verified against actual module structure
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
        # External
        "requests",
        "flask",
        "gevent",
        "numpy",
        "pandas",
        "vlc",
        "colour",
        # PyQt5 modules
        "PyQt5.sip",
        "PyQt5.QtCore",
        "PyQt5.QtGui",
        "PyQt5.QtWidgets",
    ]

    # Modules to exclude for smaller build size
    excludes_list = [
        "tkinter",
        "matplotlib",
        "IPython",
        "PyQt5.QtQuick",
        "PyQt5.QtQml",
        "PyQt5.QtWebSockets",
        "PyQt5.QtDBus",
        "PyQt5.QtPrintSupport",
        "test",
        "unittest",
        "pdb",
        "pydoc",
        "doctest",
        "xml.etree",
        "xml.parsers",
        "email",
        "http",
        "urllib",
        "html",
        "distutils",
        "setuptools",
        "pkg_resources",
        "wheel",
        "pip",
    ]

    # Add Linux-specific excludes
    if IS_LINUX:
        excludes_list.extend(
            [
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
                "pandas.plotting",
                "pandas.io.excel",
                "pandas.io.json",
                "pandas.io.html",
                "scipy.ndimage",
                "scipy.optimize",
                "scipy.integrate",
                "scipy.interpolate",
                "numpy.distutils",
                "numpy.f2py",
                "numpy.testing",
            ]
        )

    # Convert icon path for spec file
    icon_path_str = ""
    if icon_path:
        icon_path_str = str(icon_path).replace("\\", "/")

    # macOS bundle section
    bundle_section = ""
    if IS_MACOS:
        bundle_info = get_macos_bundle_info()
        bundle_section = f"""
app = BUNDLE(
    coll,
    name='{APP_NAME}.app',
    icon=r'{icon_path_str}' if r'{icon_path_str}' else None,
    bundle_identifier='{BUNDLE_IDENTIFIER}',
    info_plist={bundle_info}
)"""

    # Enable stripping and compression for Linux
    strip_option = "True" if IS_LINUX else "False"
    upx_option = "True" if IS_LINUX else "False"  # Enable UPX for Linux

    return f"""# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Ensure qrew package can be found
sys.path.insert(0, r'{root_dir_str}/qrew')
sys.path.insert(0, r'{root_dir_str}')

block_cipher = None


a = Analysis(
    [r'{root_dir_str}/qrew/main.py'],
    pathex=[r'{root_dir_str}', r'{qrew_dir_str}'],
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
    strip={strip_option},  # Strip debug symbols on Linux
    upx={upx_option},     # Enable UPX compression on Linux
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=r'{icon_path_str}' if r'{icon_path_str}' else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip={strip_option},  # Strip binaries
    upx={upx_option},      # Compress binaries
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
    parser.add_argument("--verify", action="store_true", help="Verify environment only")

    args = parser.parse_args()

    print("=" * 60)
    print(f"QREW BUILD SYSTEM - {PLATFORM.upper()}")
    print("=" * 60)
    print(f"Root directory: {ROOT_DIR}")
    print(f"Build directory: {BUILD_DIR}")
    print(f"Distribution directory: {DIST_DIR}")
    print(f"App version: {APP_VERSION}")

    # Check build environment
    if not check_build_environment():
        print("ERROR: Build environment check failed")
        sys.exit(1)

    # If verify only, exit here
    if args.verify:
        print("SUCCESS: Environment verification completed")
        sys.exit(0)

    # Install dependencies if requested
    if args.deps:
        print("Installing build dependencies...")
        if not install_build_dependencies():
            print("ERROR: Failed to install build dependencies")
            sys.exit(1)
        print("SUCCESS: Build dependencies installed successfully")

    # Clean build if requested
    if args.clean:
        clean_build()

    # Ensure directories exist
    ensure_directories()

    # Build with PyInstaller
    if not build_pyinstaller():
        print("ERROR: PyInstaller build failed")
        sys.exit(1)

    # Build platform-specific installer if requested
    if args.platform:
        print(f"Building {PLATFORM} platform installer...")

        if IS_MACOS:
            try:
                from build_scripts.build_macos import build_macos_installer

                if build_macos_installer():
                    print("SUCCESS: macOS installer created successfully")
                else:
                    print("ERROR: macOS installer creation failed")
                    sys.exit(1)
            except ImportError as e:
                print(f"ERROR: Could not import macOS build module: {e}")
                sys.exit(1)

        elif IS_WINDOWS:
            try:
                from build_scripts.build_windows import build_windows_installer

                if build_windows_installer():
                    print("SUCCESS: Windows installer created successfully")
                else:
                    print("ERROR: Windows installer creation failed")
                    sys.exit(1)
            except ImportError as e:
                print(f"ERROR: Could not import Windows build module: {e}")
                sys.exit(1)

        elif IS_LINUX:
            try:
                from build_scripts.build_linux import build_linux_installer

                if build_linux_installer():
                    print("SUCCESS: Linux packages created successfully")
                else:
                    print("ERROR: Linux package creation failed")
                    sys.exit(1)
            except ImportError as e:
                print(f"ERROR: Could not import Linux build module: {e}")
                sys.exit(1)

    # Print build summary
    print("\n" + "=" * 60)
    print("BUILD COMPLETED SUCCESSFULLY")
    print("=" * 60)

    if DIST_DIR.exists():
        print("Output files:")
        total_size = 0
        for item in sorted(DIST_DIR.iterdir()):
            if item.is_file():
                size_mb = item.stat().st_size / (1024 * 1024)
                total_size += size_mb
                print(f"  FILE: {item.name} ({size_mb:.1f} MB)")
            elif item.is_dir():
                size_mb = get_directory_size(item)
                total_size += size_mb
                print(f"  DIR:  {item.name}/ ({size_mb:.1f} MB)")

        print(f"\nTotal output size: {total_size:.1f} MB")

    # Platform-specific instructions
    if IS_MACOS:
        app_path = DIST_DIR / f"{APP_NAME}.app"
        if app_path.exists():
            print(f"\nmacOS app created: {app_path}")
            print(f"Test with: open '{app_path}'")
    elif IS_WINDOWS:
        exe_path = DIST_DIR / APP_NAME / f"{APP_NAME}.exe"
        if exe_path.exists():
            print(f"\nWindows executable created: {exe_path}")
            print(f"Test with: '{exe_path}'")
    elif IS_LINUX:
        exe_path = DIST_DIR / APP_NAME / APP_NAME
        if exe_path.exists():
            print(f"\nLinux executable created: {exe_path}")
            print(f"Test with: '{exe_path}'")


if __name__ == "__main__":
    main()
