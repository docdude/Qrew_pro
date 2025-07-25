# Qrew_settings.py  -----------------------------------------------
import json
import threading
import pathlib
import sys

# Handle PyInstaller bundled vs development environments
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # PyInstaller environment - try multiple locations for settings.json in priority order:
    # 1. Root of the executable directory (for user-editable settings)
    # 2. Inside the qrew subdirectory in _MEIPASS
    # 3. Root of _MEIPASS

    locations = [
        pathlib.Path(sys.executable).parent / "settings.json",  # Exe directory
        pathlib.Path(sys._MEIPASS) / "qrew" / "settings.json",  # _MEIPASS/qrew
        pathlib.Path(sys._MEIPASS) / "settings.json",  # _MEIPASS root
    ]

    found = False
    for loc in locations:
        if loc.exists():
            _FILE = loc
            print(f"Using settings.json from: {_FILE}")
            found = True
            break

    if not found:
        # Default to executable dir for writing settings
        _FILE = locations[0]  # Exe directory is best for writing
        print(f"No settings.json found, will create at: {_FILE}")
else:
    # Development environment - settings.json is next to this .py file
    _FILE = pathlib.Path(__file__).with_name("settings.json")
    print(f"Using settings.json from development path: {_FILE}")

_lock = threading.Lock()
_data = None  # lazy-loaded cache


def _load() -> dict:
    global _data
    if _data is None:
        try:
            with _FILE.open() as fh:
                _data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            # Create default settings if file doesn't exist
            _data = {
                "vlc_backend": "auto",
                "show_vlc_gui": False,
                "show_tooltips": True,
                "auto_pause_on_quality_issue": False,
                "save_after_repeat": False,
                "use_light_theme": False,
                "speaker_config": "Manual Select",
            }
            # Try to create the settings file
            try:
                _flush()
            except OSError:
                print(f"Warning: Could not create settings file at {_FILE}")
    return _data


def _flush():
    try:
        # Ensure parent directory exists
        _FILE.parent.mkdir(parents=True, exist_ok=True)
        with _FILE.open("w") as fh:
            json.dump(_data, fh, indent=2)
    except OSError as e:
        print(f"Warning: Could not save settings to {_FILE}: {e}")


# --------------- public API -----------------


def get(key, default=None):
    return _load().get(key, default)


def set(key, value):
    with _lock:
        _load()[key] = value
        _flush()


def as_dict() -> dict:
    """Return a **copy** of all current settings."""
    return dict(_load())


def update_many(mapping: dict):
    """Atomically update several keys at once."""
    with _lock:
        _load().update(mapping)
        _flush()
