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


def optimize_linux_build():
    """Remove unnecessary files and optimize the Linux build"""
    print("Optimizing Linux build...")
    app_dir = DIST_DIR / APP_NAME
    if not app_dir.exists():
        return False

    # Files/directories to remove
    cleanup_patterns = [
        "lib*/libQt5Quick*",
        "lib*/libQt5Qml*",
        "lib*/libQt5WebKit*",
        "lib*/libQt5Test*",
        "lib*/libQt5Multimedia*",
        "lib*/libQt5OpenGL*",
        "lib*/libQt5Sql*",
        "lib*/libQt5Designer*",
        "share/qt5/translations",
        "share/doc",
        "share/man",
        "include",
        "*.debug",
        "*.a",  # Static libraries
        "*.la",  # Libtool files
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
                    dir_size = (
                        get_directory_size(path) * 1024 * 1024
                    )  # Convert back to bytes
                    shutil.rmtree(path)
                    removed_size += dir_size
            except Exception as e:
                print(f"WARNING: Could not remove {path}: {e}")

    print(f"SUCCESS: Removed {removed_size / (1024*1024):.1f} MB of unnecessary files")

    # Strip remaining binaries
    try:
        for binary in app_dir.rglob("*"):
            if (
                binary.is_file()
                and binary.suffix in [".so", ""]
                and not binary.name.endswith(".py")
            ):
                try:
                    subprocess.run(
                        ["strip", "--strip-unneeded", str(binary)],
                        check=False,
                        capture_output=True,
                    )
                except:
                    pass
        print("SUCCESS: Stripped debug symbols from binaries")
    except Exception as e:
        print(f"WARNING: Could not strip binaries: {e}")

    return True


def build_linux_installer():
    """Build Linux packages (.deb and .rpm)"""
    print("Building Linux packages...")

    app_dir = DIST_DIR / APP_NAME
    if not app_dir.exists():
        print("ERROR: Linux app directory not found. Run PyInstaller first.")
        return False

    # Optimize the build first
    optimize_linux_build()

    success = True

    # Build .deb package
    if build_deb_package():
        print("SUCCESS: .deb package created")
    else:
        print("WARNING: .deb package creation failed")
        success = False

    # Build .rpm package - only try if rpmbuild is available
    try:
        subprocess.run(["rpmbuild", "--version"], check=True, capture_output=True)
        if build_rpm_package():
            print("SUCCESS: .rpm package created")
        else:
            print("WARNING: .rpm package creation failed")
            # Don't fail overall build
    except:
        print("INFO: rpmbuild not available, skipping .rpm creation")

    # Always create a tar.gz as fallback
    if create_tarball():
        print("SUCCESS: tar.gz archive created")
    else:
        print("WARNING: tar.gz creation failed")

    return success


def build_deb_package():
    """Build .deb package"""
    print("Building .deb package...")

    pkg_dir = BUILD_DIR / f"{APP_NAME.lower()}-{APP_VERSION}_deb"
    if pkg_dir.exists():
        shutil.rmtree(pkg_dir)

    create_deb_structure(pkg_dir)

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


def build_rpm_package():
    print("Building .rpm package...")
    try:
        subprocess.run(["rpmbuild", "--version"], check=True, capture_output=True)
        return build_rpm_with_rpmbuild()
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


def build_rpm_with_rpmbuild():
    """Original rpmbuild method"""
    print("Building .rpm package with rpmbuild...")
    rpm_build = BUILD_DIR / "rpm_build"
    for subdir in ["SPECS", "SOURCES", "BUILD", "RPMS", "SRPMS"]:
        (rpm_build / subdir).mkdir(parents=True, exist_ok=True)

    spec_content = create_rpm_spec()
    spec_file = rpm_build / "SPECS" / f"{APP_NAME.lower()}.spec"
    with open(spec_file, "w") as f:
        f.write(spec_content)

    if not create_rpm_sources(rpm_build):
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


def create_deb_structure(pkg_dir):
    """Create .deb package structure"""
    print("Creating .deb structure...")

    pkg_dir.mkdir(parents=True, exist_ok=True)

    # DEBIAN control directory
    debian_dir = pkg_dir / "DEBIAN"
    debian_dir.mkdir(exist_ok=True)

    # Control file
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

    # Application files
    app_install_dir = pkg_dir / "opt" / APP_NAME
    app_install_dir.mkdir(parents=True, exist_ok=True)

    # Copy application
    app_source = DIST_DIR / APP_NAME
    for item in app_source.iterdir():
        if item.is_file():
            shutil.copy2(item, app_install_dir)
        elif item.is_dir():
            shutil.copytree(item, app_install_dir / item.name, dirs_exist_ok=True)

    # Copy icon if it exists
    icon_src = None
    for icon_name in ["qrew.png", "Qrew.png", "qrew_desktop_500x500.png"]:
        icon_path = ICONS_DIR / icon_name
        if icon_path.exists():
            icon_src = icon_path
            break

    if icon_src:
        shutil.copy2(icon_src, app_install_dir / "icon.png")

    # Desktop file
    desktop_dir = pkg_dir / "usr" / "share" / "applications"
    desktop_dir.mkdir(parents=True, exist_ok=True)

    desktop_content = f"""[Desktop Entry]
Name={APP_NAME}
Comment={APP_DESCRIPTION}
Exec=/opt/{APP_NAME}/{APP_NAME}
Icon=/opt/{APP_NAME}/icon.png
Terminal=false
Type=Application
Categories=AudioVideo;Audio;Engineering;
"""

    with open(desktop_dir / f"{APP_NAME.lower()}.desktop", "w") as f:
        f.write(desktop_content)

    # Launcher script
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


def create_rpm_spec():
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
Icon=/opt/{APP_NAME}/icon.png
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


def create_rpm_sources(rpm_build):
    """Create source tarball for RPM"""
    print("Creating RPM source tarball...")

    sources_dir = rpm_build / "SOURCES"
    app_dir = DIST_DIR / APP_NAME

    # Create a directory with the expected name
    temp_dir = BUILD_DIR / f"{APP_NAME.lower()}-{APP_VERSION}"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    shutil.copytree(app_dir, temp_dir)

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


def create_tarball():
    """Create a tar.gz distribution"""
    print("Creating tar.gz archive...")

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
    if not ensure_directories():
        sys.exit(1)

    if build_linux_installer():
        print("SUCCESS: Linux packages build completed")
    else:
        print("ERROR: Linux packages build failed")
        sys.exit(1)
