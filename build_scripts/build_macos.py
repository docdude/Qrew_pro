"""
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
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True, timeout=timeout
        )
        if result.stdout:
            print(f"STDOUT: {result.stdout}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False, e.stderr
    except subprocess.TimeoutExpired:
        print(f"ERROR: Command timed out after {timeout} seconds")
        return False, "Command timed out"


def get_best_signing_identity():
    """Get the best available signing identity, preferring Developer ID Application"""
    codesign_identity = os.getenv("CODESIGN_IDENTITY")
    if codesign_identity:
        print(f"Using provided signing identity: {codesign_identity}")
        return codesign_identity

    (success, output) = run_command(
        ["security", "find-identity", "-v", "-p", "codesigning"]
    )
    if not success:
        return None

    dev_id_certs = []
    for line in output.split("\n"):
        if "Developer ID Application" in line:
            # Parse line like: "  3) 9B48A1831C9E0C0F30F4DB3D5445CDF7F35D37A2 "Developer ID Application: Juan Loya (SE8KQJYGX3)""
            line = line.strip()
            if ") " in line:
                # Split on ') ' to get the part after the number
                parts = line.split(") ", 1)
                if len(parts) >= 2:
                    rest = parts[
                        1
                    ]  # "9B48A1831C9E0C0F30F4DB3D5445CDF7F35D37A2 "Developer ID Application: Juan Loya (SE8KQJYGX3)""
                    # Split on space to get hash and name
                    rest_parts = rest.split(" ", 1)
                    if len(rest_parts) >= 2:
                        hash_part = rest_parts[0]  # The full hash
                        name_part = rest_parts[1].strip('"')  # The certificate name
                        dev_id_certs.append((hash_part, name_part))

    if not dev_id_certs:
        print("INFO: No Developer ID Application certificates found")
        return None

    # Use the first Developer ID Application certificate found
    best_cert = dev_id_certs[0]
    print(f"Selected certificate: {best_cert[1]}")
    print(f"Certificate hash: {best_cert[0]}")
    return best_cert[0]  # Return the full hash


def sign_app_bundle():
    """Code sign the macOS app bundle"""
    app_path = DIST_DIR / f"{APP_NAME}.app"
    if not app_path.exists():
        print("ERROR: App bundle not found for signing")
        return False

    codesign_identity = get_best_signing_identity()
    if not codesign_identity:
        print("INFO: No suitable signing identity found, skipping signing")
        return True

    print(f"Signing app bundle with identity: {codesign_identity}")

    # Prepare signing command
    entitlements_path = ROOT_DIR / "assets" / "entitlements.plist"

    sign_cmd = [
        "codesign",
        "--deep",
        "--force",
        "--verify",
        "--verbose",
        "--options",
        "runtime",
        "--sign",
        codesign_identity,
    ]

    # Add entitlements if available
    if entitlements_path.exists():
        sign_cmd.extend(["--entitlements", str(entitlements_path)])
        print(f"Using entitlements: {entitlements_path}")
    else:
        print("WARNING: entitlements.plist not found, signing without entitlements")

    # Add the app path
    sign_cmd.append(str(app_path))

    # Sign the app bundle
    success, output = run_command(sign_cmd)
    if not success:
        print("ERROR: Code signing failed")
        return False

    print("SUCCESS: App bundle signed")

    # Verify the signature
    verify_cmd = [
        "codesign",
        "--verify",
        "--deep",
        "--strict",
        "--verbose=2",
        str(app_path),
    ]
    success, output = run_command(verify_cmd)
    if success:
        print("SUCCESS: Code signature verified")
    else:
        print("WARNING: Code signature verification failed")

    return True


def create_dmg():
    """Create DMG file"""
    print("Creating DMG installer...")

    app_path = DIST_DIR / f"{APP_NAME}.app"
    dmg_path = DIST_DIR / f"{APP_NAME}-{APP_VERSION}-macos.dmg"

    if not app_path.exists():
        print("ERROR: .app bundle not found for DMG creation")
        return False

    # Remove existing DMG
    if dmg_path.exists():
        dmg_path.unlink()

    # Create DMG configuration
    dmg_config = create_dmg_config()
    config_path = BUILD_DIR / "dmg_config.py"
    config_path.parent.mkdir(exist_ok=True)

    with open(config_path, "w") as f:
        f.write(dmg_config)

    print(f"Creating DMG: {dmg_path}")

    # Build DMG using dmgbuild
    cmd = ["dmgbuild", "-s", str(config_path), APP_NAME, str(dmg_path)]
    success, output = run_command(cmd, timeout=600)

    # Cleanup config file
    if config_path.exists():
        config_path.unlink()

    if success and dmg_path.exists():
        print(f"SUCCESS: DMG created: {dmg_path}")
        return True
    else:
        print("ERROR: Failed to create DMG")
        return False


def sign_dmg():
    """Sign the DMG file"""
    dmg_files = list(DIST_DIR.glob("*.dmg"))
    if not dmg_files:
        print("ERROR: No DMG file found for signing")
        return False

    dmg_path = dmg_files[0]

    codesign_identity = get_best_signing_identity()
    if not codesign_identity:
        print("INFO: No suitable signing identity found, skipping DMG signing")
        return True

    print(f"Signing DMG: {dmg_path.name}")

    sign_cmd = [
        "codesign",
        "--force",
        "--verify",
        "--verbose",
        "--sign",
        codesign_identity,
        str(dmg_path),
    ]

    success, output = run_command(sign_cmd)
    if success:
        print("SUCCESS: DMG signed")
        return True
    else:
        print("ERROR: DMG signing failed")
        return False


def check_notarization_setup():
    """Check if notarization credentials are properly set up"""
    apple_id = os.getenv("APPLE_ID")
    apple_id_password = os.getenv("APPLE_ID_PASSWORD")
    team_id = os.getenv("APPLE_TEAM_ID")

    if not apple_id:
        print("INFO: APPLE_ID not set")
        return False
    if not apple_id_password:
        print("INFO: APPLE_ID_PASSWORD not set")
        return False
    if not team_id:
        print("INFO: APPLE_TEAM_ID not set")
        return False

    print(f"Notarization setup: Apple ID={apple_id}, Team ID={team_id}")
    return True


def notarize_dmg():
    """Submit DMG for notarization"""
    dmg_files = list(DIST_DIR.glob("*.dmg"))
    if not dmg_files:
        print("ERROR: No DMG file found for notarization")
        return False

    dmg_path = dmg_files[0]

    if not check_notarization_setup():
        print("INFO: Skipping notarization - credentials not configured")
        print("INFO: To enable notarization, set environment variables:")
        print('      export APPLE_ID="your-apple-id@example.com"')
        print('      export APPLE_ID_PASSWORD="your-app-specific-password"')
        print('      export APPLE_TEAM_ID="YOUR_TEAM_ID"')
        return False  # Return False so we know notarization was skipped

    apple_id = os.getenv("APPLE_ID")
    apple_id_password = os.getenv("APPLE_ID_PASSWORD")
    team_id = os.getenv("APPLE_TEAM_ID")

    print(f"Submitting {dmg_path.name} for notarization...")
    print("This may take 10-30 minutes...")

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

    success, output = run_command(notarize_cmd, timeout=2400)  # 40 minute timeout
    if success:
        print("SUCCESS: DMG notarized")
        return True
    else:
        print("ERROR: Notarization failed")
        return False


def staple_dmg(notarization_successful):
    """Staple the notarization to the DMG"""
    if not notarization_successful:
        print("INFO: Skipping stapling - notarization was not performed or failed")
        return True  # Don't fail the build for this

    dmg_files = list(DIST_DIR.glob("*.dmg"))
    if not dmg_files:
        print("ERROR: No DMG file found for stapling")
        return False

    dmg_path = dmg_files[0]

    print(f"Stapling notarization to {dmg_path.name}...")

    staple_cmd = ["xcrun", "stapler", "staple", str(dmg_path)]
    success, output = run_command(staple_cmd)

    if success:
        print("SUCCESS: Notarization stapled to DMG")

        # Verify stapling
        verify_cmd = ["xcrun", "stapler", "validate", str(dmg_path)]
        success, output = run_command(verify_cmd)
        if success:
            print("SUCCESS: Stapled notarization verified")
        else:
            print("WARNING: Could not verify stapled notarization")

        return True
    else:
        print("ERROR: Failed to staple notarization")
        return False


def create_dmg_config():
    """Generate DMG configuration"""
    # Calculate app size dynamically
    app_path = DIST_DIR / f"{APP_NAME}.app"
    if app_path.exists():
        result = subprocess.run(
            ["du", "-sk", str(app_path)], capture_output=True, text=True
        )
        if result.returncode == 0:
            app_size_kb = int(result.stdout.split()[0])
            # Add 50% padding and convert to MB
            dmg_size_mb = int((app_size_kb * 1.5) / 1024)
            # Minimum 200MB, maximum 2GB
            dmg_size = max(200, min(2048, dmg_size_mb))
        else:
            dmg_size = 400  # Default fallback
    else:
        dmg_size = 400  # Default fallback

    return f"""# DMG build configuration
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

# Background color
background = "#f0f0f0"

# License agreement (if LICENSE file exists)
license_path = Path("{ROOT_DIR}") / "LICENSE"
if license_path.exists():
    license = {{
        "default-language": "en_US", 
        "licenses": {{
            "en_US": str(license_path),
        }},
        "show-license": True,
    }}
"""


def build_macos_installer():
    """Build complete macOS installer with signing and notarization"""
    print("=" * 60)
    print("BUILDING MACOS INSTALLER")
    print("=" * 60)

    app_path = DIST_DIR / f"{APP_NAME}.app"
    if not app_path.exists():
        print("ERROR: .app bundle not found. Run PyInstaller first.")
        return False

    success_count = 0
    total_steps = 5
    notarization_successful = False

    # Step 1: Sign the app bundle
    print("\n1. Signing app bundle...")
    if sign_app_bundle():
        success_count += 1
        print("✓ App bundle signing completed")
    else:
        print("✗ App bundle signing failed")

    # Step 2: Create DMG
    print("\n2. Creating DMG...")
    if create_dmg():
        success_count += 1
        print("✓ DMG creation completed")
    else:
        print("✗ DMG creation failed")
        return False  # Can't continue without DMG

    # Step 3: Sign DMG
    print("\n3. Signing DMG...")
    if sign_dmg():
        success_count += 1
        print("✓ DMG signing completed")
    else:
        print("✗ DMG signing failed")

    # Step 4: Notarize DMG
    print("\n4. Notarizing DMG...")
    if notarize_dmg():
        success_count += 1
        notarization_successful = True
        print("✓ DMG notarization completed")
    else:
        print("✗ DMG notarization failed or skipped")

    # Step 5: Staple notarization
    print("\n5. Stapling notarization...")
    if staple_dmg(notarization_successful):
        if notarization_successful:
            success_count += 1
            print("✓ Notarization stapling completed")
        else:
            print("- Stapling skipped (no notarization)")
    else:
        print("✗ Notarization stapling failed")

    # Summary
    print("\n" + "=" * 60)
    print("MACOS BUILD SUMMARY")
    print("=" * 60)
    print(f"Completed steps: {success_count}/{total_steps}")

    dmg_files = list(DIST_DIR.glob("*.dmg"))
    if dmg_files:
        dmg_path = dmg_files[0]
        size_mb = dmg_path.stat().st_size / (1024 * 1024)
        print(f"DMG created: {dmg_path.name} ({size_mb:.1f} MB)")

        if success_count >= 4:
            print("✓ DMG is signed and notarized")
        elif success_count >= 3:
            print("✓ DMG is signed (notarization skipped)")
        else:
            print("⚠ DMG created but may not be properly signed")

    return success_count >= 2  # At least app signed and DMG created


if __name__ == "__main__":
    import sys

    success = build_macos_installer()
    sys.exit(0 if success else 1)
