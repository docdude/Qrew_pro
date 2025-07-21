"""
Linux-specific build script
"""
import os
import subprocess
import shutil
import tempfile
from pathlib import Path
from build_config import *

def build_linux_installer():
    """Build Linux packages (.deb and .rpm)"""
    print("Building Linux packages...")
    
    success = True
    if shutil.which("dpkg-deb"):
        success &= build_deb_package()
    else:
        print("Warning: dpkg-deb not found, skipping .deb package")
    
    if shutil.which("rpmbuild"):
        success &= build_rpm_package()
    else:
        print("Warning: rpmbuild not found, skipping .rpm package")
    
    return success

def build_deb_package():
    """Build .deb package"""
    print("Building .deb package...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        pkg_dir = temp_path / f"{APP_NAME.lower()}-{APP_VERSION}"
        
        # Create package structure
        create_deb_structure(pkg_dir)
        
        # Build package
        deb_file = DIST_DIR / f"{APP_NAME.lower()}-{APP_VERSION}-linux.deb"
        cmd = ["dpkg-deb", "--build", str(pkg_dir), str(deb_file)]
        
        result = subprocess.run(cmd)
        if result.returncode == 0:
            print(f"Successfully created: {deb_file}")
            return True
        else:
            print("Failed to create .deb package")
            return False

def create_deb_structure(pkg_dir):
    """Create Debian package directory structure"""
    # Create directories
    bin_dir = pkg_dir / "usr" / "bin"
    app_dir = pkg_dir / "opt" / APP_NAME.lower()
    desktop_dir = pkg_dir / "usr" / "share" / "applications"
    icon_dir = pkg_dir / "usr" / "share" / "pixmaps"
    debian_dir = pkg_dir / "DEBIAN"
    
    for directory in [bin_dir, app_dir, desktop_dir, icon_dir, debian_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Copy application files
    app_source = DIST_DIR / APP_NAME
    if app_source.exists():
        shutil.copytree(app_source, app_dir / APP_NAME, dirs_exist_ok=True)
    
    # Create launcher script
    launcher_script = bin_dir / APP_NAME.lower()
    with open(launcher_script, 'w') as f:
        f.write(f'''#!/bin/bash
cd /opt/{APP_NAME.lower()}/{APP_NAME}
./{APP_NAME}
''')
    launcher_script.chmod(0o755)
    
    # Copy icon
    icon_source = get_icon_for_platform()
    if Path(icon_source).exists():
        shutil.copy2(icon_source, icon_dir / f"{APP_NAME.lower()}.png")
    
    # Create desktop file
    desktop_file = desktop_dir / f"{APP_NAME.lower()}.desktop"
    with open(desktop_file, 'w') as f:
        f.write(create_desktop_file())
    
    # Create control file
    control_file = debian_dir / "control"
    with open(control_file, 'w') as f:
        f.write(create_deb_control())

def build_rpm_package():
    """Build .rpm package"""
    print("Building .rpm package...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create RPM spec file
        spec_content = create_rpm_spec()
        spec_file = temp_path / f"{APP_NAME.lower()}.spec"
        
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        # Create source tarball
        create_rpm_sources(temp_path)
        
        # Build RPM
        cmd = [
            "rpmbuild",
            "-ba",
            "--define", f"_topdir {temp_path}",
            str(spec_file)
        ]
        
        result = subprocess.run(cmd)
        if result.returncode == 0:
            # Copy built RPM to dist directory
            rpm_dir = temp_path / "RPMS" / "x86_64"
            for rpm_file in rpm_dir.glob("*.rpm"):
                target = DIST_DIR / f"{APP_NAME.lower()}-{APP_VERSION}-linux.rpm"
                shutil.copy2(rpm_file, target)
                print(f"Successfully created: {target}")
            return True
        else:
            print("Failed to create .rpm package")
            return False

def create_desktop_file():
    """Create .desktop file for Linux"""
    return f'''[Desktop Entry]
Version=1.0
Type=Application
Name={APP_NAME}
Comment={APP_DESCRIPTION}
Exec={APP_NAME.lower()}
Icon={APP_NAME.lower()}
Terminal=false
Categories=AudioVideo;Audio;Science;
StartupNotify=true
'''

def create_deb_control():
    """Create Debian control file"""
    return f'''Package: {APP_NAME.lower()}
Version: {APP_VERSION}
Section: science
Priority: optional
Architecture: amd64
Depends: python3, python3-pyqt5, vlc
Maintainer: {APP_AUTHOR} <your.email@example.com>
Description: {APP_DESCRIPTION}
 Automated loudspeaker measurement system using REW API.
 Provides GUI interface for capturing and processing speaker measurements.
'''

def create_rpm_spec():
    """Create RPM spec file"""
    return f'''Name:           {APP_NAME.lower()}
Version:        {APP_VERSION}
Release:        1%{{?dist}}
Summary:        {APP_DESCRIPTION}

License:        GPL-3.0
URL:            {APP_URL}
Source0:        %{{name}}-%{{version}}.tar.gz

BuildArch:      x86_64
Requires:       python3, python3-qt5, vlc

%description
{APP_DESCRIPTION}
Automated loudspeaker measurement system using REW API.

%prep
%setup -q

%build
# Nothing to build

%install
mkdir -p %{{buildroot}}/opt/{APP_NAME.lower()}
mkdir -p %{{buildroot}}/usr/bin
mkdir -p %{{buildroot}}/usr/share/applications
mkdir -p %{{buildroot}}/usr/share/pixmaps

cp -r * %{{buildroot}}/opt/{APP_NAME.lower()}/

# Create launcher script
cat > %{{buildroot}}/usr/bin/{APP_NAME.lower()} << EOF
#!/bin/bash
cd /opt/{APP_NAME.lower()}/{APP_NAME}
./{APP_NAME}
EOF
chmod +x %{{buildroot}}/usr/bin/{APP_NAME.lower()}

# Install desktop file
cat > %{{buildroot}}/usr/share/applications/{APP_NAME.lower()}.desktop << EOF
{create_desktop_file()}
EOF

# Install icon
cp {get_icon_for_platform()} %{{buildroot}}/usr/share/pixmaps/{APP_NAME.lower()}.png

%files
/opt/{APP_NAME.lower()}/*
/usr/bin/{APP_NAME.lower()}
/usr/share/applications/{APP_NAME.lower()}.desktop
/usr/share/pixmaps/{APP_NAME.lower()}.png

%changelog
* Wed Jan 03 2025 {APP_AUTHOR} - {APP_VERSION}-1
- Initial package
'''

def create_rpm_sources(build_dir):
    """Create source tarball for RPM build"""
    sources_dir = build_dir / "SOURCES"
    sources_dir.mkdir(exist_ok=True)
    
    # Copy application files
    app_source = DIST_DIR / APP_NAME
    if app_source.exists():
        tarball = sources_dir / f"{APP_NAME.lower()}-{APP_VERSION}.tar.gz"
        cmd = ["tar", "-czf", str(tarball), "-C", str(DIST_DIR), APP_NAME]
        subprocess.run(cmd, check=True)
