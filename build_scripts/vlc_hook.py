
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
