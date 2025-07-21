"""
VSCode integration utilities
"""
import json
import os
import subprocess
from pathlib import Path
import datetime

def create_status_bar_items():
    """Create custom status bar items for build status"""
    return {
        "qrew.build.status": {
            "text": "$(tools) Build",
            "tooltip": "Build Qrew installers",
            "command": "qrew.build.platform"
        },
        "qrew.run.status": {
            "text": "$(play) Run",
            "tooltip": "Run Qrew in debug mode",
            "command": "qrew.run.debug"
        }
    }

def update_build_status(status):
    """Update build status in VSCode"""
    status_file = Path(".vscode") / "build_status.json"
    with open(status_file, 'w') as f:
        json.dump({"status": status, "timestamp": str(datetime.now())}, f)
