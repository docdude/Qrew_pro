"""
Windows-specific build script  
"""
import os
import subprocess
import shutil
from pathlib import Path
from build_config import *

def build_windows_installer():
    """Build Windows installer using NSIS"""
    print("Building Windows installer...")
    
    # Create NSIS script
    nsis_script = create_nsis_script()
    script_path = ROOT_DIR / f"{APP_NAME}.nsi"
    
    with open(script_path, 'w') as f:
        f.write(nsis_script)
    
    # Build installer
    cmd = ["makensis", str(script_path)]
    result = subprocess.run(cmd, cwd=ROOT_DIR)
    
    # Cleanup
    if script_path.exists():
        script_path.unlink()
    
    if result.returncode == 0:
        installer_path = DIST_DIR / f"{APP_NAME}-{APP_VERSION}-windows-installer.exe"
        print(f"Successfully created: {installer_path}")
        return True
    else:
        print("Failed to create Windows installer")
        return False

def create_nsis_script():
    """Create NSIS installer script"""
    return f'''
; NSIS installer script for {APP_NAME}

!define APPNAME "{APP_NAME}"
!define APPVERSION "{APP_VERSION}"
!define APPNAMEANDVERSION "${{APPNAME}} ${{APPVERSION}}"
!define APPDIR "{DIST_DIR / APP_NAME}"

; Main Install settings
Name "${{APPNAMEANDVERSION}}"
InstallDir "$PROGRAMFILES\\${{APPNAME}}"
InstallDirRegKey HKLM "Software\\${{APPNAME}}" ""
OutFile "{DIST_DIR}\\{APP_NAME}-{APP_VERSION}-windows-installer.exe"

; Modern interface settings
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "{get_icon_for_platform()}"
!define MUI_UNICON "{get_icon_for_platform()}"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "{ROOT_DIR}\\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

Section "MainSection" SEC01
    SetOutPath "$INSTDIR"
    SetOverwrite on
    
    ; Install files
    File /r "${{APPDIR}}\\*"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\\${{APPNAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APPNAME}}\\${{APPNAME}}.lnk" "$INSTDIR\\{APP_NAME}.exe"
    CreateShortCut "$SMPROGRAMS\\${{APPNAME}}\\Uninstall.lnk" "$INSTDIR\\uninstall.exe"
    CreateShortCut "$DESKTOP\\${{APPNAME}}.lnk" "$INSTDIR\\{APP_NAME}.exe"
    
    ; Registry entries
    WriteRegStr HKLM "Software\\${{APPNAME}}" "" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayName" "${{APPNAMEANDVERSION}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "DisplayVersion" "${{APPVERSION}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "Publisher" "{APP_AUTHOR}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}" "NoRepair" 1
    
    WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

Section "Uninstall"
    ; Remove files
    RMDir /r "$INSTDIR"
    
    ; Remove shortcuts
    RMDir /r "$SMPROGRAMS\\${{APPNAME}}"
    Delete "$DESKTOP\\${{APPNAME}}.lnk"
    
    ; Remove registry entries
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APPNAME}}"
    DeleteRegKey HKLM "Software\\${{APPNAME}}"
SectionEnd
'''

def sign_exe():
    """Code sign Windows executable (requires certificate)"""
    exe_path = DIST_DIR / APP_NAME / f"{APP_NAME}.exe"
    
    # Check for signing certificate
    # This assumes you have a certificate installed
    print("Checking for code signing certificate...")
    
    cmd = [
        "signtool", "sign",
        "/t", "http://timestamp.digicert.com",
        "/fd", "sha256",
        str(exe_path)
    ]
    
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode == 0:
        print("Successfully signed executable")
        return True
    else:
        print("Warning: Could not sign executable (certificate may not be available)")
        return False
