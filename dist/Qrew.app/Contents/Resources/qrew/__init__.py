"""
Qrew - Automated loudspeaker measurement system using REW API

This package provides a PyQt5-based GUI for automated speaker measurements
through the Room EQ Wizard (REW) API.
"""

__version__ = "1.0.0"
__author__ = "Juan F. Loya"

# Import main components for easier access
from .Qrew import MainWindow, shutdown_handler
from .Qrew_api_helper import check_rew_connection, initialize_rew_subscriptions
from .Qrew_message_handlers import run_flask_server, stop_flask_server
#from .Qrew_common import SPEAKER_LABELS, SPEAKER_CONFIGS

__all__ = [
    "MainWindow",
    "shutdown_handler",
    "check_rew_connection", 
    "initialize_rew_subscriptions",
    "run_flask_server",
    "stop_flask_server",

]
