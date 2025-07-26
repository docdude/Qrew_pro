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
        # Don't use text=True to avoid encoding issues
        result = subprocess.run(
            cmd, cwd=cwd, check=True, capture_output=True, timeout=timeout
        )
        # Handle stdout and stderr decoding with error handling
        try:
            stdout = result.stdout.decode("utf-8")
        except UnicodeDecodeError:
            try:
                # Fallback to 'ignore' error handler if utf-8 fails
                stdout = result.stdout.decode("utf-8", errors="ignore")
            except:
                stdout = str(result.stdout)

        try:
            stderr = result.stderr.decode("utf-8")
        except UnicodeDecodeError:
            try:
                stderr = result.stderr.decode("utf-8", errors="ignore")
            except:
                stderr = str(result.stderr)

        if stdout:
            print("STDOUT:", stdout)
        if stderr:
            print("STDERR:", stderr)
        return True
    except subprocess.TimeoutExpired:
        print(f"ERROR: Command timed out after {timeout} seconds")
        return False
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        # Handle stdout and stderr with same error handling
        try:
            stdout = e.stdout.decode("utf-8", errors="ignore") if e.stdout else ""
            stderr = e.stderr.decode("utf-8", errors="ignore") if e.stderr else ""
        except:
            stdout = str(e.stdout)
            stderr = str(e.stderr)

        if stdout:
            print(f"STDOUT: {stdout}")
        if stderr:
            print(f"STDERR: {stderr}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return False


def ensure_directories():
    """Ensure necessary directories exist"""
    # Create build and dist directories if they don't exist
    for dir_path in [BUILD_DIR, DIST_DIR]:
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {dir_path}")


def get_icon_for_platform():
    """Get platform-specific icon path"""
    return ICON_PATHS.get(PLATFORM)


def get_macos_bundle_info():
    """Get macOS bundle info dictionary"""
    info = MACOS_BUNDLE_INFO
    return info


def install_build_dependencies():
    """Install build dependencies based on platform"""
    print("Installing build dependencies...")

    dependencies = ["pyinstaller>=5.0", "wheel", "setuptools>=60.0", "Pillow>=8.0"]

    if IS_MACOS:
        dependencies.extend(["dmgbuild>=1.5.0"])
    elif IS_WINDOWS:
        dependencies.extend(["pywin32>=227"])
    elif IS_LINUX:
        dependencies.extend(["python3-distutils", "staticx"])

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

    # Check build architecture for macOS
    if IS_MACOS:
        arch = os.getenv("MACOS_BUILD_ARCH", "native")
        print(f"macOS build architecture: {arch}")

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


def ensure_icon_exists():
    """Ensure icons exist for all platforms"""
    success = True

    # Check each platform's icon
    for platform, icon_path in ICON_PATHS.items():
        if icon_path and icon_path.exists():
            print(f"✓ Found {platform} icon: {icon_path}")
        else:
            print(f"✗ Missing {platform} icon: {icon_path}")
            success = False

    # Special handling for macOS
    if IS_MACOS:
        success = ensure_macos_icon() and success

    return success


def ensure_macos_icon():
    """Ensure macOS icon exists and is in correct format"""
    if not IS_MACOS:
        return True

    icns_path = ICONS_DIR / "Qrew.icns"

    # If ICNS already exists, we're good
    if icns_path.exists():
        print(f"SUCCESS: Found existing ICNS: {icns_path}")
        return True

    # Try to create from PNG
    png_path = ICONS_DIR / "Qrew_desktop_500x500.png"
    if png_path.exists():
        print(f"Creating ICNS from {png_path}")
        return create_icns_from_png(png_path, icns_path)

    print("WARNING: No suitable icon found for macOS")
    return False


def create_icns_from_png(png_path, icns_path):
    """Create ICNS file from PNG"""
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

        # Clean up iconset
        shutil.rmtree(iconset_path)

        print(f"SUCCESS: Created ICNS from PNG: {icns_path}")
        return True

    except ImportError:
        print("ERROR: Pillow not installed, cannot convert PNG to ICNS")
        return False
    except Exception as e:
        print(f"ERROR: Failed to create ICNS: {e}")
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
        # Removed unused import to avoid redefinition and compilation errors

        print("SUCCESS: Main module import successful")
        return True
    except ImportError as e:
        print(f"ERROR: Cannot import main module: {e}")
        print("This may indicate missing dependencies or incorrect project structure")
        return False


def build_pyinstaller(onefile=False):
    """Build application using PyInstaller"""
    print(f"Building with PyInstaller ({'onefile' if onefile else 'onedir'} mode)...")

    # Check Python environment
    if not check_python_environment():
        return False

    # Ensure icons exist
    if not ensure_icon_exists():
        print("WARNING: Some icons missing, build may have icon issues")

    # Generate spec file
    print("Generating PyInstaller spec file...")
    spec_content = generate_pyinstaller_spec(onefile=onefile)
    spec_file = ROOT_DIR / f"{APP_NAME}.spec"

    with open(spec_file, "w") as f:
        f.write(spec_content)
    print(f"SUCCESS: Generated spec file: {spec_file}")

    # Run PyInstaller
    print("Starting PyInstaller build...")
    start_time = time.time()

    # Using spec file directly (don't add --target-arch flag)
    cmd = [sys.executable, "-m", "PyInstaller", "--log-level=INFO", str(spec_file)]

    # Note: For macOS cross-compilation, the target architecture is already
    # included in the spec file so we don't need to pass it as a command-line parameter
    arch = os.getenv("MACOS_BUILD_ARCH", "native")
    if IS_MACOS and arch != "native":
        print(f"Building for macOS {arch} architecture (specified in spec file)")

    success = run_command(cmd, cwd=ROOT_DIR, timeout=1200)  # 20 minutes timeout

    build_time = time.time() - start_time
    print(f"Build took {build_time:.1f} seconds")

    if success:
        print("SUCCESS: PyInstaller build completed successfully")
        return verify_build_output(onefile)

    return False


def verify_build_output(onefile=False):
    """Verify PyInstaller output"""
    if IS_MACOS:
        if onefile:
            app_path = DIST_DIR / APP_NAME
            if app_path.exists():
                print(f"SUCCESS: macOS executable created: {app_path}")
                return True
        else:
            app_path = DIST_DIR / f"{APP_NAME}.app"
            if app_path.exists() and verify_macos_app_structure(app_path):
                size = get_directory_size(app_path)
                print(f"SUCCESS: macOS app bundle created: {app_path} ({size:.1f} MB)")
                return True
    else:
        if onefile:
            exe_name = f"{APP_NAME}.exe" if IS_WINDOWS else APP_NAME
            exe_path = DIST_DIR / exe_name
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"SUCCESS: Executable created: {exe_path} ({size_mb:.1f} MB)")
                return True
        else:
            exe_dir = DIST_DIR / APP_NAME
            if exe_dir.exists():
                size = get_directory_size(exe_dir)
                print(
                    f"SUCCESS: Application directory created: {exe_dir} ({size:.1f} MB)"
                )
                return True

    print("ERROR: Expected output not found")
    return False


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

    # Verify icon
    icon_path = app_path / "Contents" / "Resources" / "Qrew.icns"
    if not icon_path.exists():
        print("WARNING: App icon missing")

    return True


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


def generate_pyinstaller_spec(onefile=False):
    """Generate PyInstaller spec file with proper configuration"""
    icon_path = get_icon_for_platform()

    # Convert paths to strings for proper formatting
    root_dir_str = str(ROOT_DIR).replace("\\", "/")
    qrew_dir_str = str(ROOT_DIR / "qrew").replace("\\", "/")

    # Essential data files only - no source code
    data_files = []

    # Use ESSENTIAL_DATA_FILES from build_config.py
    print(f"Adding {len(ESSENTIAL_DATA_FILES)} essential data file patterns")

<<<<<<< HEAD
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
        #   "email",
        #  "http",
        # "urllib",
        # "html",
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
                #    "pandas.plotting",
                #   "pandas.io.excel",
                #  "pandas.io.json",
                # "pandas.io.html",
                "numpy.distutils",
                "numpy.f2py",
                "numpy.testing",
            ]
        )
=======
    for pattern, target_dir in ESSENTIAL_DATA_FILES:
        base_path = ROOT_DIR
        glob_pattern = pattern.split("/")[-1]
        dir_parts = pattern.split("/")[:-1]

        for part in dir_parts:
            base_path = base_path / part

        if "*" in glob_pattern:
            # Handle glob pattern
            if base_path.exists():
                for file_path in base_path.glob(glob_pattern):
                    if file_path.exists():
                        file_str = str(file_path).replace("\\", "/")
                        data_files.append(f"(r'{file_str}', '{target_dir}')")
        else:
            # Handle specific file
            file_path = base_path / glob_pattern
            if file_path.exists():
                file_str = str(file_path).replace("\\", "/")

                # For settings.json, add it to the root AND the qrew subdirectory for full compatibility
                if glob_pattern == "settings.json":
                    data_files.append(f"(r'{file_str}', '.')")  # Root directory
                    data_files.append(f"(r'{file_str}', 'qrew')")  # qrew subdirectory
                    print(
                        f"Added essential file (three locations): {file_path} -> root, qrew, and {target_dir}"
                    )

                # Always add to the target directory too
                data_files.append(f"(r'{file_str}', '{target_dir}')")

                if glob_pattern != "settings.json":
                    print(f"Added essential file: {file_path} -> {target_dir}")
            else:
                print(f"WARNING: Essential file not found: {file_path}")
>>>>>>> 80fd89d1b487b52d9852eea9661d354a15efab56

    data_files_str = "[" + ", ".join(data_files) + "]"

    # 🔧 FIX: Use HIDDEN_IMPORTS from build_config.py instead of hardcoded list
    hidden_imports = HIDDEN_IMPORTS

    # 🔧 FIX: Use EXCLUDES from build_config.py instead of hardcoded list
    excludes_list = EXCLUDES

    print(f"Using {len(excludes_list)} exclusions from build_config.py")
    print(f"Scipy exclusions included: {any('scipy' in ex for ex in excludes_list)}")
    # Convert icon path for spec file
    icon_path_str = ""
    if icon_path:
        icon_path_str = str(icon_path).replace("\\", "/")

    # Get VLC binaries
    from build_scripts.vlc_pyinstaller_helper import (
        get_vlc_libraries,
        get_runtime_hooks,
    )

    vlc_binaries = get_vlc_libraries()
    vlc_hook = get_runtime_hooks()
    vlc_hook_str = vlc_hook.as_posix()
    vlc_binaries_str = repr(vlc_binaries)

    # macOS-specific options
    macos_options = ""
    target_arch_str = "None"

    # Get target architecture for macOS builds
    if IS_MACOS:
        arch = os.getenv("MACOS_BUILD_ARCH", "native")
        if arch != "native":
            target_arch_str = f"'{arch}'"  # For spec file

        # Bundle info for macOS app
        bundle_info = get_macos_bundle_info()
        if not onefile:
            macos_options = f"""
app = BUNDLE(
    exe,
    name='{APP_NAME}.app',
    icon=r'{icon_path_str}' if r'{icon_path_str}' else None,
    bundle_identifier='{BUNDLE_IDENTIFIER}',
    info_plist={bundle_info}
)"""

    # Build mode specific options
    if onefile:
        exe_section = f"""
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip={str(IS_LINUX).capitalize()},
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch={target_arch_str},
    codesign_identity=None,
    entitlements_file=None,
    icon=r'{icon_path_str}' if r'{icon_path_str}' else None,
)"""
    else:
        exe_section = f"""
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip={str(IS_LINUX).capitalize()},
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch={target_arch_str},
    codesign_identity=None,
    entitlements_file=None,
    icon=r'{icon_path_str}' if r'{icon_path_str}' else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip={str(IS_LINUX).capitalize()},
    upx=True,
    upx_exclude=[],
    name='{APP_NAME}',
)"""

    # Add VLC libraries and hook
    from build_scripts.vlc_pyinstaller_helper import (
        get_vlc_libraries,
        get_runtime_hooks,
    )

    vlc_binaries = get_vlc_libraries()
    vlc_hook = get_runtime_hooks()
    vlc_hook_str = vlc_hook.as_posix()
    # Add these to the spec file
    vlc_binaries_str = repr(vlc_binaries)

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
    binaries={vlc_binaries_str},
    datas={data_files_str},
    hiddenimports={hidden_imports},
    excludes={excludes_list},
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=['{vlc_hook_str}'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
{exe_section}{macos_options}
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
    parser.add_argument(
        "--onefile", action="store_true", help="Build single executable file"
    )

    args = parser.parse_args()

    print("=" * 60)
    print(f"QREW BUILD SYSTEM - {PLATFORM.upper()}")
    print("=" * 60)
    print(f"Root directory: {ROOT_DIR}")
    print(f"Build directory: {BUILD_DIR}")
    print(f"Distribution directory: {DIST_DIR}")
    print(f"App version: {APP_VERSION}")
    print(f"Build mode: {'onefile' if args.onefile else 'onedir'}")

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
    if not build_pyinstaller(onefile=args.onefile):
        print("ERROR: PyInstaller build failed")
        sys.exit(1)

    # Build platform-specific installer if requested
    if args.platform:
        print(f"Building {PLATFORM} platform installer...")

        if IS_MACOS:
            try:
                from build_scripts.build_macos import build_macos_installer

                if build_macos_installer(onefile=args.onefile):
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

                if build_windows_installer(onefile=args.onefile):
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

                if build_linux_installer(onefile=args.onefile):
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


if __name__ == "__main__":
    main()
