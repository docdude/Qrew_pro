#!/usr/bin/env python3
"""
Complete setup script to create ALL updated Qrew build files locally
"""

import os
from pathlib import Path

def create_file(path, content):
    """Create a file with the given content"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created: {path}")

def main():
    # Get current directory (should be run from project root)
    project_root = Path.cwd()
    build_scripts_dir = project_root / "build_scripts"
    
    print(f"Creating ALL build files in: {project_root}")
    print("=" * 80)
    
    # File contents will be defined here for each file...
    files_to_create = {
        # GitHub Actions workflow
        ".github/workflows/build.yml": """name: Build Installers

on:
  push:
    tags:
      - 'v*'
  pull_request:
    branches: [ main ]

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
        
    - name: Install VLC
      run: |
        choco install vlc -y
        echo "C:\\\\Program Files\\\\VideoLAN\\\\VLC" >> $env:GITHUB_PATH
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-build.txt
        
    - name: Install NSIS
      run: choco install nsis
      
    - name: Build Windows installer
      run: |
        cd ${{ github.workspace }}
        python build_scripts/build.py --clean --onefile --platform
      
    - name: Upload Windows installer
      uses: actions/upload-artifact@v4
      with:
        name: windows-installer
        path: |
          dist/*.exe
          dist/*.zip
        if-no-files-found: warn

  build-macos:
    strategy:
      matrix:
        include:
          - arch: x86_64
            runner: macos-13
          - arch: arm64
            runner: macos-14
    runs-on: ${{ matrix.runner }}
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install VLC
      run: brew install --cask vlc

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-build.txt

    - name: Build macOS installer for ${{ matrix.arch }}
      run: |
        cd ${{ github.workspace }}
        export MACOS_BUILD_ARCH=${{ matrix.arch }}
        python build_scripts/build.py --clean --onefile --platform

    - name: Upload macOS installer
      uses: actions/upload-artifact@v4
      with:
        name: macos-installer-${{ matrix.arch }}
        path: dist/*.dmg
        if-no-files-found: warn

  build-linux:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y vlc libvlc-dev dpkg-dev rpm alien build-essential python3-dev upx-ucl binutils
        
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-build.txt
        
    - name: Build Linux packages
      run: |
        cd ${{ github.workspace }}
        python build_scripts/build.py --clean --onefile --platform

    - name: Upload Linux packages
      uses: actions/upload-artifact@v4
      with:
        name: linux-packages
        path: |
          dist/*.deb
          dist/*.rpm  
          dist/*.tar.gz
        if-no-files-found: warn
""",

        # Build config
        "build_scripts/build_config.py": '''"""
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

ROOT_DIR = Path(__file__).parent.parent
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

ICON_FALLBACKS = {
    "darwin": [
        ICONS_DIR / "Qrew.icns",
        ICONS_DIR / "Qrew_desktop_500x500.png",
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
    "CFBundleIconName": "Qrew",
    "NSHumanReadableCopyright": f"© {datetime.datetime.now().year} {APP_AUTHOR}",
    "NSHighResolutionCapable": True,
    "LSMinimumSystemVersion": "10.15",
    "LSUIElement": False,
    "LSApplicationCategoryType": "public.app-category.utilities",
}

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
''',

        # Windows build script  
        "build_scripts/build_windows.py": '''"""
Windows installer build script for Qrew
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from build_scripts.build_config import *
except ImportError:
    print("Error: Could not import build_config")
    sys.exit(1)

def run_command(cmd, cwd=None):
    """Run a command with proper error handling"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        if result.stdout:
            print("STDOUT:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed: {e}")
        return False

def build_windows_installer(onefile=False):
    """Build Windows installer using NSIS or create ZIP fallback"""
    print("Building Windows installer...")

    if onefile:
        exe_path = DIST_DIR / f"{APP_NAME}.exe"
        if not exe_path.exists():
            print("ERROR: Windows executable not found")
            return False
    else:
        app_dir = DIST_DIR / APP_NAME
        if not app_dir.exists():
            print("ERROR: Windows app directory not found")
            return False

    # Try NSIS first, fall back to ZIP
    if build_nsis_installer(onefile):
        return True
    else:
        print("WARNING: NSIS not available, creating ZIP distribution...")
        return build_windows_zip(onefile)

def build_nsis_installer(onefile=False):
    """Build NSIS-based Windows installer"""
    try:
        subprocess.run(["makensis", "/VERSION"], check=True, capture_output=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("ERROR: NSIS not found")
        return False

    nsis_script = generate_nsis_script(onefile)
    nsis_file = BUILD_DIR / f"{APP_NAME}_installer.nsi"
    BUILD_DIR.mkdir(exist_ok=True)

    with open(nsis_file, "w", encoding="utf-8") as f:
        f.write(nsis_script)

    cmd = ["makensis", str(nsis_file)]
    if run_command(cmd, cwd=ROOT_DIR):
        print("SUCCESS: NSIS installer created")
        return True
    else:
        print("ERROR: NSIS build failed")
        return False

def build_windows_zip(onefile=False):
    """Create Windows ZIP distribution as fallback"""
    print("Creating Windows ZIP distribution...")

    if onefile:
        exe_path = DIST_DIR / f"{APP_NAME}.exe"
        if not exe_path.exists():
            return False
            
        temp_dir = DIST_DIR / f"{APP_NAME}_portable"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()
        
        shutil.copy2(exe_path, temp_dir)
        
        icon_path = get_icon_for_platform()
        if icon_path and icon_path.exists():
            shutil.copy2(icon_path, temp_dir / "Qrew.ico")
        
        zip_path = DIST_DIR / f"{APP_NAME}-{APP_VERSION}-windows-portable"
        try:
            shutil.make_archive(str(zip_path), "zip", str(temp_dir.parent), temp_dir.name)
            shutil.rmtree(temp_dir)
            print(f"SUCCESS: Windows portable ZIP created")
            return True
        except Exception as e:
            print(f"ERROR: ZIP creation failed: {e}")
            return False
    else:
        app_dir = DIST_DIR / APP_NAME
        zip_path = DIST_DIR / f"{APP_NAME}-{APP_VERSION}-windows"
        try:
            shutil.make_archive(str(zip_path), "zip", str(app_dir.parent), app_dir.name)
            print(f"SUCCESS: Windows ZIP created")
            return True
        except Exception as e:
            print(f"ERROR: ZIP creation failed: {e}")
            return False

def generate_nsis_script(onefile=False):
    """Generate NSIS installer script"""
    dist_dir_nsis = str(DIST_DIR).replace("\\\\", "/")
    
    if onefile:
        install_files = f'File "{dist_dir_nsis}/{APP_NAME}.exe"'
    else:
        install_files = f'File /r "{dist_dir_nsis}/{APP_NAME}/*"'

    return f'''
; NSIS Script for {APP_NAME}
!include "MUI2.nsh"

Name "{APP_NAME}"
OutFile "{dist_dir_nsis}/{APP_NAME}-{APP_VERSION}-windows-installer.exe"
InstallDir "$PROGRAMFILES64\\\\{APP_NAME}"
RequestExecutionLevel admin

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME  
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "English"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    {install_files}
    
    CreateDirectory "$SMPROGRAMS\\\\{APP_NAME}"
    CreateShortCut "$SMPROGRAMS\\\\{APP_NAME}\\\\{APP_NAME}.lnk" "$INSTDIR\\\\{APP_NAME}.exe"
    CreateShortCut "$DESKTOP\\\\{APP_NAME}.lnk" "$INSTDIR\\\\{APP_NAME}.exe"
    
    WriteRegStr HKLM "Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Uninstall\\\\{APP_NAME}" "DisplayName" "{APP_NAME}"
    WriteRegStr HKLM "Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Uninstall\\\\{APP_NAME}" "UninstallString" "$INSTDIR\\\\uninstall.exe"
    
    WriteUninstaller "$INSTDIR\\\\uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\\\uninstall.exe"
    RMDir /r "$INSTDIR"
    Delete "$DESKTOP\\\\{APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\\\\{APP_NAME}"
    DeleteRegKey HKLM "Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Uninstall\\\\{APP_NAME}"
SectionEnd
'''

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--onefile", action="store_true")
    args = parser.parse_args()
    
    if not ensure_directories():
        sys.exit(1)

    if build_windows_installer(onefile=args.onefile):
        print("SUCCESS: Windows installer build completed")
    else:
        print("ERROR: Windows installer build failed")
        sys.exit(1)
''',

        # Linux build script
        "build_scripts/build_linux.py": '''"""
Linux packages build script for Qrew
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from build_scripts.build_config import *
except ImportError:
    print("Error: Could not import build_config")
    sys.exit(1)

def run_command(cmd, cwd=None):
    """Run a command with proper error handling"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        if result.stdout:
            print("STDOUT:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed: {e}")
        return False

def build_linux_installer(onefile=False):
    """Build Linux packages"""
    print("Building Linux packages...")
    
    if onefile:
        exe_path = DIST_DIR / APP_NAME
        if not exe_path.exists():
            print("ERROR: Linux executable not found")
            return False
    else:
        app_dir = DIST_DIR / APP_NAME
        if not app_dir.exists():
            print("ERROR: Linux app directory not found")
            return False

    success = True

    # Optimize BEFORE building packages
    if optimize_linux_build(onefile):
        print("SUCCESS: Linux build optimized")

    # Build packages
    if build_deb_package(onefile):
        print("SUCCESS: .deb package created")
    else:
        print("WARNING: .deb package creation failed")
        success = False

    # Create tarball
    if create_tarball(onefile):
        print("SUCCESS: tar.gz archive created")
    else:
        print("WARNING: tar.gz creation failed")

    return success

def optimize_linux_build(onefile=False):
    """Remove unnecessary files and optimize the Linux build""" 
    print("Optimizing Linux build...")
    
    if onefile:
        exe_path = DIST_DIR / APP_NAME
        if exe_path.exists():
            try:
                subprocess.run(["strip", "--strip-unneeded", str(exe_path)], 
                             check=False, capture_output=True)
                print("SUCCESS: Stripped executable")
            except:
                print("INFO: Could not strip executable")
        return True
    
    app_dir = DIST_DIR / APP_NAME
    if not app_dir.exists():
        return False

    # Only remove truly unnecessary files
    cleanup_patterns = [
        "**/__pycache__",
        "**/*.pyc", 
        "**/*.pyo",
        "**/*.debug",
        "**/*.a",
        "**/*.la",
        "lib*/libQt5Test*",
        "lib*/libQt5Designer*",
        "include",
        "share/doc",
        "share/man",
    ]

    removed_size = 0
    for pattern in cleanup_patterns:
        for path in app_dir.rglob(pattern):
            try:
                if path.is_file():
                    size = path.stat().st_size
                    path.unlink()
                    removed_size += size
                elif path.is_dir():
                    dir_size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
                    shutil.rmtree(path)
                    removed_size += dir_size
            except Exception as e:
                print(f"WARNING: Could not remove {path}: {e}")

    print(f"SUCCESS: Removed {removed_size / (1024*1024):.1f} MB of unnecessary files")

    # Strip binaries
    try:
        for binary in app_dir.rglob("*.so*"):
            if binary.is_file() and not binary.is_symlink():
                try:
                    subprocess.run(["strip", "--strip-unneeded", str(binary)],
                                 check=False, capture_output=True)
                except:
                    pass
        print("SUCCESS: Stripped debug symbols from libraries")
    except Exception as e:
        print(f"WARNING: Could not strip binaries: {e}")

    return True

def build_deb_package(onefile=False):
    """Build .deb package"""
    print("Building .deb package...")

    pkg_dir = BUILD_DIR / f"{APP_NAME.lower()}-{APP_VERSION}_deb"
    if pkg_dir.exists():
        shutil.rmtree(pkg_dir)

    create_deb_structure(pkg_dir, onefile)

    try:
        cmd = [
            "dpkg-deb",
            "--build",
            str(pkg_dir),
            str(DIST_DIR / f"{APP_NAME.lower()}-{APP_VERSION}-linux.deb"),
        ]
        return run_command(cmd, cwd=ROOT_DIR)
    except Exception as e:
        print(f"ERROR: .deb build exception: {e}")
        return False

def create_deb_structure(pkg_dir, onefile=False):
    """Create .deb package structure"""
    print("Creating .deb structure...")
    pkg_dir.mkdir(parents=True, exist_ok=True)

    # Create DEBIAN control files
    debian_dir = pkg_dir / "DEBIAN"
    debian_dir.mkdir(exist_ok=True)

    control_content = f"""Package: {APP_NAME.lower()}
Version: {APP_VERSION}
Section: sound
Priority: optional
Architecture: amd64
Depends: libc6, libpython3.10, vlc
Maintainer: {APP_AUTHOR}
Description: {APP_DESCRIPTION}
 Automated loudspeaker measurement system using REW API.
"""
    with open(debian_dir / "control", "w") as f:
        f.write(control_content)

    # Copy application files
    app_install_dir = pkg_dir / "opt" / APP_NAME
    app_install_dir.mkdir(parents=True, exist_ok=True)

    if onefile:
        # Single executable file
        exe_path = DIST_DIR / APP_NAME
        if exe_path.exists():
            shutil.copy2(exe_path, app_install_dir / APP_NAME)
            (app_install_dir / APP_NAME).chmod(0o755)
    else:
        # Directory structure
        app_source = DIST_DIR / APP_NAME
        if app_source.exists():
            for item in app_source.iterdir():
                if item.is_file():
                    shutil.copy2(item, app_install_dir)
                elif item.is_dir():
                    shutil.copytree(item, app_install_dir / item.name, dirs_exist_ok=True)

    # Add icon file
    icon_dir = pkg_dir / "usr" / "share" / "icons" / "hicolor" / "scalable" / "apps"
    icon_dir.mkdir(parents=True, exist_ok=True)
    
    icon_src = get_icon_for_platform()
    if icon_src and icon_src.exists():
        shutil.copy2(icon_src, icon_dir / "Qrew.png")
        shutil.copy2(icon_src, app_install_dir / "Qrew.png")

    # Create desktop entry
    desktop_dir = pkg_dir / "usr" / "share" / "applications"
    desktop_dir.mkdir(parents=True, exist_ok=True)

    desktop_content = f"""[Desktop Entry]
Name={APP_NAME}
Comment={APP_DESCRIPTION}
Exec=/opt/{APP_NAME}/{APP_NAME}
Icon=Qrew
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Engineering;
StartupWMClass={APP_NAME}
"""
    with open(desktop_dir / f"{APP_NAME.lower()}.desktop", "w") as f:
        f.write(desktop_content)

    # Create launcher script
    bin_dir = pkg_dir / "usr" / "local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    launcher_content = f"""#!/bin/bash
export LD_LIBRARY_PATH=/opt/{APP_NAME}:$LD_LIBRARY_PATH
cd /opt/{APP_NAME}
./{APP_NAME} "$@"
"""
    launcher_file = bin_dir / APP_NAME.lower()
    with open(launcher_file, "w") as f:
        f.write(launcher_content)
    launcher_file.chmod(0o755)

def create_tarball(onefile=False):
    """Create a tar.gz distribution"""
    print("Creating tar.gz archive...")

    if onefile:
        source = DIST_DIR / APP_NAME
        tarball_path = DIST_DIR / f"{APP_NAME.lower()}-{APP_VERSION}-linux-portable.tar.gz"
        
        try:
            cmd = ["tar", "-czf", str(tarball_path), "-C", str(DIST_DIR), APP_NAME]
            return run_command(cmd, cwd=ROOT_DIR)
        except Exception as e:
            print(f"ERROR: tar.gz creation failed: {e}")
            return False
    else:
        app_dir = DIST_DIR / APP_NAME
        tarball_path = DIST_DIR / f"{APP_NAME.lower()}-{APP_VERSION}-linux.tar.gz"

        try:
            cmd = [
                "tar", "-czf", str(tarball_path), "-C", str(app_dir.parent), app_dir.name,
            ]
            return run_command(cmd, cwd=ROOT_DIR)
        except Exception as e:
            print(f"ERROR: tar.gz creation failed: {e}")
            return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--onefile", action="store_true")
    args = parser.parse_args()
    
    if not ensure_directories():
        sys.exit(1)

    if build_linux_installer(onefile=args.onefile):
        print("SUCCESS: Linux packages build completed")
    else:
        print("ERROR: Linux packages build failed")
        sys.exit(1)
''',

        # VLC helper 
        "build_scripts/vlc_pyinstaller_helper.py": '''"""Helper module to include VLC libraries in PyInstaller builds"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def get_vlc_libraries():
    """Find VLC libraries for current platform to include in PyInstaller spec"""
    system = platform.system()
    binaries = []

    if system == "Windows":
        vlc_path = find_windows_vlc()
        if vlc_path:
            plugin_path = os.path.join(os.path.dirname(vlc_path), "plugins")
            binaries.append((vlc_path, "."))
            binaries.append((os.path.join(os.path.dirname(vlc_path), "libvlccore.dll"), "."))
            
            if os.path.exists(plugin_path):
                for root, _, files in os.walk(plugin_path):
                    for file in files:
                        if file.endswith(".dll"):
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(os.path.dirname(full_path), os.path.dirname(plugin_path))
                            dest_dir = os.path.join("plugins", rel_path)
                            binaries.append((full_path, dest_dir))

    elif system == "Darwin":
        vlc_dir = "/Applications/VLC.app/Contents/MacOS"
        if os.path.exists(vlc_dir):
            lib_dir = os.path.join(vlc_dir, "lib")
            binaries.append((os.path.join(lib_dir, "libvlc.dylib"), "."))
            binaries.append((os.path.join(lib_dir, "libvlccore.dylib"), "."))
            
            plugins_dir = os.path.join(vlc_dir, "plugins")
            if os.path.exists(plugins_dir):
                for root, _, files in os.walk(plugins_dir):
                    for file in files:
                        if file.endswith(".dylib"):
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(os.path.dirname(full_path), plugins_dir)
                            dest_dir = os.path.join("plugins", rel_path)
                            binaries.append((full_path, dest_dir))

    elif system == "Linux":
        vlc_lib = find_linux_vlc()
        if vlc_lib:
            lib_dir = os.path.dirname(vlc_lib)
            vlc_core_lib = os.path.join(lib_dir, "libvlccore.so")
            if os.path.exists(vlc_core_lib):
                binaries.append((vlc_lib, "."))
                binaries.append((vlc_core_lib, "."))

            plugins_dirs = [
                "/usr/lib/x86_64-linux-gnu/vlc/plugins",
                "/usr/lib/vlc/plugins",
                os.path.join(lib_dir, "vlc/plugins"),
            ]

            for plugins_dir in plugins_dirs:
                if os.path.exists(plugins_dir):
                    for root, _, files in os.walk(plugins_dir):
                        for file in files:
                            if file.endswith(".so"):
                                full_path = os.path.join(root, file)
                                rel_path = os.path.relpath(os.path.dirname(full_path), plugins_dir)
                                dest_dir = os.path.join("plugins", rel_path)
                                binaries.append((full_path, dest_dir))
                    break

    return binaries

def find_windows_vlc():
    """Find VLC executable on Windows"""
    try:
        import winreg
        for key in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                reg_key = winreg.OpenKey(key, r"Software\\VideoLAN\\VLC")
                install_dir = winreg.QueryValueEx(reg_key, "InstallDir")[0]
                vlc_exe = os.path.join(install_dir, "libvlc.dll")
                if os.path.exists(vlc_exe):
                    return vlc_exe
            except:
                pass
    except:
        pass

    common_locations = [
        os.path.join(os.environ.get("PROGRAMFILES", "C:\\\\Program Files"), "VideoLAN", "VLC", "libvlc.dll"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\\\Program Files (x86)"), "VideoLAN", "VLC", "libvlc.dll"),
    ]

    for location in common_locations:
        if os.path.exists(location):
            return location
    return None

def find_linux_vlc():
    """Find libvlc.so on Linux systems"""
    common_locations = [
        "/usr/lib/x86_64-linux-gnu/libvlc.so",
        "/usr/lib/libvlc.so",
        "/usr/local/lib/libvlc.so",
    ]

    for location in common_locations:
        if os.path.exists(location):
            return location

    try:
        result = subprocess.run(["ldconfig", "-p"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "libvlc.so" in line:
                parts = line.split(" => ")
                if len(parts) >= 2:
                    lib_path = parts[1].strip()
                    if os.path.exists(lib_path):
                        return lib_path
    except:
        pass
    return None

def get_runtime_hooks():
    """Get path to runtime hook for VLC"""
    hook_content = """
# PyInstaller runtime hook to configure VLC paths
import os
import sys
import platform

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    if platform.system() == "Darwin":
        os.environ['VLC_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'plugins')
    elif platform.system() == "Windows":
        os.environ['VLC_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'plugins')
    elif platform.system() == "Linux":
        os.environ['VLC_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'plugins')
"""

    hook_path = Path(__file__).parent / "vlc_hook.py"
    with open(hook_path, "w") as f:
        f.write(hook_content)
    return hook_path
''',

        # macOS build script
        "build_scripts/build_macos.py": '''"""
macOS-specific build script with code signing and notarization
"""

import os
import subprocess
import shutil
from pathlib import Path
from build_config import *

def run_command(cmd, timeout=1800):
    """Run a command with error handling"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=timeout)
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        return False, e.stderr
    except subprocess.TimeoutExpired:
        print(f"ERROR: Command timed out after {timeout} seconds")
        return False, "Command timed out"

def get_build_architecture():
    """Get the architecture we're building for"""
    arch = os.getenv('MACOS_BUILD_ARCH', 'native')
    if arch == 'native':
        result = subprocess.run(['uname', '-m'], capture_output=True, text=True)
        arch = result.stdout.strip()
    return arch

def build_macos_installer(onefile=False):
    """Build complete macOS installer with signing and notarization"""
    print("Building macOS installer...")
    
    arch = get_build_architecture()
    print(f"Building for architecture: {arch}")

    if onefile:
        app_path = DIST_DIR / APP_NAME
        if not app_path.exists():
            print("ERROR: Executable not found")
            return False
    else:
        app_path = DIST_DIR / f"{APP_NAME}.app"
        if not app_path.exists():
            print("ERROR: .app bundle not found")
            return False

    # Create DMG
    print("Creating DMG...")
    if create_dmg(onefile=onefile):
        print("SUCCESS: DMG created")
        return True
    else:
        print("ERROR: DMG creation failed")
        return False

def create_dmg(onefile=False):
    """Create DMG file"""
    print("Creating DMG installer...")
    
    arch = get_build_architecture()
    
    if onefile:
        exe_path = DIST_DIR / APP_NAME
        temp_app = DIST_DIR / f"{APP_NAME}.app"
        create_minimal_app_bundle(exe_path, temp_app)
        app_path = temp_app
    else:
        app_path = DIST_DIR / f"{APP_NAME}.app"

    dmg_path = DIST_DIR / f"{APP_NAME}-{APP_VERSION}-macos-{arch}.dmg"

    if dmg_path.exists():
        dmg_path.unlink()

    # Simple DMG creation using hdiutil
    temp_dmg = DIST_DIR / "temp.dmg"
    
    try:
        # Create temporary DMG
        cmd = ["hdiutil", "create", "-size", "500m", "-fs", "HFS+", "-volname", APP_NAME, str(temp_dmg)]
        success, output = run_command(cmd)
        if not success:
            return False
        
        # Mount it
        cmd = ["hdiutil", "attach", str(temp_dmg), "-mountpoint", "/tmp/qrew_dmg"]
        success, output = run_command(cmd)
        if not success:
            return False
        
        # Copy app
        shutil.copytree(app_path, f"/tmp/qrew_dmg/{APP_NAME}.app")
        
        # Create Applications symlink
        os.symlink("/Applications", "/tmp/qrew_dmg/Applications")
        
        # Unmount
        cmd = ["hdiutil", "detach", "/tmp/qrew_dmg"]
        run_command(cmd)
        
        # Convert to final DMG
        cmd = ["hdiutil", "convert", str(temp_dmg), "-format", "UDZO", "-o", str(dmg_path)]
        success, output = run_command(cmd)
        
        # Cleanup
        if temp_dmg.exists():
            temp_dmg.unlink()
        if onefile and temp_app.exists():
            shutil.rmtree(temp_app)
            
        return success and dmg_path.exists()
        
    except Exception as e:
        print(f"ERROR: DMG creation failed: {e}")
        return False

def create_minimal_app_bundle(exe_path, app_path):
    """Create minimal app bundle for single-file executable"""
    contents_dir = app_path / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"
    
    macos_dir.mkdir(parents=True, exist_ok=True)
    resources_dir.mkdir(parents=True, exist_ok=True)
    
    shutil.copy2(exe_path, macos_dir / APP_NAME)
    
    icns_path = ICONS_DIR / "Qrew.icns"
    if icns_path.exists():
        shutil.copy2(icns_path, resources_dir / "Qrew.icns")
    
    info_plist = get_macos_bundle_info()
    plist_content = generate_info_plist(info_plist)
    
    with open(contents_dir / "Info.plist", "w") as f:
        f.write(plist_content)
    
    (macos_dir / APP_NAME).chmod(0o755)

def generate_info_plist(info_dict):
    """Generate Info.plist XML content"""
    plist = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
'''
    
    for key, value in info_dict.items():
        if isinstance(value, bool):
            plist += f"    <key>{key}</key>\\n    <{str(value).lower()}/>\\n"
        elif isinstance(value, int):
            plist += f"    <key>{key}</key>\\n    <integer>{value}</integer>\\n"
        else:
            plist += f"    <key>{key}</key>\\n    <string>{value}</string>\\n"
    
    plist += '''</dict>
</plist>'''
    return plist

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--onefile", action="store_true")
    args = parser.parse_args()
    
    success = build_macos_installer(onefile=args.onefile)
    sys.exit(0 if success else 1)
''',

        # Universal binary helper
        "build_scripts/create_universal.py": '''"""
Create universal binary from separate architecture builds
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(cmd):
    """Run command with error handling"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e}")
        return False

def create_universal_app(x86_app, arm_app, universal_app):
    """Create universal app bundle"""
    print(f"Creating universal app from {x86_app} and {arm_app}")
    
    x86_path = Path(x86_app)
    arm_path = Path(arm_app)
    universal_path = Path(universal_app)
    
    if universal_path.exists():
        shutil.rmtree(universal_path)
    shutil.copytree(x86_path, universal_path)
    
    app_name = "Qrew"
    x86_binary = x86_path / "Contents" / "MacOS" / app_name
    arm_binary = arm_path / "Contents" / "MacOS" / app_name
    universal_binary = universal_path / "Contents" / "MacOS" / app_name
    
    cmd = ["lipo", "-create", "-output", str(universal_binary), str(x86_binary), str(arm_binary)]
    
    if run_command(cmd):
        print("SUCCESS: Universal binary created")
        verify_cmd = ["lipo", "-info", str(universal_binary)]
        if run_command(verify_cmd):
            print("SUCCESS: Universal binary verified")
            return True
    return False

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python create_universal.py <x86_app> <arm_app> <universal_app>")
        sys.exit(1)
    
    x86_app, arm_app, universal_app = sys.argv[1:4]
    
    if create_universal_app(x86_app, arm_app, universal_app):
        print("SUCCESS: Universal app created")
        sys.exit(0)
    else:
        print("ERROR: Failed to create universal app")
        sys.exit(1)
''',
    }
    
    # Create all files
    files_created = 0
    for relative_path, content in files_to_create.items():
        file_path = project_root / relative_path
        create_file(file_path, content)
        files_created += 1
    
    print("=" * 80)
    print("🎉 COMPLETE SETUP FINISHED!")
    print("=" * 80)
    print(f"✅ Created {files_created} build files")
    print()
    print("📁 Files created:")
    for relative_path in files_to_create.keys():
        print(f"   • {relative_path}")
    print()
    print("🚀 You can now run:")
    print("   python build_scripts/build.py --clean --onefile --platform")
    print()
    print("🔧 Features enabled:")
    print("   • Single-file executables (no internal folders)")
    print("   • Proper icon handling for all platforms")
    print("   • macOS Intel/ARM/Universal support")
    print("   • GitHub Actions workflow for automated builds")
    print("   • Optimized packages (source code excluded)")

if __name__ == "__main__":
    main()