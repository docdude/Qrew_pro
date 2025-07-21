"""
macOS-specific build script
"""
import os
import subprocess
import shutil
from pathlib import Path
from build_config import *

def build_macos_installer():
    """Build macOS .app bundle and .dmg"""
    print("Building macOS installer...")
    
    app_path = DIST_DIR / f"{APP_NAME}.app"
    dmg_path = DIST_DIR / f"{APP_NAME}-{APP_VERSION}-macos.dmg"
    
    if not app_path.exists():
        print("Error: .app bundle not found. Run PyInstaller first.")
        return False
    
    # Create DMG configuration
    dmg_config = create_dmg_config()
    config_path = ROOT_DIR / "dmg_config.py"
    
    with open(config_path, 'w') as f:
        f.write(dmg_config)
    
    # Build DMG
    cmd = ["dmgbuild", "-s", str(config_path), APP_NAME, str(dmg_path)]
    result = subprocess.run(cmd, cwd=ROOT_DIR)
    
    # Cleanup
    if config_path.exists():
        config_path.unlink()
    
    if result.returncode == 0:
        print(f"Successfully created: {dmg_path}")
        return True
    else:
        print("Failed to create DMG")
        return False

def create_dmg_config():
    """Create DMG build configuration"""
    return f'''
# DMG build configuration
import os
from pathlib import Path

# Volume settings
volume_name = "{APP_NAME}"
format = "UDBZ"  # Compressed
size = "100M"

# Files to include
files = [
    (str(Path("{DIST_DIR}") / "{APP_NAME}.app"), "{APP_NAME}.app"),
]

# Symlink to Applications folder
symlinks = {{
    "Applications": "/Applications"
}}

# Window settings
window_rect = ((100, 100), (600, 400))
icon_size = 128
text_size = 16

# Icon positions
icon_locations = {{
    "{APP_NAME}.app": (150, 200),
    "Applications": (450, 200),
}}

# Background image (if you have one)
# background = str(Path("{ASSETS_DIR}") / "dmg_background.png")

# License agreement
# license = {{
#     "default-language": "en_US",
#     "licenses": {{
#         "en_US": str(Path("{ROOT_DIR}") / "LICENSE"),
#     }},
# }}
'''

def sign_app():
    """Code sign the app (requires Apple Developer certificate)"""
    app_path = DIST_DIR / f"{APP_NAME}.app"
    
    # Check if signing certificate is available
    result = subprocess.run(
        ["security", "find-identity", "-v", "-p", "codesigning"],
        capture_output=True, text=True
    )
    
    if "Developer ID Application" not in result.stdout:
        print("Warning: No code signing certificate found. Skipping signing.")
        return True
    
    print("Code signing app...")
    cmd = [
        "codesign",
        "--force",
        "--deep", 
        "--sign", "Developer ID Application",
        str(app_path)
    ]
    
    result = subprocess.run(cmd)
    return result.returncode == 0

def notarize_app():
    """Notarize the app with Apple (requires Apple Developer account)"""
    dmg_path = DIST_DIR / f"{APP_NAME}-{APP_VERSION}-macos.dmg"
    
    print("Notarizing app (this may take several minutes)...")
    cmd = [
        "xcrun", "notarytool", "submit",
        str(dmg_path),
        "--keychain-profile", "notarytool-password",
        "--wait"
    ]
    
    result = subprocess.run(cmd)
    if result.returncode == 0:
        # Staple the notarization
        cmd = ["xcrun", "stapler", "staple", str(dmg_path)]
        subprocess.run(cmd)
    
    return result.returncode == 0
