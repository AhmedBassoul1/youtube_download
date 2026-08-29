"""Thread-safe JSON storage for download history and app settings.

Fixes the original /log endpoint problems:
- no lock -> corrupted JSON under concurrent writes
- json.load() crash on empty/corrupted file
- history stored as a bare URL list (no metadata)
"""
import json
import os
import threading
from datetime import datetime, timezone

_LOCK = threading.Lock()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "last_folder": "",                 # TODO: remember last chosen folder
    "filename_template": "%(title)s.%(ext)s",
    "duplicate_policy": "skip",        # skip | overwrite | rename
    "post_hook": "",                   # TODO: post-download hooks
    "channel_profiles": {},            # TODO: per-channel quality profiles
    "max_parallel_downloads": 3,       # TODO: parallel downloads
    "cookies_browser": "",             # "firefox" (recommended on Linux) | "chrome" | "" (disabled)
    "cookies_file": "",                # path to a cookies.txt (Netscape format) — takes priority
}


def _read_json(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return fallback


def _write_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)  # atomic write -> no half-written files


# ---------------- History ----------------

def get_history(limit=100):
    with _LOCK:
        history = _read_json(HISTORY_FILE, [])
        if not isinstance(history, list):
            history = []
        # migrate old format (bare URL strings) transparently
        history = [h if isinstance(h, dict) else {"url": h} for h in history]
        return history[-limit:][::-1]  # newest first


def add_history_entry(url, title="", folder="", status="completed", is_audio=False):
    entry = {
        "url": url,
        "title": title,
        "folder": folder,
        "status": status,
        "is_audio": is_audio,
        "date": datetime.now(timezone.utc).isoformat(),
    }
    with _LOCK:
        history = _read_json(HISTORY_FILE, [])
        if not isinstance(history, list):
            history = []
        # migrate old format (bare URL strings) transparently
        history = [h if isinstance(h, dict) else {"url": h} for h in history]
        history.append(entry)
        _write_json(HISTORY_FILE, history[-500:])  # cap file size
    return entry


def clear_history():
    with _LOCK:
        _write_json(HISTORY_FILE, [])


# ---------------- Settings ----------------

def get_settings():
    with _LOCK:
        settings = _read_json(SETTINGS_FILE, {})
        if not isinstance(settings, dict):
            settings = {}
        merged = {**DEFAULT_SETTINGS, **settings}
        return merged


def update_settings(patch: dict):
    with _LOCK:
        settings = _read_json(SETTINGS_FILE, {})
        if not isinstance(settings, dict):
            settings = {}
        for key, value in patch.items():
            if key in DEFAULT_SETTINGS:
                settings[key] = value
        merged = {**DEFAULT_SETTINGS, **settings}
        _write_json(SETTINGS_FILE, merged)
        return merged


def save_channel_profile(channel: str, profile: dict):
    with _LOCK:
        settings = _read_json(SETTINGS_FILE, {})
        if not isinstance(settings, dict):
            settings = {}
        profiles = settings.get("channel_profiles", {})
        profiles[channel] = profile
        settings["channel_profiles"] = profiles
        merged = {**DEFAULT_SETTINGS, **settings}
        _write_json(SETTINGS_FILE, merged)
        return merged


def get_channel_profile(channel: str):
    return get_settings().get("channel_profiles", {}).get(channel)
