"""
Enhanced macOS build script with better notarization error handling and debugging
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


def get_build_architecture():
    """Get the architecture we're building for"""
    arch = os.getenv("MACOS_BUILD_ARCH", "native")
    if arch == "native":
        # Detect current architecture
        try:
            result = subprocess.run(["uname", "-m"], capture_output=True)
            arch = result.stdout.decode('utf-8', errors='ignore').strip()
        except Exception as e:
            print(f"Error detecting architecture: {e}, falling back to x86_64")
            arch = "x86_64"  # Fallback to x86_64 on error
    return arch


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
            # Parse certificate info
            line = line.strip()
            if ") " in line:
                parts = line.split(") ", 1)
                if len(parts) >= 2:
                    rest = parts[1]
                    rest_parts = rest.split(" ", 1)
                    if len(rest_parts) >= 2:
                        hash_part = rest_parts[0]
                        name_part = rest_parts[1].strip("\"'")
                        dev_id_certs.append((hash_part, name_part))

    if not dev_id_certs:
        print("INFO: No Developer ID Application certificates found")
        return None

    # Use the first Developer ID Application certificate found
    best_cert = dev_id_certs[0]
    print(f"Selected certificate: {best_cert[1]}")
    print(f"Certificate hash: {best_cert[0]}")
    return best_cert[0]  # Return the full hash


def create_enhanced_entitlements():
    """Create enhanced entitlements for notarization"""
    entitlements_content = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Enable Hardened Runtime -->
    <key>com.apple.security.cs.allow-jit</key>
    <false/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <false/>
    <key>com.apple.security.cs.allow-dyld-environment-variables</key>
    <false/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    
    <!-- Network access -->
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.network.server</key>
    <true/>
    
    <!-- File system access -->
    <key>com.apple.security.files.downloads.read-write</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
    
    <!-- Audio access (for VLC) -->
    <key>com.apple.security.device.audio-input</key>
    <true/>
    <key>com.apple.security.device.microphone</key>
    <true/>
    
    <!-- Camera access (if needed) -->
    <key>com.apple.security.device.camera</key>
    <false/>
</dict>
</plist>"""

    entitlements_path = ROOT_DIR / "assets" / "entitlements.plist"
    entitlements_path.parent.mkdir(exist_ok=True)

    with open(entitlements_path, "w") as f:
        f.write(entitlements_content)

    print(f"Created enhanced entitlements: {entitlements_path}")
    return entitlements_path


def sign_app_bundle(app_path, onefile=False):
    """Code sign the macOS app bundle or executable with enhanced options"""
    if not app_path.exists():
        print(f"ERROR: App/executable not found for signing: {app_path}")
        return False

    codesign_identity = get_best_signing_identity()
    if not codesign_identity:
        print("INFO: No suitable signing identity found, skipping signing")
        return True

    print(
        f"Signing {'executable' if onefile else 'app bundle'} with identity: {codesign_identity}"
    )

    # Create enhanced entitlements
    entitlements_path = create_enhanced_entitlements()

    # Sign with hardened runtime and proper entitlements
    sign_cmd = [
        "codesign",
        "--force",
        "--verify",
        "--verbose",
        "--timestamp",
        "--options",
        "runtime",
        "--entitlements",
        str(entitlements_path),
        "--sign",
        codesign_identity,
    ]

    if not onefile:
        sign_cmd.insert(1, "--deep")

    # Add the app path
    sign_cmd.append(str(app_path))

    # Sign the app/executable
    success, output = run_command(sign_cmd)
    if not success:
        print("ERROR: Code signing failed")
        return False

    print(f"SUCCESS: {'Executable' if onefile else 'App bundle'} signed")

    # Verify the signature with more details
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

        # Also check entitlements
        entitlements_cmd = [
            "codesign",
            "--display",
            "--entitlements",
            "-",
            str(app_path),
        ]
        run_command(entitlements_cmd)

    else:
        print("WARNING: Code signature verification failed")

    return True


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
    """Submit DMG for notarization with better error handling"""
    dmg_files = list(DIST_DIR.glob("*.dmg"))
    if not dmg_files:
        print("ERROR: No DMG file found for notarization")
        return False

    dmg_path = dmg_files[0]

    if not check_notarization_setup():
        print("INFO: Skipping notarization - credentials not configured")
        return False

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
        "--timeout",
        "3600s",  # 1 hour timeout
    ]

    success, output = run_command(notarize_cmd, timeout=3600)

    # Parse the output to get submission ID and status
    submission_id = None
    status = "Unknown"

    for line in output.split("\n"):
        if "id:" in line and not "team-id" in line:
            submission_id = line.split("id:")[1].strip()
        elif "status:" in line:
            status = line.split("status:")[1].strip()

    print(f"Notarization status: {status}")

    if status == "Accepted":
        print("SUCCESS: DMG notarized successfully")
        return True
    elif status == "Invalid":
        print("ERROR: Notarization failed - getting detailed log...")
        if submission_id:
            get_notarization_log(submission_id, apple_id, apple_id_password, team_id)
        return False
    else:
        print(f"ERROR: Notarization failed with status: {status}")
        return False


def get_notarization_log(submission_id, apple_id, password, team_id):
    """Get detailed notarization log"""
    print(f"Fetching notarization log for submission {submission_id}...")

    log_cmd = [
        "xcrun",
        "notarytool",
        "log",
        submission_id,
        "--apple-id",
        apple_id,
        "--password",
        password,
        "--team-id",
        team_id,
    ]

    success, output = run_command(log_cmd)
    if success:
        print("=== NOTARIZATION LOG ===")
        print(output)
        print("=== END LOG ===")

        # Parse common issues
        if "DYLIB_INSTALL_NAME" in output:
            print("\n💡 ISSUE: Dynamic library paths issue")
            print("   Solution: Libraries need proper install names")
        elif "codesign" in output.lower() and "invalid" in output.lower():
            print("\n💡 ISSUE: Code signing problem")
            print("   Solution: Some binaries aren't properly signed")
        elif "entitlements" in output.lower():
            print("\n💡 ISSUE: Entitlements problem")
            print("   Solution: Check entitlements.plist")
    else:
        print("Failed to get notarization log")


def create_dmg(onefile=False):
    """Create DMG file with proper structure"""
    print("Creating DMG installer...")

    arch = get_build_architecture()

    if onefile:
        exe_path = DIST_DIR / APP_NAME
        if not exe_path.exists():
            print("ERROR: Executable not found for DMG creation")
            return False

        # Create a temporary .app bundle for DMG
        temp_app = DIST_DIR / f"{APP_NAME}.app"
        create_minimal_app_bundle(exe_path, temp_app)
        app_path = temp_app
    else:
        app_path = DIST_DIR / f"{APP_NAME}.app"
        if not app_path.exists():
            print("ERROR: .app bundle not found for DMG creation")
            return False

    dmg_path = DIST_DIR / f"{APP_NAME}-{APP_VERSION}-macos-{arch}.dmg"

    # Remove existing DMG
    if dmg_path.exists():
        dmg_path.unlink()

    # Create DMG configuration
    dmg_config = create_dmg_config(onefile=onefile)
    config_path = BUILD_DIR / "dmg_config.py"
    config_path.parent.mkdir(exist_ok=True)

    with open(config_path, "w") as f:
        f.write(dmg_config)

    print(f"Creating DMG: {dmg_path}")

    # Build DMG using dmgbuild
    cmd = ["dmgbuild", "-s", str(config_path), APP_NAME, str(dmg_path)]
    success, output = run_command(cmd, timeout=600)

    # Cleanup
    if config_path.exists():
        config_path.unlink()
    if onefile and temp_app.exists():
        shutil.rmtree(temp_app)

    if success and dmg_path.exists():
        print(f"SUCCESS: DMG created: {dmg_path}")
        return True
    else:
        print("ERROR: Failed to create DMG")
        return False


def create_minimal_app_bundle(exe_path, app_path):
    """Create minimal app bundle for single-file executable"""
    print(f"Creating minimal app bundle at {app_path}")

    # Create directory structure
    contents_dir = app_path / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"

    macos_dir.mkdir(parents=True, exist_ok=True)
    resources_dir.mkdir(parents=True, exist_ok=True)

    # Copy executable
    shutil.copy2(exe_path, macos_dir / APP_NAME)

    # Copy icon if exists
    icns_path = ICONS_DIR / "Qrew.icns"
    if icns_path.exists():
        shutil.copy2(icns_path, resources_dir / "Qrew.icns")

    # Create Info.plist
    info_plist = get_macos_bundle_info()
    plist_content = generate_info_plist(info_plist)

    with open(contents_dir / "Info.plist", "w") as f:
        f.write(plist_content)

    # Make executable
    (macos_dir / APP_NAME).chmod(0o755)


def generate_info_plist(info_dict):
    """Generate Info.plist XML content"""
    plist = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
"""

    for key, value in info_dict.items():
        if isinstance(value, bool):
            plist += f"    <key>{key}</key>\n    <{str(value).lower()}/>\n"
        elif isinstance(value, int):
            plist += f"    <key>{key}</key>\n    <integer>{value}</integer>\n"
        else:
            plist += f"    <key>{key}</key>\n    <string>{value}</string>\n"

    plist += """</dict>
</plist>"""

    return plist


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
        "--timestamp",
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


def staple_dmg(notarization_successful):
    """Staple the notarization to the DMG"""
    if not notarization_successful:
        print("INFO: Skipping stapling - notarization was not successful")
        return True

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
        return True
    else:
        print("ERROR: Failed to staple notarization")
        return False


def create_dmg_config(onefile=False):
    """Generate DMG configuration"""
    # Calculate app size dynamically
    if onefile:
        app_path = DIST_DIR / APP_NAME
        if app_path.exists():
            app_size_kb = app_path.stat().st_size / 1024
            dmg_size = max(200, int((app_size_kb * 2) / 1024))  # Double size, min 200MB
        else:
            dmg_size = 200
    else:
        app_path = DIST_DIR / f"{APP_NAME}.app"
        if app_path.exists():
            result = subprocess.run(
                ["du", "-sk", str(app_path)], capture_output=True, text=True
            )
            if result.returncode == 0:
                app_size_kb = int(result.stdout.split()[0])
                dmg_size = max(200, min(2048, int((app_size_kb * 1.5) / 1024)))
            else:
                dmg_size = 400
        else:
            dmg_size = 400

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
    }}
"""


def build_macos_installer(onefile=False):
    """Build complete macOS installer with enhanced notarization"""
    print("=" * 60)
    print("BUILDING MACOS INSTALLER")
    print("=" * 60)

    arch = get_build_architecture()
    print(f"Building for architecture: {arch}")

    if onefile:
        app_path = DIST_DIR / APP_NAME
        if not app_path.exists():
            print("ERROR: Executable not found. Run PyInstaller first.")
            return False
    else:
        app_path = DIST_DIR / f"{APP_NAME}.app"
        if not app_path.exists():
            print("ERROR: .app bundle not found. Run PyInstaller first.")
            return False

    success_count = 0
    total_steps = 5
    notarization_successful = False

    # Step 1: Sign the app bundle/executable
    print(f"\n1. Signing {'executable' if onefile else 'app bundle'}...")
    if sign_app_bundle(app_path, onefile=onefile):
        success_count += 1
        print(f"✓ {'Executable' if onefile else 'App bundle'} signing completed")
    else:
        print(f"✗ {'Executable' if onefile else 'App bundle'} signing failed")

    # Step 2: Create DMG
    print("\n2. Creating DMG...")
    if create_dmg(onefile=onefile):
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
        print("✗ DMG notarization failed")

    # Step 5: Staple notarization
    print("\n5. Stapling notarization...")
    if staple_dmg(notarization_successful):
        if notarization_successful:
            success_count += 1
            print("✓ Notarization stapling completed")
        else:
            print("- Stapling skipped (notarization failed)")
    else:
        print("✗ Notarization stapling failed")

    # Summary
    print("\n" + "=" * 60)
    print("MACOS BUILD SUMMARY")
    print("=" * 60)
    print(f"Architecture: {arch}")
    print(f"Build mode: {'onefile' if onefile else 'app bundle'}")
    print(f"Completed steps: {success_count}/{total_steps}")

    dmg_files = list(DIST_DIR.glob("*.dmg"))
    if dmg_files:
        dmg_path = dmg_files[0]
        size_mb = dmg_path.stat().st_size / (1024 * 1024)
        print(f"DMG created: {dmg_path.name} ({size_mb:.1f} MB)")

        if success_count >= 4:
            print("✓ DMG is signed and notarized")
        elif success_count >= 3:
            print("✓ DMG is signed (notarization failed - see logs above)")
        else:
            print("⚠ DMG created but may not be properly signed")

    return success_count >= 2  # At least app signed and DMG created


if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--onefile", action="store_true", help="Build for single-file executable"
    )
    parser.add_argument(
        "--create-dmg-only", help="Create DMG from existing app", metavar="APP_PATH"
    )
    args = parser.parse_args()

    if args.create_dmg_only:
        # Special mode for creating universal DMG
        app_path = Path(args.create_dmg_only)
        if app_path.exists():
            # Sign the universal app first
            sign_app_bundle(app_path, onefile=False)
            # Create DMG
            os.environ["MACOS_BUILD_ARCH"] = "universal"
            create_dmg(onefile=False)
            sys.exit(0)
        else:
            print(f"ERROR: App not found: {app_path}")
            sys.exit(1)

    success = build_macos_installer(onefile=args.onefile)
    sys.exit(0 if success else 1)
