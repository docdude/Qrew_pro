"""
Create universal binary from separate architecture builds

This script combines Intel (x86_64) and Apple Silicon (arm64) app bundles
into a single universal binary app that can run natively on both architectures.
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path


def run_command(cmd):
    """Run command with error handling"""
    print(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True)
        stdout = result.stdout.decode('utf-8', errors='ignore')
        if stdout:
            print(f"STDOUT: {stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e}")
        stdout = e.stdout.decode('utf-8', errors='ignore') if e.stdout else ""
        stderr = e.stderr.decode('utf-8', errors='ignore') if e.stderr else ""
        if stdout:
            print(f"STDOUT: {stdout}")
        if stderr:
            print(f"STDERR: {stderr}")
        return False


def is_app_bundle(path):
    """Check if path is an app bundle or a standalone executable"""
    path = Path(path)
    return path.is_dir() and path.suffix == ".app"


def create_universal_binary(x86_binary_path, arm_binary_path, output_path):
    """Create a universal binary from x86_64 and arm64 binaries"""
    # Create universal binary using lipo
    cmd = [
        "lipo",
        "-create",
        "-output",
        str(output_path),
        str(x86_binary_path),
        str(arm_binary_path),
    ]

    if not run_command(cmd):
        print("ERROR: Failed to create universal binary")
        return False

    print("SUCCESS: Universal binary created")

    # Verify the universal binary
    verify_cmd = ["lipo", "-info", str(output_path)]
    if run_command(verify_cmd):
        # Set executable permissions
        output_path.chmod(0o755)
        print("Set executable permissions on universal binary")
        return True

    return False


def create_universal_app(intel_app, arm_app, output_app):
    """Create universal app bundle or executable depending on input"""
    print(f"Creating universal binary from {intel_app} and {arm_app}")

    x86_path = Path(intel_app)
    arm_path = Path(arm_app)
    universal_path = Path(output_app)

    # Validate input paths
    if not x86_path.exists():
        print(f"ERROR: Intel binary not found at: {x86_path}")
        return False
    if not arm_path.exists():
        print(f"ERROR: ARM binary not found at: {arm_path}")
        return False

    # Detect if we're working with app bundles or standalone executables
    x86_is_app = is_app_bundle(x86_path)
    arm_is_app = is_app_bundle(arm_path)

    # Make sure both inputs are of the same type
    if x86_is_app != arm_is_app:
        print(f"ERROR: Input types don't match: x86={x86_is_app}, arm={arm_is_app}")
        return False

    # Handle app bundle case
    if x86_is_app:
        print("Working with app bundles")

        # Create clean destination
        if universal_path.exists():
            print(f"Removing existing universal app: {universal_path}")
            shutil.rmtree(universal_path)

        # Copy x86 app as base (typically has all resources)
        print("Copying Intel app as base structure")
        shutil.copytree(x86_path, universal_path)

        # Get binary paths
        app_name = "Qrew"  # Adjust if needed
        x86_binary = x86_path / "Contents" / "MacOS" / app_name
        arm_binary = arm_path / "Contents" / "MacOS" / app_name
        universal_binary = universal_path / "Contents" / "MacOS" / app_name

        # Validate binary paths
        if not x86_binary.exists():
            print(f"ERROR: Intel binary not found at: {x86_binary}")
            return False
        if not arm_binary.exists():
            print(f"ERROR: ARM binary not found at: {arm_binary}")
            return False

        # Check architecture of binaries
        for binary_path, arch_name in [(x86_binary, "Intel"), (arm_binary, "ARM")]:
            check_arch_cmd = ["lipo", "-info", str(binary_path)]
            result = subprocess.run(
                check_arch_cmd, capture_output=True, text=True, check=False
            )
            print(f"{arch_name} binary architecture: {result.stdout.strip()}")

        # Create the universal binary
        return create_universal_binary(x86_binary, arm_binary, universal_binary)

    # Handle standalone executable case
    else:
        print("Working with standalone executables")

        # Check architecture of binaries
        for bin_path, arch_name in [(x86_path, "Intel"), (arm_path, "ARM")]:
            check_arch_cmd = ["lipo", "-info", str(bin_path)]
            result = subprocess.run(
                check_arch_cmd, capture_output=True, text=True, check=False
            )
            print(f"{arch_name} binary architecture: {result.stdout.strip()}")

        # Make sure universal path's parent directory exists
        if universal_path.exists():
            print(f"Removing existing universal binary: {universal_path}")
            universal_path.unlink()

        universal_path.parent.mkdir(parents=True, exist_ok=True)

        # Create the universal binary directly
        return create_universal_binary(x86_path, arm_path, universal_path)


def find_apps_in_directory(directory, app_name="Qrew"):
    """Find app bundles in a directory

    Useful for GitHub Actions artifact paths
    """
    directory = Path(directory)
    apps = list(directory.glob(f"**/{app_name}.app"))
    return apps


if __name__ == "__main__":
    # Print system information for debugging in CI
    print(f"Python version: {sys.version}")
    print(f"Running on: {platform.platform()}")

    # Check for command line arguments
    if len(sys.argv) != 4:
        print("Usage: python create_universal.py <intel> <arm> <output>")
        # For GitHub Actions, provide a hint about directory structure
        print("\nIn GitHub Actions, the paths might look like:")
        print("  macos-installer-x86_64/Qrew.app")
        print("  macos-installer-arm64/Qrew.app")
        print("  universal/Qrew.app")
        sys.exit(1)

    intel_app, arm_app, output_app = sys.argv[1:4]

    # Create parent directory for universal app if needed
    output_path = Path(output_app)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Run the universal binary creation
    print("Starting universal app creation process...")
    if create_universal_app(intel_app, arm_app, output_app):
        print("✅ SUCCESS: Universal app created successfully")

        # Output details for GitHub Actions logs
        print(f"Universal app path: {os.path.abspath(output_app)}")
        sys.exit(0)
    else:
        print("❌ ERROR: Failed to create universal app")
        sys.exit(1)
