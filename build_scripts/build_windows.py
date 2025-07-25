"""
Windows installer build script for Qrew
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from build_scripts.build_config import *
except ImportError:
    print(
        "Error: Could not import build_config. Make sure build_scripts/build_config.py exists."
    )
    sys.exit(1)


def run_command(cmd, cwd=None):
    """Run a command with proper error handling"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd, cwd=cwd, check=True, capture_output=True, text=True
        )
        if result.stdout:
            print("STDOUT:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def build_windows_installer(onefile=False):
    """Build Windows installer using NSIS or create ZIP fallback"""
    print("Building Windows installer...")

    if onefile:
        exe_path = DIST_DIR / f"{APP_NAME}.exe"
        if not exe_path.exists():
            print("ERROR: Windows executable not found. Run PyInstaller first.")
            return False
    else:
        app_dir = DIST_DIR / APP_NAME
        if not app_dir.exists():
            print("ERROR: Windows app directory not found. Run PyInstaller first.")
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
        # Check if NSIS is available
        subprocess.run(["makensis", "/VERSION"], check=True, capture_output=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("ERROR: NSIS not found")
        return False

    nsis_script = generate_nsis_script(onefile)
    nsis_file = BUILD_DIR / f"{APP_NAME}_installer.nsi"

    # Ensure build directory exists
    BUILD_DIR.mkdir(exist_ok=True)

    with open(nsis_file, "w", encoding="utf-8") as f:
        f.write(nsis_script)

    print(f"SUCCESS: Generated NSIS script: {nsis_file}")

    cmd = ["makensis", str(nsis_file)]
    if run_command(cmd, cwd=ROOT_DIR):
        print("SUCCESS: NSIS installer created successfully")
        return True
    else:
        print("ERROR: NSIS build failed")
        return False


def build_windows_zip(onefile=False):
    """Create Windows ZIP distribution as fallback"""
    print("Creating Windows ZIP distribution...")

    if onefile:
        # Single executable
        exe_path = DIST_DIR / f"{APP_NAME}.exe"
        if not exe_path.exists():
            print("ERROR: Executable not found")
            return False

        # Create a temp directory with the exe and icon
        temp_dir = DIST_DIR / f"{APP_NAME}_portable"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir()

        # Copy exe
        shutil.copy2(exe_path, temp_dir)

        # Copy icon if exists
        icon_path = get_icon_for_platform()
        if icon_path and icon_path.exists():
            shutil.copy2(icon_path, temp_dir / "Qrew.ico")

        # Create README
        readme_content = f"""
{APP_NAME} v{APP_VERSION} - Portable Version

This is a portable version of {APP_NAME}.
Simply run {APP_NAME}.exe to start the application.

Requirements:
- VLC Media Player must be installed
- Windows 10 or later

For more information, visit: {APP_URL}
"""
        with open(temp_dir / "README.txt", "w") as f:
            f.write(readme_content)

        # Create ZIP
        zip_path = DIST_DIR / f"{APP_NAME}-{APP_VERSION}-windows-portable"
        try:
            shutil.make_archive(
                str(zip_path), "zip", str(temp_dir.parent), temp_dir.name
            )
            shutil.rmtree(temp_dir)  # Clean up

            zip_file = Path(str(zip_path) + ".zip")
            if zip_file.exists():
                print(f"SUCCESS: Windows portable ZIP created: {zip_file}")
                return True
        except Exception as e:
            print(f"ERROR: ZIP creation failed: {e}")
            return False
    else:
        # Directory structure
        app_dir = DIST_DIR / APP_NAME
        zip_path = DIST_DIR / f"{APP_NAME}-{APP_VERSION}-windows"

        try:
            shutil.make_archive(str(zip_path), "zip", str(app_dir.parent), app_dir.name)

            zip_file = Path(str(zip_path) + ".zip")
            if zip_file.exists():
                print(f"SUCCESS: Windows ZIP created: {zip_file}")
                return True
        except Exception as e:
            print(f"ERROR: ZIP creation failed: {e}")
            return False


def generate_nsis_script(onefile=False):
    """Generate NSIS installer script"""
    # Use forward slashes for NSIS paths
    dist_dir_nsis = str(DIST_DIR).replace("\\", "/")

    if onefile:
        install_files = f'File "{dist_dir_nsis}/{APP_NAME}.exe"'
    else:
        install_files = f'File /r "{dist_dir_nsis}/{APP_NAME}/*"'

    return f"""
; NSIS Script for {APP_NAME}
!include "MUI2.nsh"

!define APP_NAME "{APP_NAME}"
!define APP_VERSION "{APP_VERSION}"
!define APP_PUBLISHER "{APP_AUTHOR}"
!define APP_URL "{APP_URL}"
!define APP_DESCRIPTION "{APP_DESCRIPTION}"

Name "${{APP_NAME}}"
OutFile "{dist_dir_nsis}/{APP_NAME}-{APP_VERSION}-windows-installer.exe"
InstallDir "$PROGRAMFILES64\\${{APP_NAME}}"
InstallDirRegKey HKCU "Software\\${{APP_NAME}}" ""
RequestExecutionLevel admin

; Modern UI Configuration
!insertmacro MUI_PAGE_WELCOME
; Skip license page if LICENSE file doesn't exist
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    {install_files}
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\{APP_NAME}.exe"
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\{APP_NAME}.exe"
    
    ; Registry entries
    WriteRegStr HKCU "Software\\${{APP_NAME}}" "" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayVersion" "${{APP_VERSION}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "Publisher" "${{APP_PUBLISHER}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "URLInfoAbout" "${{APP_URL}}"
    
    WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\\uninstall.exe"
    RMDir /r "$INSTDIR"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    RMDir /r "$SMPROGRAMS\\${{APP_NAME}}"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
    DeleteRegKey HKCU "Software\\${{APP_NAME}}"
SectionEnd
"""


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--onefile", action="store_true", help="Build for single-file executable"
    )
    args = parser.parse_args()

    if not ensure_directories():
        sys.exit(1)

    if build_windows_installer(onefile=args.onefile):
        print("SUCCESS: Windows installer build completed")
    else:
        print("ERROR: Windows installer build failed")
        sys.exit(1)
