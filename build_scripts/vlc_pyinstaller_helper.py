"""Helper module to include VLC libraries in PyInstaller builds"""

import os
import sys
import platform
import shutil
from pathlib import Path


def get_vlc_libraries():
    """Find VLC libraries for current platform to include in PyInstaller spec"""
    system = platform.system()
    binaries = []

    if system == "Windows":
        # Find Windows VLC location
        vlc_path = find_windows_vlc()
        if vlc_path:
            plugin_path = os.path.join(os.path.dirname(vlc_path), "plugins")
            binaries.append((vlc_path, "."))
            binaries.append(
                (os.path.join(os.path.dirname(vlc_path), "libvlccore.dll"), ".")
            )
            # Add plugins directory
            if os.path.exists(plugin_path):
                for root, _, files in os.walk(plugin_path):
                    for file in files:
                        if file.endswith(".dll"):
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(
                                os.path.dirname(full_path), os.path.dirname(plugin_path)
                            )
                            dest_dir = os.path.join("plugins", rel_path)
                            binaries.append((full_path, dest_dir))

    elif system == "Darwin":
        # macOS VLC location
        vlc_dir = "/Applications/VLC.app/Contents/MacOS"
        if os.path.exists(vlc_dir):
            lib_dir = os.path.join(vlc_dir, "lib")
            binaries.append((os.path.join(lib_dir, "libvlc.dylib"), "."))
            binaries.append((os.path.join(lib_dir, "libvlccore.dylib"), "."))
            # Add plugins directory
            plugins_dir = os.path.join(vlc_dir, "plugins")
            if os.path.exists(plugins_dir):
                for root, _, files in os.walk(plugins_dir):
                    for file in files:
                        if file.endswith(".dylib"):
                            full_path = os.path.join(root, file)
                            rel_path = os.path.relpath(
                                os.path.dirname(full_path), plugins_dir
                            )
                            dest_dir = os.path.join("plugins", rel_path)
                            binaries.append((full_path, dest_dir))

    elif system == "Linux":
        # Linux - try to find libvlc.so
        vlc_lib = find_linux_vlc()
        if vlc_lib:
            lib_dir = os.path.dirname(vlc_lib)
            vlc_core_lib = os.path.join(lib_dir, "libvlccore.so")
            if os.path.exists(vlc_core_lib):
                binaries.append((vlc_lib, "."))
                binaries.append((vlc_core_lib, "."))

            # Add plugins - common Linux paths
            plugins_dirs = [
                "/usr/lib/x86_64-linux-gnu/vlc/plugins",
                "/usr/lib/vlc/plugins",
                os.path.join(lib_dir, "vlc/plugins"),
            ]

            for plugins_dir in plugins_dirs:
                if os.path.exists(plugins_dir):
                    for root, _, files in os.walk(plugins_dir):
                        for file in files:
                            if file.endswith(".so"):
                                full_path = os.path.join(root, file)
                                rel_path = os.path.relpath(
                                    os.path.dirname(full_path), plugins_dir
                                )
                                dest_dir = os.path.join("plugins", rel_path)
                                binaries.append((full_path, dest_dir))
                    break  # Use first plugins directory found

    return binaries


def find_windows_vlc():
    """Find VLC executable on Windows"""
    try:
        import winreg

        for key in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                reg_key = winreg.OpenKey(key, r"Software\VideoLAN\VLC")
                install_dir = winreg.QueryValueEx(reg_key, "InstallDir")[0]
                vlc_exe = os.path.join(install_dir, "libvlc.dll")
                if os.path.exists(vlc_exe):
                    return vlc_exe
            except:
                pass
    except:
        pass

    # Try common locations
    common_locations = [
        os.path.join(
            os.environ.get("PROGRAMFILES", "C:\\Program Files"),
            "VideoLAN",
            "VLC",
            "libvlc.dll",
        ),
        os.path.join(
            os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"),
            "VideoLAN",
            "VLC",
            "libvlc.dll",
        ),
    ]

    for location in common_locations:
        if os.path.exists(location):
            return location

    return None


def find_linux_vlc():
    """Find libvlc.so on Linux systems"""
    common_locations = [
        "/usr/lib/x86_64-linux-gnu/libvlc.so",
        "/usr/lib/libvlc.so",
        "/usr/local/lib/libvlc.so",
    ]

    for location in common_locations:
        if os.path.exists(location):
            return location

    # Try to find using ldconfig
    try:
        result = subprocess.run(["ldconfig", "-p"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "libvlc.so" in line:
                parts = line.split(" => ")
                if len(parts) >= 2:
                    lib_path = parts[1].strip()
                    if os.path.exists(lib_path):
                        return lib_path
    except:
        pass

    return None


def get_runtime_hooks():
    """Get path to runtime hook for VLC"""
    hook_content = """
# PyInstaller runtime hook to configure VLC paths
import os
import sys
import platform

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Running in PyInstaller bundle
    if platform.system() == "Darwin":
        # Set VLC plugin path for macOS
        os.environ['VLC_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'plugins')
    elif platform.system() == "Windows":
        # Set VLC plugin path for Windows
        os.environ['VLC_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'plugins')
    elif platform.system() == "Linux":
        # Set VLC plugin path for Linux
        os.environ['VLC_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'plugins')
"""

    # Write hook to file
    hook_path = Path(__file__).parent / "vlc_hook.py"
    with open(hook_path, "w") as f:
        f.write(hook_content)

    return str(hook_path)
