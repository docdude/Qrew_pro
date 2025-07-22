"""
Linux packages build script
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from build_config import *


def build_linux_installer():
    """Build Linux .deb and .rpm packages"""
    print("Building Linux packages...")

    app_dir = DIST_DIR / APP_NAME
    if not app_dir.exists():
        print("❌ Linux app directory not found. Run PyInstaller first.")
        return False

    success = True
    if not build_deb_package():
        success = False
    if not build_rpm_package():
        success = False

    return success


def build_deb_package():
    """Build Debian .deb package"""
    print("Building .deb package...")

    # Create package structure
    pkg_dir = BUILD_DIR / f"{APP_NAME}-{APP_VERSION}_deb"
    create_deb_structure(pkg_dir)

    # Build package
    try:
        cmd = [
            "dpkg-deb",
            "--build",
            str(pkg_dir),
            str(DIST_DIR / f"{APP_NAME}-{APP_VERSION}-linux.deb"),
        ]
        subprocess.run(cmd, check=True)
        print("✅ .deb package created")
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"❌ .deb build failed: {e}")
        return False


def build_rpm_package():
    """Build RPM package"""
    print("Building .rpm package...")

    # Create RPM build directories
    rpm_build = BUILD_DIR / "rpm_build"
    for subdir in ["SPECS", "SOURCES", "BUILD", "RPMS", "SRPMS"]:
        (rpm_build / subdir).mkdir(parents=True, exist_ok=True)

    # Create spec file
    spec_content = create_rpm_spec()
    spec_file = rpm_build / "SPECS" / f"{APP_NAME}.spec"
    with open(spec_file, "w") as f:
        f.write(spec_content)

    # Create source tarball
    create_rpm_sources(rpm_build)

    try:
        cmd = ["rpmbuild", "--define", f"_topdir {rpm_build}", "-ba", str(spec_file)]
        subprocess.run(cmd, check=True)

        # Copy RPM to dist
        for rpm_file in (rpm_build / "RPMS").rglob("*.rpm"):
            shutil.copy2(rpm_file, DIST_DIR / f"{APP_NAME}-{APP_VERSION}-linux.rpm")
            break

        print("✅ .rpm package created")
        return True
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"❌ .rpm build failed: {e}")
        return False


def create_deb_structure(pkg_dir):
    """Create Debian package directory structure"""
    pkg_dir.mkdir(parents=True, exist_ok=True)

    # DEBIAN control directory
    debian_dir = pkg_dir / "DEBIAN"
    debian_dir.mkdir(exist_ok=True)

    # Control file
    control_content = f"""Package: {APP_NAME.lower()}
Version: {APP_VERSION}
Section: utils
Priority: optional
Architecture: amd64
Maintainer: {APP_AUTHOR}
Description: {APP_DESCRIPTION}
 Automated loudspeaker measurement system using REW API.
"""

    with open(debian_dir / "control", "w") as f:
        f.write(control_content)

    # Application files
    app_install_dir = pkg_dir / "opt" / APP_NAME
    app_install_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(DIST_DIR / APP_NAME, app_install_dir, dirs_exist_ok=True)

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
Categories=AudioVideo;Audio;
"""

    with open(desktop_dir / f"{APP_NAME.lower()}.desktop", "w") as f:
        f.write(desktop_content)

    # Launcher script
    bin_dir = pkg_dir / "usr" / "local" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    launcher_content = f"""#!/bin/bash
cd /opt/{APP_NAME}
./{APP_NAME} "$@"
"""

    launcher_file = bin_dir / APP_NAME.lower()
    with open(launcher_file, "w") as f:
        f.write(launcher_content)
    launcher_file.chmod(0o755)


def create_rpm_spec():
    """Create RPM spec file"""
    return f"""
Name: {APP_NAME.lower()}
Version: {APP_VERSION}
Release: 1%{{?dist}}
Summary: {APP_DESCRIPTION}

License: GPL-3.0
URL: {APP_URL}
Source0: %{{name}}-%{{version}}.tar.gz

%description
{APP_DESCRIPTION}

%prep
%setup -q

%install
mkdir -p %{{buildroot}}/opt/{APP_NAME}
cp -r * %{{buildroot}}/opt/{APP_NAME}/

mkdir -p %{{buildroot}}/usr/local/bin
cat > %{{buildroot}}/usr/local/bin/{APP_NAME.lower()} << 'EOF'
#!/bin/bash
cd /opt/{APP_NAME}
./{APP_NAME} "$@"
EOF
chmod +x %{{buildroot}}/usr/local/bin/{APP_NAME.lower()}

%files
/opt/{APP_NAME}/
/usr/local/bin/{APP_NAME.lower()}

%changelog
* %(date "+%%a %%b %%d %%Y") {APP_AUTHOR} - {APP_VERSION}-1
- Initial release
"""


def create_rpm_sources(rpm_build):
    """Create source tarball for RPM"""
    sources_dir = rpm_build / "SOURCES"
    app_dir = DIST_DIR / APP_NAME

    # Create tarball
    tarball_name = f"{APP_NAME.lower()}-{APP_VERSION}.tar.gz"
    cmd = [
        "tar",
        "-czf",
        str(sources_dir / tarball_name),
        "-C",
        str(app_dir.parent),
        app_dir.name,
    ]
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    build_linux_installer()
