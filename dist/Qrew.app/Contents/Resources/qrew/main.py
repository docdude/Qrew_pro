#!/usr/bin/env python3
"""
Main entry point for Qrew application
"""
import os
import sys
import time
import platform
import signal
from threading import Thread
from PyQt5.QtWidgets import QApplication

# Add the frozen application path for imports
if getattr(sys, "frozen", False):
    # Running as PyInstaller bundle
    application_path = sys._MEIPASS
    sys.path.insert(0, application_path)
    sys.path.insert(0, os.path.join(application_path, "qrew"))

# Force Windows to use IPv4 for all requests
if platform.system() == "Windows":
    import socket

    # import requests.packages.urllib3.util.connection as urllib3_cn  # this is for older versions
    import urllib3.util.connection as urllib3_cn

    def allowed_gai_family():
        """Force IPv4 only for Windows"""
        return socket.AF_INET  # Force IPv4 only

    urllib3_cn.allowed_gai_family = allowed_gai_family


try:
    from .Qrew import MainWindow, wait_for_rew_qt, shutdown_handler
    from .Qrew_api_helper import initialize_rew_subscriptions
    from .Qrew_message_handlers import run_flask_server
    from .Qrew_styles import GLOBAL_STYLE
except ImportError:
    try:
        from Qrew import MainWindow, wait_for_rew_qt, shutdown_handler
        from Qrew_api_helper import initialize_rew_subscriptions
        from Qrew_message_handlers import run_flask_server
        from Qrew_styles import GLOBAL_STYLE
    except ImportError:
        # Try with qrew prefix
        import qrew.Qrew as QrewModule
        from qrew.Qrew_api_helper import initialize_rew_subscriptions
        from qrew.Qrew_message_handlers import run_flask_server
        from qrew.Qrew_styles import GLOBAL_STYLE

        MainWindow = QrewModule.MainWindow
        wait_for_rew_qt = QrewModule.wait_for_rew_qt
        shutdown_handler = QrewModule.shutdown_handler


def main():
    """Main application entry point"""
    try:
        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)

        # Start Flask in a background thread
        flask_thread = Thread(target=run_flask_server, daemon=True)
        flask_thread.start()

        time.sleep(1)

        # Create Qt application
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        app.setStyleSheet(GLOBAL_STYLE)
        # Check REW connection
        wait_for_rew_qt()

        # Initialize all subscriptions
        initialize_rew_subscriptions()

        # Create and show main window
        window = MainWindow()
        window.show()

        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
