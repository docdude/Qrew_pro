"""
Linux packages build script for Qrew
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

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


def build_linux_installer(onefile=False):
    """Build Linux packages"""
    print("Building Linux packages...")

    if onefile:
        exe_path = DIST_DIR / APP_NAME
        if not exe_path.exists():
            print("ERROR: Linux executable not found. Run PyInstaller first.")
            return False
    else:
        app_dir = DIST_DIR / APP_NAME
        if not app_dir.exists():
            print("ERROR: Linux app directory not found. Run PyInstaller first.")
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

    # Build .rpm package - only try if rpmbuild is available
    try:
        subprocess.run(["rpmbuild", "--version"], check=True, capture_output=True)
        if build_rpm_package(onefile):
            print("SUCCESS: .rpm package created")
        else:
            print("WARNING: .rpm package creation failed")
    except:
        print("INFO: rpmbuild not available, skipping .rpm creation")

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
            # For single file, just strip if possible
            try:
                subprocess.run(
                    ["strip", "--strip-unneeded", str(exe_path)],
                    check=False,
                    capture_output=True,
                )
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
        "**/*.a",  # Static libraries
        "**/*.la",  # Libtool files
        "lib*/libQt5Test*",  # Test libraries
        "lib*/libQt5Designer*",  # Designer libraries
        "include",  # Header files
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
                    dir_size = sum(
                        f.stat().st_size for f in path.rglob("*") if f.is_file()
                    )
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
                    subprocess.run(
                        ["strip", "--strip-unneeded", str(binary)],
                        check=False,
                        capture_output=True,
                    )
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
 Provides advanced measurement and analysis capabilities.
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
            # Copy contents, not the directory itself
            for item in app_source.iterdir():
                if item.is_file():
                    shutil.copy2(item, app_install_dir)
                elif item.is_dir():
                    shutil.copytree(
                        item, app_install_dir / item.name, dirs_exist_ok=True
                    )

    # Add icon file
    icon_dir = pkg_dir / "usr" / "share" / "icons" / "hicolor" / "scalable" / "apps"
    icon_dir.mkdir(parents=True, exist_ok=True)

    # Find and copy icon
    icon_src = get_icon_for_platform()
    if icon_src and icon_src.exists():
        shutil.copy2(icon_src, icon_dir / "Qrew.png")
        # Also copy to app directory
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


def build_rpm_package(onefile=False):
    """Build .rpm package"""
    print("Building .rpm package...")
    try:
        subprocess.run(["rpmbuild", "--version"], check=True, capture_output=True)
        return build_rpm_with_rpmbuild(onefile)
    except:
        print("INFO: rpmbuild not available, trying alien conversion...")
        return build_rpm_with_alien()


def build_rpm_with_alien():
    """Convert .deb to .rpm using alien"""
    deb_file = None
    for deb_path in DIST_DIR.glob("*.deb"):
        deb_file = deb_path
        break

    if not deb_file:
        print("ERROR: No .deb file found for RPM conversion")
        return False

    try:
        subprocess.run(["which", "alien"], check=True, capture_output=True)
    except:
        print("ERROR: alien not installed, cannot convert .deb to .rpm")
        return False

    try:
        cmd = ["alien", "--to-rpm", "--scripts", str(deb_file)]
        result = run_command(cmd, cwd=DIST_DIR)
        if result:
            # Find the generated RPM
            for rpm_file in DIST_DIR.glob("*.rpm"):
                target = DIST_DIR / f"{APP_NAME.lower()}-{APP_VERSION}-linux.rpm"
                if rpm_file != target:
                    rpm_file.rename(target)
                print(f"SUCCESS: RPM created via alien: {target}")
                return True
        return False
    except Exception as e:
        print(f"ERROR: alien conversion failed: {e}")
        return False


def build_rpm_with_rpmbuild(onefile=False):
    """Build RPM using rpmbuild"""
    print("Building .rpm package with rpmbuild...")
    rpm_build = BUILD_DIR / "rpm_build"
    for subdir in ["SPECS", "SOURCES", "BUILD", "RPMS", "SRPMS"]:
        (rpm_build / subdir).mkdir(parents=True, exist_ok=True)

    spec_content = create_rpm_spec(onefile)
    spec_file = rpm_build / "SPECS" / f"{APP_NAME.lower()}.spec"
    with open(spec_file, "w") as f:
        f.write(spec_content)

    if not create_rpm_sources(rpm_build, onefile):
        return False

    try:
        cmd = ["rpmbuild", "--define", f"_topdir {rpm_build}", "-ba", str(spec_file)]
        if run_command(cmd, cwd=ROOT_DIR):
            for rpm_file in (rpm_build / "RPMS").rglob("*.rpm"):
                target = DIST_DIR / f"{APP_NAME.lower()}-{APP_VERSION}-linux.rpm"
                shutil.copy2(rpm_file, target)
                print(f"SUCCESS: RPM copied to: {target}")
                return True
        return False
    except Exception as e:
        print(f"ERROR: .rpm build exception: {e}")
        return False


def create_rpm_spec(onefile=False):
    """Create RPM spec file content"""
    return f"""Name: {APP_NAME.lower()}
Version: {APP_VERSION}
Release: 1%{{?dist}}
Summary: {APP_DESCRIPTION}

License: GPL-3.0
URL: {APP_URL}
Source0: %{{name}}-%{{version}}.tar.gz

Requires: python3, vlc

%description
{APP_DESCRIPTION}
Automated loudspeaker measurement system using REW API.

%prep
%setup -q

%install
mkdir -p %{{buildroot}}/opt/{APP_NAME}
cp -r * %{{buildroot}}/opt/{APP_NAME}/

mkdir -p %{{buildroot}}/usr/local/bin
cat > %{{buildroot}}/usr/local/bin/{APP_NAME.lower()} << 'EOF'
#!/bin/bash
export LD_LIBRARY_PATH=/opt/{APP_NAME}:$LD_LIBRARY_PATH
cd /opt/{APP_NAME}
./{APP_NAME} "$@"
EOF
chmod +x %{{buildroot}}/usr/local/bin/{APP_NAME.lower()}

mkdir -p %{{buildroot}}/usr/share/applications
cat > %{{buildroot}}/usr/share/applications/{APP_NAME.lower()}.desktop << 'EOF'
[Desktop Entry]
Name={APP_NAME}
Comment={APP_DESCRIPTION}
Exec=/opt/{APP_NAME}/{APP_NAME}
Icon=/opt/{APP_NAME}/Qrew.png
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Engineering;
EOF

%files
/opt/{APP_NAME}/
/usr/local/bin/{APP_NAME.lower()}
/usr/share/applications/{APP_NAME.lower()}.desktop

%changelog
* {datetime.now().strftime('%a %b %d %Y')} {APP_AUTHOR} - {APP_VERSION}-1
- Initial release
"""


def create_rpm_sources(rpm_build, onefile=False):
    """Create source tarball for RPM"""
    print("Creating RPM source tarball...")

    sources_dir = rpm_build / "SOURCES"

    if onefile:
        app_source = DIST_DIR / APP_NAME
    else:
        app_source = DIST_DIR / APP_NAME

    # Create a directory with the expected name
    temp_dir = BUILD_DIR / f"{APP_NAME.lower()}-{APP_VERSION}"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    if onefile:
        temp_dir.mkdir(parents=True)
        shutil.copy2(app_source, temp_dir / APP_NAME)
    else:
        shutil.copytree(app_source, temp_dir)

    tarball_name = f"{APP_NAME.lower()}-{APP_VERSION}.tar.gz"
    cmd = [
        "tar",
        "-czf",
        str(sources_dir / tarball_name),
        "-C",
        str(BUILD_DIR),
        f"{APP_NAME.lower()}-{APP_VERSION}",
    ]

    result = run_command(cmd, cwd=ROOT_DIR)

    # Clean up
    shutil.rmtree(temp_dir)

    return result


def create_tarball(onefile=False):
    """Create a tar.gz distribution"""
    print("Creating tar.gz archive...")

    if onefile:
        source = DIST_DIR / APP_NAME
        tarball_path = (
            DIST_DIR / f"{APP_NAME.lower()}-{APP_VERSION}-linux-portable.tar.gz"
        )

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
                "tar",
                "-czf",
                str(tarball_path),
                "-C",
                str(app_dir.parent),
                app_dir.name,
            ]
            return run_command(cmd, cwd=ROOT_DIR)
        except Exception as e:
            print(f"ERROR: tar.gz creation failed: {e}")
            return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--onefile", action="store_true", help="Build for single-file executable"
    )
    args = parser.parse_args()

    if not ensure_directories():
        sys.exit(1)

    if build_linux_installer(onefile=args.onefile):
        print("SUCCESS: Linux packages build completed")
    else:
        print("ERROR: Linux packages build failed")
        sys.exit(1)
