#!/usr/bin/env python3
"""
Generate PyInstaller spec file for Qrew with cross-compilation support
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from build_scripts.build_config import *
    from build_scripts.vlc_pyinstaller_helper import (
        get_vlc_libraries,
        get_runtime_hooks,
    )
except ImportError as e:
    print(f"ERROR: {e}")
    sys.exit(1)


def get_icon_for_platform():
    """Get platform-specific icon path"""
    return ICON_PATHS.get(PLATFORM)


def generate_spec_file(onefile=False):
    """Generate PyInstaller spec file with proper configuration"""
    icon_path = get_icon_for_platform()

    # Convert paths to strings for proper formatting
    root_dir_str = str(ROOT_DIR).replace("\\", "/")
    qrew_dir_str = str(ROOT_DIR / "qrew").replace("\\", "/")

    # Essential data files only
    data_files = []
    for pattern, target_dir in ESSENTIAL_DATA_FILES:
        data_files.append(f"('{pattern}', '{target_dir}')")

    data_files_str = "[" + ", ".join(data_files) + "]"

    # Hidden imports and exclusions
    hidden_imports = HIDDEN_IMPORTS
    excludes_list = EXCLUDES

    # Convert icon path for spec file
    icon_path_str = ""
    if icon_path:
        icon_path_str = str(icon_path).replace("\\", "/")

    # Get VLC binaries
    vlc_binaries = get_vlc_libraries()
    vlc_hook = get_runtime_hooks()
    vlc_hook_str = vlc_hook.as_posix()
    vlc_binaries_str = repr(vlc_binaries)

    # Target architecture handling
    target_arch_str = "None"
    if IS_MACOS:
        arch = os.getenv("MACOS_BUILD_ARCH", "native")
        if arch != "native":
            target_arch_str = f"'{arch}'"
            print(f"Setting target architecture to {arch} in spec file")

    # macOS-specific options
    macos_options = ""
    if IS_MACOS:
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
    upx=True,
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
    """Generate spec file"""
    import argparse

    parser = argparse.ArgumentParser(description="Generate PyInstaller spec file")
    parser.add_argument(
        "--onefile", action="store_true", help="Generate for single file mode"
    )
    args = parser.parse_args()

    spec_content = generate_spec_file(onefile=args.onefile)
    spec_file = ROOT_DIR / f"{APP_NAME}.spec"

    with open(spec_file, "w") as f:
        f.write(spec_content)

    print(f"SUCCESS:Generated spec file: {spec_file}")

    # Display target architecture if set
    if IS_MACOS:
        arch = os.getenv("MACOS_BUILD_ARCH", "native")
        if arch != "native":
            print(f"SUCCESS: Spec file configured for target architecture: {arch}")


if __name__ == "__main__":
    main()
