"""
macOS-specific build script
"""

import os
import subprocess
import shutil
from pathlib import Path
from build_config import *


def sign_and_notarize_app():
    """Sign and notarize the macOS app"""
    app_path = DIST_DIR / f"{APP_NAME}.app"
    if not app_path.exists():
        print("ERROR: App bundle not found for signing")
        return False

    # Get signing identity from environment
    codesign_identity = os.getenv("CODESIGN_IDENTITY")
    if not codesign_identity:
        print("INFO: No code signing identity provided, skipping signing")
        return True

    print(f"Signing app with identity: {codesign_identity}")

    # Sign the app bundle
    entitlements_path = ROOT_DIR / "assets" / "entitlements.plist"
    if not entitlements_path.exists():
        print("WARNING: entitlements.plist not found, signing without entitlements")
        entitlements_path = None

    sign_cmd = [
        "codesign",
        "--deep",
        "--force",
        "--verify",
        "--options",
        "runtime",
        "--sign",
        codesign_identity,
        str(app_path),
    ]

    if entitlements_path:
        sign_cmd.extend(["--entitlements", str(entitlements_path)])

    try:
        result = subprocess.run(sign_cmd, check=True, capture_output=True, text=True)
        print("SUCCESS: App bundle signed")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Code signing failed: {e}")
        print(f"Stderr: {e.stderr}")
        return False

    # Verify signing
    verify_cmd = ["codesign", "--verify", "--deep", "--strict", str(app_path)]
    try:
        subprocess.run(verify_cmd, check=True, capture_output=True)
        print("SUCCESS: Code signature verified")
    except subprocess.CalledProcessError as e:
        print(f"WARNING: Code signature verification failed: {e}")

    return True


def notarize_dmg():
    """Notarize the DMG file"""
    dmg_files = list(DIST_DIR.glob("*.dmg"))
    if not dmg_files:
        print("ERROR: No DMG file found for notarization")
        return False

    dmg_path = dmg_files[0]

    # Check for required environment variables
    apple_id = os.getenv("APPLE_ID")
    apple_id_password = os.getenv("APPLE_ID_PASSWORD")
    team_id = os.getenv("APPLE_TEAM_ID")

    if not all([apple_id, apple_id_password, team_id]):
        print("INFO: Apple ID credentials not provided, skipping notarization")
        return True

    print(f"Submitting {dmg_path.name} for notarization...")

    notarize_cmd = [
        "xcrun",
        "notarytool",
        "submit",
        str(dmg_path),
        "--apple-id",
        apple_id,
        "--password",
        apple_id_password,
        "--team-id",
        team_id,
        "--wait",
    ]

    try:
        result = subprocess.run(
            notarize_cmd, check=True, capture_output=True, text=True, timeout=1800
        )  # 30 minute timeout
        print("SUCCESS: DMG notarized")
        print(result.stdout)

        # Staple the notarization
        staple_cmd = ["xcrun", "stapler", "staple", str(dmg_path)]
        subprocess.run(staple_cmd, check=True, capture_output=True)
        print("SUCCESS: Notarization stapled to DMG")

        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Notarization failed: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        print("ERROR: Notarization timed out")
        return False


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

    with open(config_path, "w") as f:
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
    # Calculate app size dynamically
    app_path = DIST_DIR / f"{APP_NAME}.app"
    if app_path.exists():
        import subprocess

        result = subprocess.run(
            ["du", "-sk", str(app_path)], capture_output=True, text=True
        )
        app_size_kb = int(result.stdout.split()[0])
        # Add 50% padding and convert to MB
        dmg_size_mb = int((app_size_kb * 1.5) / 1024)
        # Minimum 500MB, maximum 2GB
        dmg_size = max(500, min(2048, dmg_size_mb))
    else:
        dmg_size = 800  # Default fallback

    return f"""
# DMG build configuration
import os
from pathlib import Path

# Volume settings  
volume_name = "{APP_NAME}"
format = "UDBZ"  # Compressed
size = "{dmg_size}M"

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
#background = str(Path("{ASSETS_DIR}") / "dmg_background.png")
background = str("#cafeee")
# License agreement
license = {{
    "default-language": "en_US", 
    "licenses": {{
        "en_US": str(Path("{ROOT_DIR}") / "LICENSE"),
    }},
    "show-license": True,
}}
"""


def sign_app():
    """Code sign the app (requires Apple Developer certificate)"""
    app_path = DIST_DIR / f"{APP_NAME}.app"

    # Check if signing certificate is available
    result = subprocess.run(
        ["security", "find-identity", "-v", "-p", "codesigning"],
        capture_output=True,
        text=True,
    )

    if "Developer ID Application" not in result.stdout:
        print("Warning: No code signing certificate found. Skipping signing.")
        return True

    print("Code signing app...")
    cmd = [
        "codesign",
        "--force",
        "--deep",
        "--sign",
        "Developer ID Application",
        str(app_path),
    ]

    result = subprocess.run(cmd)
    return result.returncode == 0


def notarize_app():
    """Notarize the app with Apple (requires Apple Developer account)"""
    dmg_path = DIST_DIR / f"{APP_NAME}-{APP_VERSION}-macos.dmg"

    print("Notarizing app (this may take several minutes)...")
    cmd = [
        "xcrun",
        "notarytool",
        "submit",
        str(dmg_path),
        "--keychain-profile",
        "notarytool-password",
        "--wait",
    ]

    result = subprocess.run(cmd)
    if result.returncode == 0:
        # Staple the notarization
        cmd = ["xcrun", "stapler", "staple", str(dmg_path)]
        subprocess.run(cmd)

    return result.returncode == 0
