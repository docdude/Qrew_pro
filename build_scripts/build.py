"""
Universal build script for Qrew
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse

# Add the project root to the Python path so we can import build_config
sys.path.insert(0, str(Path(__file__).parent.parent))
from build_scripts.build_config import *


def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, cwd=cwd, check=True, capture_output=True, text=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False


def install_build_dependencies():
    """Install build dependencies"""
    dependencies = ["pyinstaller", "wheel", "setuptools"]

    if IS_MACOS:
        dependencies.extend(["dmgbuild", "py2app"])
    elif IS_WINDOWS:
        dependencies.extend(["nsis", "pywin32"])
    elif IS_LINUX:
        dependencies.extend(["python3-distutils"])

    cmd = [sys.executable, "-m", "pip", "install"] + dependencies
    return run_command(cmd)


def clean_build():
    """Clean previous build directories"""
    print("Cleaning previous builds...")
    for path in [BUILD_DIR, DIST_DIR]:
        if path.exists():
            shutil.rmtree(path)
    ensure_directories()


def build_pyinstaller():
    """Build with PyInstaller"""
    print("Building with PyInstaller...")
    spec_content = generate_pyinstaller_spec()
    spec_file = ROOT_DIR / f"{APP_NAME}.spec"

    with open(spec_file, "w") as f:
        f.write(spec_content)

    # Run PyInstaller from the project root directory
    cmd = ["pyinstaller", str(spec_file)]
    return run_command(cmd, cwd=ROOT_DIR)


def generate_pyinstaller_spec():
    icon_path = get_icon_for_platform()
    macos_bundle_info = get_macos_bundle_info() if IS_MACOS else {}
    
    return f"""# -*- mode: python ; coding: utf-8 -*-\n\nblock_cipher = None\n\na = Analysis(\n    ['qrew/main.py'],\n    pathex=['{ROOT_DIR}'],\n    binaries=[],\n    datas={DATA_FILES},\n    hiddenimports={HIDDEN_IMPORTS},\n    hookspath=[],\n    hooksconfig={{}},\n    runtime_hooks=[],\n    excludes=[],\n    win_no_prefer_redirects=False,\n    win_private_assemblies=False,\n    cipher=block_cipher,\n    noarchive=False,\n)\n\npyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)\n\nexe = EXE(\n    pyz,\n    a.scripts,\n    [],\n    exclude_binaries=True,\n    name='{APP_NAME}',\n    debug=False,\n    bootloader_ignore_signals=False,\n    strip=False,\n    upx=True,\n    console=False,\n    disable_windowed_traceback=False,\n    argv_emulation=False,\n    target_arch=None,\n    codesign_identity=None,\n    entitlements_file=None,\n    icon='{icon_path}',\n)\n\ncoll = COLLECT(\n    exe,\n    a.binaries,\n    a.zipfiles,\n    a.datas,\n    strip=False,\n    upx=True,\n    upx_exclude=[],\n    name='{APP_NAME}',\n)\n\n{('app = BUNDLE(coll, name="' + APP_NAME + '.app", icon="' + icon_path + '", bundle_identifier="' + BUNDLE_IDENTIFIER + '", info_plist=' + str(macos_bundle_info) + ')' if IS_MACOS else '')}\n"""


block_cipher = None

a = Analysis(
    ['qrew/main.py'],  # Fixed: Correct path relative to project root
    pathex=['{ROOT_DIR}'],
    binaries=[],
    datas={DATA_FILES},
    hiddenimports={HIDDEN_IMPORTS},
    hookspath=[],
    hooksconfig={{}},
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
    name='{APP_NAME}',
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
    icon='{icon_path}',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{APP_NAME}',
)

{('app = BUNDLE(coll, name="' + APP_NAME + '.app", icon="' + icon_path + '", bundle_identifier="com.yourcompany.qrew")' if IS_MACOS else '')}
"""


def main():
    parser = argparse.ArgumentParser(description="Build Qrew installers")
    parser.add_argument("--clean", action="store_true", help="Clean before building")
    parser.add_argument(
        "--deps", action="store_true", help="Install build dependencies"
    )
    parser.add_argument(
        "--platform", action="store_true", help="Build platform-specific installer"
    )

    args = parser.parse_args()

    if args.deps:
        print("Installing build dependencies...")
        if not install_build_dependencies():
            sys.exit(1)

    if args.clean:
        clean_build()

    ensure_directories()

    print(f"Building for {PLATFORM}...")
    if not build_pyinstaller():
        sys.exit(1)

    if args.platform:
        if IS_MACOS:
            from build_macos import build_macos_installer

            build_macos_installer()
        elif IS_WINDOWS:
            from build_windows import build_windows_installer

            build_windows_installer()
        elif IS_LINUX:
            from build_linux import build_linux_installer

            build_linux_installer()


if __name__ == "__main__":
    main()
