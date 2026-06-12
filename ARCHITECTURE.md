# Architecture du projet — YouTube Downloader v2

## Arborescence

```
youtube_download/
│
├── api/
│   ├── __init__.py
│   └── routes.py            # Tous les endpoints HTTP
│
├── server/
│   ├── __init__.py
│   ├── info.py              # Métadonnées : preview & playlist (thumbnails, durées)
│   ├── options.py           # Options yt_dlp (formats, sous-titres, templates, doublons)
│   ├── jobs.py              # Jobs : parallélisme, progress, annulation, post-hooks
│   └── storage.py           # history.json + settings.json (thread-safe, atomique)
│
├── front/
│   ├── index.html           # UI (preview, playlist, options avancées, jobs, historique)
│   ├── script.js            # Logique frontend
│   ├── style.css            # Styles (glassmorphisme + composants v2)
│   └── favicon.ico
│
├── main.py                  # Point d'entrée FastAPI (CORS restreint)
├── main_desktop.py          # Launcher pour le build .exe (PyInstaller)
├── requirements.txt
├── README.md
├── TODO.md                  # Tâches cochées
├── BUILDING.md              # Instructions release exe/apk
├── history.json             # Historique des téléchargements
└── settings.json            # Créé au premier lancement
```

---

## `README.md`

```markdown
# 🎬 YouTube Downloader

A sleek, modern YouTube video & audio downloader with a glassmorphic web UI and a FastAPI backend powered by `yt-dlp` (Python API — no subprocess).

## ✨ Features

- 🎥 **Video downloads** — 4K / 1080p / 720p / 480p / Data Saver, output as **MP4 / MKV / WebM**.
- 🎵 **Audio-only mode** — **MP3 / M4A / OPUS / FLAC** at best bitrate.
- ✅ **Selective playlist downloading** — checkboxes **with thumbnails & durations**, or range syntax `1-10, 15, 20-30`.
- 📊 **Real-time progress** — percent, speed, ETA, per-item counter, with a **Cancel** button.
- ⚡ **Parallel downloads** — multiple jobs at once (configurable, default 3).
- 🖼️ **Video preview** — thumbnail, title, channel and duration before downloading.
- 📜 **Subtitles** — pick languages (e.g. `en,fr`), includes auto-generated subs.
- 🗂️ **Duplicate detection** — Skip / Overwrite / Rename.
- ✏️ **Custom filename template** — safe subset of yt-dlp fields (`%(title)s`, `%(uploader)s`, …).
- 📂 **Smart folders** — auto-named after the playlist/video, **"Open folder"** button, **last folder remembered**.
- 🕘 **Download history** — persisted JSON with title, folder, status, date.
- 👤 **Per-channel profiles** — save quality/format per channel, auto-applied on next paste.
- 📄 **Batch mode** — load a `.txt` of URLs and queue them all.
- 🔁 **Post-download hooks** — run a custom command after each job (`$DOWNLOAD_FOLDER` env var).
- ⬆️ **yt-dlp auto-update** — one button in the UI.
- 🔔 **Desktop notifications** via `plyer`.

## 📁 Project Structure

```
youtube_download/
│
├── api/
│   └── routes.py        # All HTTP endpoints
│
├── server/
│   ├── info.py          # Metadata: preview & playlist (thumbnails, durations)
│   ├── options.py       # Builds yt_dlp option dicts (formats, subs, templates…)
│   ├── jobs.py          # Job manager: parallel, progress, cancel, hooks
│   └── storage.py       # Thread-safe history.json + settings.json
│
├── front/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── main.py              # FastAPI app entry point
├── main_desktop.py      # Launcher for the .exe build
├── BUILDING.md          # exe/apk release notes
└── requirements.txt
```

## 🚀 Installation

```
git clone https://github.com/AhmedBassoul1/youtube_download.git
cd youtube_download
python -m venv venv
source venv/bin/activate        # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

> ⚠️ **FFmpeg** must be installed — required for merging and audio extraction.

## 🎯 Usage

```
uvicorn main:app --reload          # backend  -> http://127.0.0.1:8000
cd front && python3 -m http.server 8080   # frontend -> http://127.0.0.1:8080
```

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/info?url=` | Preview (video) or listing (playlist) with thumbnails/durations + channel profile |
| POST | `/download` | Start a job (all options in body) |
| POST | `/download-batch` | Start one job per URL |
| GET | `/status/{job_id}` | `queued/processing/completed/failed/cancelled` + progress `{percent, speed, eta, item, total_items, filename}` |
| POST | `/cancel/{job_id}` | Cancel a running job |
| GET | `/jobs` | All jobs |
| POST | `/open-folder` | Open a completed download folder in the OS file manager |
| GET/DELETE | `/history` | Read / clear download history |
| GET/PATCH | `/settings` | last_folder, filename_template, duplicate_policy, post_hook, max_parallel_downloads |
| POST | `/update-ytdlp` | Upgrade yt-dlp via pip |
| GET | `/pick-folder` | Native folder picker |

**POST /download body:**
```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "is_audio": false,
  "quality": "1080p",
  "output_dir": null,
  "playlist_items": "1-10,15",
  "selected_indices": null,
  "video_container": "mp4",
  "audio_format": "mp3",
  "subtitles_langs": ["en", "fr"],
  "filename_template": "%(title)s.%(ext)s",
  "duplicate_policy": "skip",
  "save_channel_profile": false
}
```

## ⚠️ Disclaimer

This tool is intended for **personal use only**. Downloading copyrighted material without permission may violate YouTube's Terms of Service and applicable copyright laws. Use responsibly.

Made with ❤️ and a lot of ☕

```

---

## `TODO.md`

```markdown
# YouTube Downloader — TODO

## Quick wins
- [x] Real-time download progress bar
- [x] Cancel button for running downloads
- [x] Download history (persisted in JSON)
- [x] "Open folder" button on completed downloads
- [x] Thumbnails in playlist panel
- [x] Video duration in playlist panel
- [x] Remember last chosen folder

## Medium effort
- [x] Playlist range syntax (e.g. "1-10, 15, 20-30")
- [x] Output format selection (MP4 / MKV / WebM, MP3 / M4A / OPUS / FLAC)
- [x] Subtitles download with language selection
- [x] Customizable filename template
- [x] Duplicate detection (Skip / Overwrite / Rename)
- [x] Parallel downloads (multiple jobs at once)

## Bigger features
- [x] yt-dlp auto-update button
- [x] Video preview before download (thumbnail, title, channel, duration)
- [x] Per-channel quality profiles
- [x] Batch mode (load URLs from .txt file)
- [x] Post-download hooks (custom command after each download)

## Releases
- [ ] exe and apk Releases — build instructions in BUILDING.md
      (exe via PyInstaller; an APK is not applicable to a Python/FastAPI
      desktop app — see notes in BUILDING.md)

```

---

## `BUILDING.md`

```markdown
# Building releases

## Windows .exe (PyInstaller)

```powershell
pip install pyinstaller
pyinstaller --onefile --name yt-downloader ^
  --add-data "front;front" ^
  --hidden-import uvicorn.logging ^
  --hidden-import uvicorn.loops.auto ^
  --hidden-import uvicorn.protocols.http.auto ^
  main_desktop.py
```

`main_desktop.py` (included in the repo) starts the API and opens the UI in the
default browser. FFmpeg must be installed on the target machine, or bundled
with `--add-binary "C:\path\to\ffmpeg.exe;."`.

macOS / Linux equivalents: same command with `:` instead of `;` in `--add-data`.

## APK

This project is a Python/FastAPI desktop app: packaging it as a native Android
APK is not practical (yt-dlp + FFmpeg + a local web server inside Android would
require a rewrite with Kivy/Chaquopy or Termux packaging). Recommended
alternatives:

1. Use the web UI from a phone browser pointing at the desktop server on the
   local network (`uvicorn main:app --host 0.0.0.0`).
2. Wrap the frontend in a thin WebView app (Capacitor / TWA) that talks to a
   self-hosted server.

```

---

## `requirements.txt`

```text
fastapi
uvicorn[standard]
yt-dlp
plyer

```

---

## `main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as download_router

app = FastAPI(title="YouTube Downloader API", version="2.0.0")

# Restricted CORS: only the local frontend (was "*" + credentials, an invalid
# and insecure combination).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080", "http://127.0.0.1:8080",
        "http://localhost:5500", "http://127.0.0.1:5500",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(download_router)


@app.get("/")
def read_root():
    return {"message": "Server is running. Access docs at /docs"}

```

---

## `main_desktop.py`

```python
"""Desktop launcher used for the PyInstaller .exe build (see BUILDING.md).

Starts the FastAPI backend, serves the frontend, and opens the browser.
"""
import os
import sys
import threading
import webbrowser

import uvicorn
from fastapi.staticfiles import StaticFiles

from main import app


def _front_dir():
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "front")


app.mount("/app", StaticFiles(directory=_front_dir(), html=True), name="front")


def _open_ui():
    webbrowser.open("http://127.0.0.1:8000/app/")


if __name__ == "__main__":
    threading.Timer(1.5, _open_ui).start()
    uvicorn.run(app, host="127.0.0.1", port=8000)

```

---

## `api/routes.py`

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import re
import sys
import subprocess

from server import info as info_engine
from server import options as opt_engine
from server import storage
from server.jobs import manager

router = APIRouter()

_URL_RE = re.compile(
    r"^(https?://)?(www\.|m\.|music\.)?(youtube\.com|youtu\.be)/"
    r"(watch\?v=|playlist\?list=|shorts/|embed/|v/)?([a-zA-Z0-9_-]{11,34})([&?].*)?$"
)


def validate_youtube_url(url: str) -> bool:
    return bool(url) and bool(_URL_RE.match(url.strip()))


def _sanitize_folder_name(name: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name).strip().rstrip(".")
    return cleaned[:150] or "download"


def _resolve_base_dir(output_dir: Optional[str]) -> str:
    if output_dir:
        base = os.path.abspath(os.path.expanduser(output_dir))
        if not os.path.isdir(base):
            raise HTTPException(400, f"Folder does not exist: {base}")
        if not os.access(base, os.W_OK):
            raise HTTPException(400, f"Folder is not writable: {base}")
        return base
    last = storage.get_settings().get("last_folder", "")
    if last and os.path.isdir(last) and os.access(last, os.W_OK):
        return last
    return os.path.join(os.path.expanduser("~"), "Downloads") \
        if os.path.isdir(os.path.join(os.path.expanduser("~"), "Downloads")) \
        else os.getcwd()


# ---------------- Models ----------------

class DownloadRequest(BaseModel):
    url: str
    is_audio: bool = False
    quality: str = "1080p"
    output_dir: Optional[str] = None
    # range syntax string "1-10,15,20-30" OR explicit indices list (legacy)
    playlist_items: Optional[str] = None
    selected_indices: Optional[List[int]] = None
    video_container: str = "mp4"            # mp4 | mkv | webm
    audio_format: str = "mp3"               # mp3 | m4a | opus | flac
    subtitles_langs: Optional[List[str]] = None
    filename_template: Optional[str] = None
    duplicate_policy: str = "skip"          # skip | overwrite | rename
    save_channel_profile: bool = False


class BatchRequest(BaseModel):
    urls: List[str] = Field(..., min_length=1, max_length=100)
    is_audio: bool = False
    quality: str = "1080p"
    output_dir: Optional[str] = None
    video_container: str = "mp4"
    audio_format: str = "mp3"
    duplicate_policy: str = "skip"


class SettingsPatch(BaseModel):
    last_folder: Optional[str] = None
    filename_template: Optional[str] = None
    duplicate_policy: Optional[str] = None
    post_hook: Optional[str] = None
    max_parallel_downloads: Optional[int] = None


class OpenFolderRequest(BaseModel):
    path: str


# ---------------- Info / preview ----------------

@router.get("/info")
async def get_info(url: str):
    """Video preview OR playlist listing, with thumbnails + durations.
    If a per-channel profile exists, it is returned alongside."""
    if not validate_youtube_url(url):
        raise HTTPException(400, "Invalid YouTube URL")
    try:
        data = info_engine.get_media_info(url)
    except Exception as e:
        raise HTTPException(502, f"Could not fetch metadata: {e}")
    profile = storage.get_channel_profile(data.get("channel", "")) \
        if data.get("channel") else None
    data["channel_profile"] = profile
    return data


@router.get("/playlist-info")
async def get_playlist_info(url: str):
    """Backward-compatible alias of /info for the old frontend."""
    data = await get_info(url)
    if not data["is_playlist"]:
        return {"is_playlist": False, "videos": []}
    return {"is_playlist": True, "playlist_title": data["title"],
            "videos": data["videos"]}


# ---------------- Download ----------------

def _start_job(url: str, req) -> str:
    if not validate_youtube_url(url):
        raise HTTPException(400, f"Invalid YouTube URL: {url}")

    playlist_items = getattr(req, "playlist_items", None)
    if playlist_items:
        if not opt_engine.validate_playlist_range(playlist_items):
            raise HTTPException(400, 'Invalid range syntax (expected e.g. "1-10,15,20-30")')
    elif getattr(req, "selected_indices", None):
        playlist_items = ",".join(str(i) for i in sorted(set(req.selected_indices)))

    base_dir = _resolve_base_dir(req.output_dir)
    storage.update_settings({"last_folder": base_dir})  # remember last folder

    try:
        title, channel = info_engine.get_title_for_folder(url)
    except Exception as e:
        raise HTTPException(502, f"Could not get title from URL: {e}")

    full_output_dir = os.path.join(base_dir, _sanitize_folder_name(title))
    os.makedirs(full_output_dir, exist_ok=True)

    if getattr(req, "save_channel_profile", False) and channel:
        storage.save_channel_profile(channel, {
            "is_audio": req.is_audio, "quality": req.quality,
            "video_container": req.video_container,
            "audio_format": req.audio_format,
        })

    settings = storage.get_settings()
    return manager.create_job({
        "url": url,
        "download_url": info_engine.normalize_to_playlist_url(url)
                        if info_engine.extract_playlist_id(url) else url,
        "title": title,
        "output_dir": full_output_dir,
        "is_audio": req.is_audio,
        "quality": req.quality,
        "video_container": req.video_container,
        "audio_format": req.audio_format,
        "playlist_items": playlist_items,
        "subtitles_langs": getattr(req, "subtitles_langs", None),
        "filename_template": getattr(req, "filename_template", None)
                             or settings.get("filename_template"),
        "duplicate_policy": getattr(req, "duplicate_policy", None)
                            or settings.get("duplicate_policy", "skip"),
    })


@router.post("/download")
async def start_download(request: DownloadRequest):
    job_id = _start_job(request.url, request)
    return {"job_id": job_id, "message": "Download started"}


@router.post("/download-batch")
async def start_batch(request: BatchRequest):
    """Batch mode: load URLs from a .txt file (parsed client-side)."""
    jobs, errors = [], []
    for url in request.urls:
        url = url.strip()
        if not url or url.startswith("#"):
            continue
        try:
            jobs.append({"url": url, "job_id": _start_job(url, request)})
        except HTTPException as e:
            errors.append({"url": url, "error": e.detail})
    return {"jobs": jobs, "errors": errors}


@router.get("/status/{job_id}")
async def get_status(job_id: str):
    return manager.get_status(job_id)


@router.get("/jobs")
async def list_jobs():
    return manager.list_jobs()


@router.post("/cancel/{job_id}")
async def cancel_job(job_id: str):
    if not manager.cancel(job_id):
        raise HTTPException(404, "Job not found or already finished")
    return {"message": "Cancellation requested"}


# ---------------- Open folder ----------------

@router.post("/open-folder")
async def open_folder(req: OpenFolderRequest):
    path = os.path.abspath(os.path.expanduser(req.path))
    # Only allow opening folders this app actually created (anti-abuse).
    known = {h.get("folder") for h in storage.get_history(500) if h.get("folder")}
    known |= {j["folder"] for j in
              (manager.get_status(jid) for jid in manager.list_jobs())
              if isinstance(j, dict) and j.get("folder")}
    if path not in known or not os.path.isdir(path):
        raise HTTPException(403, "Unknown folder")
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", path])
        elif sys.platform == "win32":
            os.startfile(path)  # noqa
        else:
            subprocess.Popen(["xdg-open", path])
        return {"message": "Folder opened"}
    except Exception as e:
        raise HTTPException(500, f"Could not open folder: {e}")


# ---------------- History ----------------

@router.get("/history")
async def get_history(limit: int = 50):
    return {"history": storage.get_history(min(max(limit, 1), 500))}


@router.delete("/history")
async def delete_history():
    storage.clear_history()
    return {"message": "History cleared"}


# ---------------- Settings & profiles ----------------

@router.get("/settings")
async def get_settings():
    return storage.get_settings()

@router.patch("/settings")
async def patch_settings(patch: SettingsPatch):
    data = {k: v for k, v in patch.model_dump().items() if v is not None}
    if "duplicate_policy" in data and data["duplicate_policy"] not in ("skip", "overwrite", "rename"):
        raise HTTPException(400, "duplicate_policy must be skip|overwrite|rename")
    if "max_parallel_downloads" in data:
        data["max_parallel_downloads"] = min(max(int(data["max_parallel_downloads"]), 1), 8)
    return storage.update_settings(data)


# ---------------- yt-dlp auto-update ----------------

@router.post("/update-ytdlp")
async def update_ytdlp():
    """TODO item: yt-dlp auto-update button."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
            capture_output=True, text=True, timeout=180)
        if result.returncode != 0:
            raise HTTPException(500, result.stderr[-300:])
        import importlib, yt_dlp
        importlib.reload(yt_dlp)
        return {"message": "yt-dlp updated", "version": yt_dlp.version.__version__,
                "note": "Restart the server to be sure the new version is active."}
    except subprocess.TimeoutExpired:
        raise HTTPException(500, "Update timed out")


# ---------------- Folder picker (kept from v1) ----------------

def _open_native_folder_dialog() -> str:
    if sys.platform == "darwin":
        script = 'POSIX path of (choose folder with prompt "Choose download folder")'
        result = subprocess.run(["osascript", "-e", script],
                                capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else ""
    if sys.platform == "win32":
        ps = ('Add-Type -AssemblyName System.Windows.Forms; '
              '$f = New-Object System.Windows.Forms.FolderBrowserDialog; '
              '$f.Description = "Choose download folder"; '
              '$f.ShowNewFolderButton = $true; '
              'if ($f.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) '
              '{ Write-Output $f.SelectedPath }')
        result = subprocess.run(["powershell", "-NoProfile", "-STA", "-Command", ps],
                                capture_output=True, text=True)
        return result.stdout.strip()
    for cmd in ([["zenity", "--file-selection", "--directory",
                  "--title=Choose download folder"],
                 ["kdialog", "--getexistingdirectory", os.path.expanduser("~")]]):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            if result.returncode == 1:
                return ""
        except FileNotFoundError:
            continue
    raise RuntimeError("No folder picker available. Install 'zenity' or 'kdialog'.")


@router.get("/pick-folder")
def pick_folder():
    try:
        path = _open_native_folder_dialog()
        if path:
            storage.update_settings({"last_folder": os.path.abspath(path)})
        return {"path": os.path.abspath(path) if path else ""}
    except Exception as e:
        raise HTTPException(500, str(e))

```

---

## `server/storage.py`

```python
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

```

---

## `server/options.py`

```python
"""Builds yt_dlp option dictionaries.

Replaces the old subprocess-based command.py. Using the Python API instead of
shelling out gives us: real-time progress hooks, cancellation, structured
errors, and no command-injection surface.
"""
import re

QUALITY_MAP = {
    "4k":    "bestvideo[height<=2160]+bestaudio/best[height<=2160]/best",
    "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
    "720p":  "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
    "480p":  "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
    "low":   "bestvideo[height<=360]+bestaudio/best[height<=360]/best",
}

VIDEO_CONTAINERS = {"mp4", "mkv", "webm"}
AUDIO_FORMATS = {"mp3", "m4a", "opus", "flac"}

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

# TODO item: playlist range syntax "1-10, 15, 20-30"
_RANGE_RE = re.compile(r"^\s*\d+\s*(-\s*\d+\s*)?(,\s*\d+\s*(-\s*\d+\s*)?)*$")

# Whitelist of yt-dlp template fields allowed in custom filename templates.
_ALLOWED_TEMPLATE_FIELDS = {
    "title", "ext", "id", "uploader", "channel", "upload_date",
    "playlist_title", "playlist_index", "autonumber", "resolution", "duration",
}
_TEMPLATE_FIELD_RE = re.compile(r"%\((\w+)\)")


def validate_playlist_range(expr: str) -> bool:
    return bool(_RANGE_RE.match(expr))


def sanitize_filename_template(template: str) -> str:
    """Validate a user-supplied output template. Falls back to a safe default
    on anything suspicious (path separators, unknown fields)."""
    default = "%(title)s.%(ext)s"
    if not template or not isinstance(template, str):
        return default
    if "/" in template or "\\" in template or ".." in template:
        return default
    fields = _TEMPLATE_FIELD_RE.findall(template)
    if not fields or any(f not in _ALLOWED_TEMPLATE_FIELDS for f in fields):
        return default
    if "%(ext)s" not in template:
        template += ".%(ext)s"
    return template


def build_ydl_opts(output_dir: str,
                   is_audio: bool = False,
                   quality: str = "1080p",
                   video_container: str = "mp4",
                   audio_format: str = "mp3",
                   playlist_items: str = None,
                   subtitles_langs: list = None,
                   filename_template: str = None,
                   duplicate_policy: str = "skip",
                   progress_hook=None,
                   postprocessor_hook=None) -> dict:
    template = sanitize_filename_template(filename_template or "%(title)s.%(ext)s")

    # TODO item: duplicate detection (Skip / Overwrite / Rename)
    if duplicate_policy == "rename":
        # include the unique video id so re-downloads never collide
        if "%(id)s" not in template:
            template = template.replace(".%(ext)s", " [%(id)s].%(ext)s")

    opts = {
        "outtmpl": f"{output_dir}/{template}",
        "http_headers": {"User-Agent": USER_AGENT},
        "extractor_args": {"youtube": {"player_client": ["android_vr", "web"],
                                       "player_skip": ["configs"]}},
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "ignoreerrors": "only_download",   # one failed playlist item doesn't kill the job
        "overwrites": duplicate_policy == "overwrite",
        "nooverwrites": duplicate_policy == "skip",
        "retries": 5,
        "fragment_retries": 5,
        "socket_timeout": 30,
    }

    if playlist_items:
        opts["playlist_items"] = playlist_items.replace(" ", "")

    if progress_hook:
        opts["progress_hooks"] = [progress_hook]
    if postprocessor_hook:
        opts["postprocessor_hooks"] = [postprocessor_hook]

    if is_audio:
        if audio_format not in AUDIO_FORMATS:
            audio_format = "mp3"
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": audio_format,
            "preferredquality": "0",
        }]
    else:
        if video_container not in VIDEO_CONTAINERS:
            video_container = "mp4"
        opts["format"] = QUALITY_MAP.get(quality, QUALITY_MAP["1080p"])
        opts["merge_output_format"] = video_container
        opts["postprocessor_args"] = {"ffmpeg": ["-movflags", "+faststart"]} \
            if video_container == "mp4" else {}
        opts["fixup"] = "detect_or_warn"

    # TODO item: subtitles download with language selection
    if subtitles_langs:
        opts["writesubtitles"] = True
        opts["writeautomaticsub"] = True
        opts["subtitleslangs"] = [l.strip() for l in subtitles_langs if l.strip()]

    return opts

```

---

## `server/info.py`

```python
"""Metadata extraction: video preview & playlist info with thumbnails and
durations (TODO items: thumbnails in playlist panel, video duration in
playlist panel, video preview before download)."""
import re

import yt_dlp

_FLAT_OPTS = {
    "extract_flat": "in_playlist",
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
}


def extract_playlist_id(url):
    m = re.search(r"[?&]list=([a-zA-Z0-9_-]+)", url)
    return m.group(1) if m else None


def normalize_to_playlist_url(url):
    pid = extract_playlist_id(url)
    return f"https://www.youtube.com/playlist?list={pid}" if pid else url


def _fmt_duration(seconds):
    if not seconds:
        return ""
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def _best_thumbnail(entry):
    if entry.get("thumbnail"):
        return entry["thumbnail"]
    thumbs = entry.get("thumbnails") or []
    if thumbs:
        return thumbs[-1].get("url", "")
    vid = entry.get("id")
    return f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg" if vid else ""


def get_media_info(url):
    """Single entry point for /info. Returns either a playlist payload
    (with per-video thumbnail + duration) or a single-video preview."""
    is_playlist = bool(extract_playlist_id(url))
    target = normalize_to_playlist_url(url) if is_playlist else url

    with yt_dlp.YoutubeDL(_FLAT_OPTS) as ydl:
        info = ydl.extract_info(target, download=False)

    if info is None:
        raise RuntimeError("No metadata returned for this URL")

    entries = info.get("entries")
    if is_playlist and entries:
        videos = []
        for idx, entry in enumerate(entries, 1):
            if not entry:
                continue
            videos.append({
                "index": idx,
                "id": entry.get("id", ""),
                "title": entry.get("title") or f"Video {idx}",
                "duration": _fmt_duration(entry.get("duration")),
                "thumbnail": _best_thumbnail(entry),
                "channel": entry.get("channel") or entry.get("uploader") or "",
            })
        return {
            "is_playlist": True,
            "title": info.get("title", "Playlist"),
            "channel": info.get("channel") or info.get("uploader") or "",
            "videos": videos,
        }

    # Single video preview
    return {
        "is_playlist": False,
        "id": info.get("id", ""),
        "title": info.get("title", ""),
        "channel": info.get("channel") or info.get("uploader") or "",
        "duration": _fmt_duration(info.get("duration")),
        "thumbnail": _best_thumbnail(info),
        "videos": [],
    }


def get_title_for_folder(url):
    """Title used to name the output subfolder (playlist title or video title)."""
    is_playlist = bool(extract_playlist_id(url))
    target = normalize_to_playlist_url(url) if is_playlist else url
    with yt_dlp.YoutubeDL(_FLAT_OPTS) as ydl:
        info = ydl.extract_info(target, download=False)
    if not info or not info.get("title"):
        raise RuntimeError("Could not resolve a title for this URL")
    return info["title"], info.get("channel") or info.get("uploader") or ""

```

---

## `server/jobs.py`

```python
"""Job manager: parallel downloads, real-time progress, cancellation,
post-download hooks, desktop notifications, history persistence.

Replaces the old fire-and-forget subprocess.run() which gave no progress,
no cancel, no error detail, and ran one download at a time.
"""
import os
import shlex
import subprocess
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor

import yt_dlp

from server import options as opt_engine
from server import storage

try:
    from plyer import notification as _plyer_notification
except Exception:  # plyer is optional
    _plyer_notification = None


def send_alert(title, message):
    if not _plyer_notification:
        return
    try:
        _plyer_notification.notify(title=title, message=message,
                                   app_name="YouTube Downloader", timeout=10)
    except Exception as e:
        print(f"[notify] {e}")


class CancelledError(Exception):
    pass


class JobManager:
    def __init__(self):
        self._jobs = {}
        self._lock = threading.Lock()
        max_workers = max(1, int(storage.get_settings().get("max_parallel_downloads", 3)))
        # TODO item: parallel downloads (multiple jobs at once)
        self._executor = ThreadPoolExecutor(max_workers=max_workers)

    # ---------- public API ----------

    def create_job(self, params: dict) -> str:
        job_id = str(uuid.uuid4())
        with self._lock:
            self._jobs[job_id] = {
                "status": "queued",
                "url": params["url"],
                "progress": {"percent": 0.0, "speed": "", "eta": "",
                             "filename": "", "item": 0, "total_items": 0},
                "error": None,
                "folder": None,
                "cancel": threading.Event(),
            }
        self._executor.submit(self._run, job_id, params)
        return job_id

    def get_status(self, job_id: str):
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return {"status": "not_found"}
            return {
                "status": job["status"],
                "url": job["url"],
                "progress": dict(job["progress"]),
                "error": job["error"],
                "folder": job["folder"],
            }

    def list_jobs(self):
        with self._lock:
            return {jid: {"status": j["status"], "url": j["url"],
                          "progress": dict(j["progress"])}
                    for jid, j in self._jobs.items()}

    def cancel(self, job_id: str) -> bool:
        """TODO item: cancel button for running downloads."""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job["status"] in ("completed", "failed", "cancelled"):
                return False
            job["cancel"].set()
            if job["status"] == "queued":
                job["status"] = "cancelled"
        return True

    # ---------- internals ----------

    def _set(self, job_id, **kwargs):
        with self._lock:
            job = self._jobs.get(job_id)
            if job:
                job.update(kwargs)

    def _progress_hook(self, job_id):
        """TODO item: real-time download progress bar."""
        def hook(d):
            with self._lock:
                job = self._jobs.get(job_id)
                if not job:
                    return
                if job["cancel"].is_set():
                    raise CancelledError()
                info = d.get("info_dict") or {}
                prog = job["progress"]
                prog["item"] = info.get("playlist_index") or prog["item"] or 1
                prog["total_items"] = info.get("n_entries") or prog["total_items"] or 1
                if d.get("status") == "downloading":
                    total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                    done = d.get("downloaded_bytes") or 0
                    prog["percent"] = round(done * 100.0 / total, 1) if total else 0.0
                    prog["speed"] = d.get("_speed_str", "").strip()
                    prog["eta"] = d.get("_eta_str", "").strip()
                    prog["filename"] = os.path.basename(d.get("filename") or "")
                elif d.get("status") == "finished":
                    prog["percent"] = 100.0
                    prog["speed"] = ""
                    prog["eta"] = ""
        return hook

    def _run_post_hook(self, folder: str):
        """TODO item: post-download hooks (custom command after each download)."""
        hook_cmd = storage.get_settings().get("post_hook", "").strip()
        if not hook_cmd:
            return
        try:
            env = dict(os.environ, DOWNLOAD_FOLDER=folder)
            subprocess.run(shlex.split(hook_cmd), env=env, timeout=120,
                           capture_output=True)
        except Exception as e:
            print(f"[post-hook] failed: {e}")

    def _run(self, job_id: str, params: dict):
        with self._lock:
            job = self._jobs.get(job_id)
            if not job or job["cancel"].is_set():
                return
            job["status"] = "processing"

        try:
            ydl_opts = opt_engine.build_ydl_opts(
                output_dir=params["output_dir"],
                is_audio=params.get("is_audio", False),
                quality=params.get("quality", "1080p"),
                video_container=params.get("video_container", "mp4"),
                audio_format=params.get("audio_format", "mp3"),
                playlist_items=params.get("playlist_items"),
                subtitles_langs=params.get("subtitles_langs"),
                filename_template=params.get("filename_template"),
                duplicate_policy=params.get("duplicate_policy", "skip"),
                progress_hook=self._progress_hook(job_id),
            )
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ret = ydl.download([params["download_url"]])
            if ret != 0:
                raise RuntimeError("Some items failed to download")

            self._set(job_id, status="completed", folder=params["output_dir"])
            storage.add_history_entry(
                url=params["url"], title=params.get("title", ""),
                folder=params["output_dir"], status="completed",
                is_audio=params.get("is_audio", False))
            send_alert("Download complete", params.get("title") or params["url"])
            self._run_post_hook(params["output_dir"])

        except CancelledError:
            self._set(job_id, status="cancelled")
            storage.add_history_entry(url=params["url"],
                                      title=params.get("title", ""),
                                      folder=params["output_dir"],
                                      status="cancelled")
        except Exception as e:
            msg = str(e).split("\n")[0][:300]
            self._set(job_id, status="failed", error=msg)
            storage.add_history_entry(url=params["url"],
                                      title=params.get("title", ""),
                                      folder=params["output_dir"],
                                      status="failed")
            send_alert("Download failed", msg)


manager = JobManager()

```

---

## `front/index.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YT Downloader</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
    <link rel="icon" type="image/x-icon" href="favicon.ico">
</head>
<body>
    <div class="background-glow"></div>
    <div class="container">
        <div class="header">
            <div class="logo">
                <svg viewBox="0 0 24 24" fill="currentColor" width="32" height="32">
                    <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
            </div>
            <h1>YouTube Downloader</h1>
            <p class="subtitle">Paste a link, pick your format, and grab it.</p>
            <div class="toolbar">
                <button type="button" class="action-btn" onclick="toggleHistory()">History</button>
                <button type="button" class="action-btn" id="batchBtn" onclick="document.getElementById('batchFile').click()">Batch (.txt)</button>
                <input type="file" id="batchFile" accept=".txt" class="hidden" onchange="loadBatchFile(this)">
                <button type="button" class="action-btn" id="updateBtn" onclick="updateYtdlp()">Update yt-dlp</button>
            </div>
        </div>

        <div class="input-group">
            <input type="text" id="urlInput" placeholder="Paste YouTube link here...">
        </div>

        <!-- Video preview (single video) -->
        <div id="previewContainer" class="preview-card hidden">
            <img id="previewThumb" alt="" class="preview-thumb">
            <div class="preview-meta">
                <div id="previewTitle" class="preview-title"></div>
                <div class="preview-sub"><span id="previewChannel"></span> · <span id="previewDuration"></span></div>
                <div id="profileBadge" class="profile-badge hidden">Channel profile applied</div>
            </div>
        </div>

        <!-- Playlist Selector -->
        <div id="playlistContainer" class="playlist-group hidden">
            <div class="playlist-header">
                <span class="playlist-title" id="playlistTitle">Playlist</span>
                <div class="playlist-actions">
                    <button type="button" class="action-btn" onclick="selectAllVideos(true)">Select All</button>
                    <button type="button" class="action-btn" onclick="selectAllVideos(false)">Deselect All</button>
                </div>
            </div>
            <input type="text" id="rangeInput" class="range-input" placeholder='Range (optional) — e.g. "1-10, 15, 20-30"'>
            <div class="playlist-list" id="playlistList"></div>
            <div class="playlist-count" id="playlistCount"></div>
        </div>

        <div class="input-group">
            <label class="folder-label" for="outputDir">Save to</label>
            <div class="folder-row">
                <input type="text" id="outputDir" placeholder="Last used folder (or ~/Downloads)" readonly>
                <button type="button" id="browseBtn" class="browse-btn" onclick="pickFolder()">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
                        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                    </svg>
                    <span>Browse</span>
                </button>
            </div>
        </div>

        <div class="toggle-group">
            <label class="toggle-switch">
                <input type="checkbox" id="audioOnly">
                <span class="toggle-track"><span class="toggle-thumb"></span></span>
                <span class="toggle-label">
                    <span class="toggle-title">Audio only</span>
                    <span class="toggle-sub">Strip the video, keep the sound</span>
                </span>
            </label>
        </div>

        <div id="qualityContainer" class="quality-group">
            <label class="quality-heading">Quality</label>
            <div class="radio-grid">
                <label class="radio-card"><input type="radio" name="quality" value="4k"><span class="radio-content"><span class="radio-title">4K</span><span class="radio-sub">Ultra HD</span></span></label>
                <label class="radio-card"><input type="radio" name="quality" value="1080p" checked><span class="radio-content"><span class="radio-title">1080p</span><span class="radio-sub">Full HD</span></span></label>
                <label class="radio-card"><input type="radio" name="quality" value="720p"><span class="radio-content"><span class="radio-title">720p</span><span class="radio-sub">HD</span></span></label>
                <label class="radio-card"><input type="radio" name="quality" value="480p"><span class="radio-content"><span class="radio-title">480p</span><span class="radio-sub">SD</span></span></label>
                <label class="radio-card radio-card-wide"><input type="radio" name="quality" value="low"><span class="radio-content"><span class="radio-title">Low</span><span class="radio-sub">Data Saver</span></span></label>
            </div>
        </div>

        <!-- Advanced options -->
        <details class="advanced">
            <summary>Advanced options</summary>
            <div class="advanced-grid">
                <label id="containerOpt">Video format
                    <select id="videoContainer">
                        <option value="mp4" selected>MP4</option>
                        <option value="mkv">MKV</option>
                        <option value="webm">WebM</option>
                    </select>
                </label>
                <label id="audioOpt" class="hidden">Audio format
                    <select id="audioFormat">
                        <option value="mp3" selected>MP3</option>
                        <option value="m4a">M4A</option>
                        <option value="opus">OPUS</option>
                        <option value="flac">FLAC</option>
                    </select>
                </label>
                <label>If file exists
                    <select id="duplicatePolicy">
                        <option value="skip" selected>Skip</option>
                        <option value="overwrite">Overwrite</option>
                        <option value="rename">Rename</option>
                    </select>
                </label>
                <label>Subtitles (e.g. en,fr — empty = none)
                    <input type="text" id="subtitlesLangs" placeholder="en,fr">
                </label>
                <label class="advanced-wide">Filename template
                    <input type="text" id="filenameTemplate" placeholder="%(title)s.%(ext)s">
                </label>
                <label class="advanced-wide checkbox-line">
                    <input type="checkbox" id="saveProfile">
                    Save these settings as the profile for this channel
                </label>
            </div>
        </details>

        <button id="downloadBtn" onclick="startDownload()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            <span>Download</span>
        </button>

        <!-- Active jobs (progress + cancel + open folder) -->
        <div id="jobsContainer"></div>

        <!-- History panel -->
        <div id="historyContainer" class="history-group hidden">
            <div class="playlist-header">
                <span class="playlist-title">Download history</span>
                <button type="button" class="action-btn" onclick="clearHistory()">Clear</button>
            </div>
            <div id="historyList" class="playlist-list"></div>
        </div>

        <div id="status"></div>
    </div>
    <script src="script.js" defer></script>
</body>
</html>

```

---

## `front/script.js`

```javascript
const API = 'http://127.0.0.1:8000';

const audioCheckbox = document.getElementById('audioOnly');
const qualityContainer = document.getElementById('qualityContainer');
const urlInput = document.getElementById('urlInput');
const statusDiv = document.getElementById('status');

let currentInfo = null;       // last /info payload
let lastCheckedUrl = '';
const activeJobs = new Map(); // job_id -> {el, timer}

// ---------- helpers ----------

async function api(path, opts = {}) {
    const res = await fetch(API + path, opts);
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
}

function getQuality() {
    const r = document.querySelector('input[name="quality"]:checked');
    return r ? r.value : '1080p';
}

function setQuality(value) {
    const r = document.querySelector(`input[name="quality"][value="${value}"]`);
    if (r) r.checked = true;
}

audioCheckbox.addEventListener('change', function () {
    qualityContainer.classList.toggle('hidden', this.checked);
    document.getElementById('containerOpt').classList.toggle('hidden', this.checked);
    document.getElementById('audioOpt').classList.toggle('hidden', !this.checked);
});

// ---------- settings bootstrap (remember last folder) ----------

(async function init() {
    try {
        const s = await api('/settings');
        if (s.last_folder) document.getElementById('outputDir').value = s.last_folder;
        if (s.filename_template) document.getElementById('filenameTemplate').placeholder = s.filename_template;
        if (s.duplicate_policy) document.getElementById('duplicatePolicy').value = s.duplicate_policy;
    } catch (_) { /* server not up yet */ }
})();

// ---------- URL info: preview / playlist ----------

urlInput.addEventListener('paste', () => setTimeout(() => maybeCheckUrl(urlInput.value.trim()), 50));
urlInput.addEventListener('blur', () => maybeCheckUrl(urlInput.value.trim()));

function maybeCheckUrl(url) {
    if (!url) { hidePlaylist(); hidePreview(); lastCheckedUrl = ''; return; }
    if (url === lastCheckedUrl) return;
    lastCheckedUrl = url;
    fetchInfo(url);
}

async function fetchInfo(url) {
    hidePreview();
    const container = document.getElementById('playlistContainer');
    container.classList.remove('hidden');
    document.getElementById('playlistTitle').textContent = 'Loading info...';
    document.getElementById('playlistList').innerHTML = '';
    document.getElementById('playlistCount').textContent = '';

    try {
        const data = await api(`/info?url=${encodeURIComponent(url)}`);
        currentInfo = data;
        applyChannelProfile(data.channel_profile);
        if (data.is_playlist && data.videos.length > 0) {
            renderPlaylist(data);
        } else {
            hidePlaylist();
            renderPreview(data);
        }
    } catch (e) {
        showPlaylistError('Could not load info: ' + e.message);
        setTimeout(hidePlaylist, 2500);
    }
}

function applyChannelProfile(profile) {
    const badge = document.getElementById('profileBadge');
    if (!profile) { badge.classList.add('hidden'); return; }
    audioCheckbox.checked = !!profile.is_audio;
    audioCheckbox.dispatchEvent(new Event('change'));
    if (profile.quality) setQuality(profile.quality);
    if (profile.video_container) document.getElementById('videoContainer').value = profile.video_container;
    if (profile.audio_format) document.getElementById('audioFormat').value = profile.audio_format;
    badge.classList.remove('hidden');
}

// ---------- single-video preview ----------

function renderPreview(data) {
    if (!data.title) return;
    document.getElementById('previewThumb').src = data.thumbnail || '';
    document.getElementById('previewTitle').textContent = data.title;
    document.getElementById('previewChannel').textContent = data.channel || 'Unknown channel';
    document.getElementById('previewDuration').textContent = data.duration || '—';
    document.getElementById('previewContainer').classList.remove('hidden');
}

function hidePreview() {
    document.getElementById('previewContainer').classList.add('hidden');
    document.getElementById('profileBadge').classList.add('hidden');
}

// ---------- playlist panel (thumbnails + durations) ----------

function showPlaylistError(msg) {
    document.getElementById('playlistTitle').textContent = msg;
    document.getElementById('playlistList').innerHTML = '';
    document.getElementById('playlistCount').textContent = '';
}

function renderPlaylist(data) {
    document.getElementById('playlistTitle').textContent = data.title || 'Playlist';
    const list = document.getElementById('playlistList');
    list.innerHTML = '';

    data.videos.forEach(video => {
        const item = document.createElement('div');
        item.className = 'playlist-item';
        item.innerHTML = `
            <label class="playlist-label">
                <input type="checkbox" class="playlist-checkbox" checked>
                <span class="playlist-checkmark"></span>
                <img class="playlist-thumb" loading="lazy" alt="">
                <span class="playlist-video-text">
                    <span class="playlist-video-title"></span>
                    <span class="playlist-video-duration"></span>
                </span>
            </label>`;
        item.querySelector('.playlist-checkbox').value = video.index;
        item.querySelector('.playlist-thumb').src = video.thumbnail || '';
        item.querySelector('.playlist-video-title').textContent = video.title;       // textContent => no XSS
        item.querySelector('.playlist-video-duration').textContent = video.duration || '';
        list.appendChild(item);
    });

    list.querySelectorAll('.playlist-checkbox').forEach(cb => cb.addEventListener('change', updatePlaylistCount));
    updatePlaylistCount();
}

function hidePlaylist() {
    document.getElementById('playlistContainer').classList.add('hidden');
    document.getElementById('rangeInput').value = '';
}

function selectAllVideos(checked) {
    document.querySelectorAll('.playlist-checkbox').forEach(cb => cb.checked = checked);
    updatePlaylistCount();
}

function updatePlaylistCount() {
    const checked = document.querySelectorAll('.playlist-checkbox:checked').length;
    const total = document.querySelectorAll('.playlist-checkbox').length;
    document.getElementById('playlistCount').textContent = `${checked} of ${total} videos selected`;
}

function getSelectedIndices() {
    if (!currentInfo || !currentInfo.is_playlist) return null;
    return Array.from(document.querySelectorAll('.playlist-checkbox:checked'))
        .map(cb => parseInt(cb.value, 10));
}

// ---------- folder picker ----------

async function pickFolder() {
    const btn = document.getElementById('browseBtn');
    const input = document.getElementById('outputDir');
    const original = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<span>Picking…</span>';
    try {
        const data = await api('/pick-folder');
        if (data.path) input.value = data.path;
    } catch (e) {
        alert('Could not open folder picker: ' + e.message);
    } finally {
        btn.disabled = false;
        btn.innerHTML = original;
    }
}

// ---------- download ----------

function buildRequestBody(url) {
    const range = document.getElementById('rangeInput').value.trim();
    const selected = getSelectedIndices();
    const subs = document.getElementById('subtitlesLangs').value.trim();
    return {
        url,
        is_audio: audioCheckbox.checked,
        quality: getQuality(),
        output_dir: document.getElementById('outputDir').value.trim() || null,
        playlist_items: range || null,
        selected_indices: range ? null : selected,
        video_container: document.getElementById('videoContainer').value,
        audio_format: document.getElementById('audioFormat').value,
        subtitles_langs: subs ? subs.split(',').map(s => s.trim()).filter(Boolean) : null,
        filename_template: document.getElementById('filenameTemplate').value.trim() || null,
        duplicate_policy: document.getElementById('duplicatePolicy').value,
        save_channel_profile: document.getElementById('saveProfile').checked,
    };
}

async function startDownload() {
    const url = urlInput.value.trim();
    if (!url) { alert('Please enter a URL'); return; }
    const range = document.getElementById('rangeInput').value.trim();
    const selected = getSelectedIndices();
    if (!range && selected !== null && selected.length === 0) {
        alert('Please select at least one video from the playlist.');
        return;
    }
    statusDiv.innerText = '';
    try {
        const data = await api('/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(buildRequestBody(url)),
        });
        trackJob(data.job_id, currentInfo?.title || url);
    } catch (e) {
        statusDiv.innerText = 'Error: ' + e.message;
    }
}

// ---------- batch mode (.txt of URLs) ----------

async function loadBatchFile(input) {
    const file = input.files[0];
    if (!file) return;
    const text = await file.text();
    const urls = text.split(/\r?\n/).map(l => l.trim()).filter(l => l && !l.startsWith('#'));
    input.value = '';
    if (urls.length === 0) { alert('No URLs found in file.'); return; }
    if (!confirm(`Start ${urls.length} downloads with the current settings?`)) return;
    try {
        const body = buildRequestBody('');
        const data = await api('/download-batch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                urls,
                is_audio: body.is_audio,
                quality: body.quality,
                output_dir: body.output_dir,
                video_container: body.video_container,
                audio_format: body.audio_format,
                duplicate_policy: body.duplicate_policy,
            }),
        });
        data.jobs.forEach(j => trackJob(j.job_id, j.url));
        if (data.errors.length) {
            statusDiv.innerText = data.errors.map(e => `${e.url}: ${e.error}`).join('\n');
        }
    } catch (e) {
        statusDiv.innerText = 'Batch error: ' + e.message;
    }
}

// ---------- job cards: progress bar + cancel + open folder ----------

function trackJob(jobId, label) {
    const container = document.getElementById('jobsContainer');
    const card = document.createElement('div');
    card.className = 'job-card';
    card.innerHTML = `
        <div class="job-head">
            <span class="job-title"></span>
            <span class="job-state">queued</span>
        </div>
        <div class="progress-track"><div class="progress-fill" style="width:0%"></div></div>
        <div class="job-meta"></div>
        <div class="job-actions">
            <button type="button" class="action-btn job-cancel">Cancel</button>
            <button type="button" class="action-btn job-open hidden">Open folder</button>
        </div>`;
    card.querySelector('.job-title').textContent = label;
    container.prepend(card);

    const cancelBtn = card.querySelector('.job-cancel');
    cancelBtn.onclick = async () => {
        cancelBtn.disabled = true;
        try { await api(`/cancel/${jobId}`, { method: 'POST' }); } catch (_) {}
    };

    const timer = setInterval(() => pollJob(jobId), 1500);
    activeJobs.set(jobId, { el: card, timer });
    pollJob(jobId);
}

async function pollJob(jobId) {
    const job = activeJobs.get(jobId);
    if (!job) return;
    let data;
    try { data = await api(`/status/${jobId}`); }
    catch (_) { return; }

    const { el } = job;
    const p = data.progress || {};
    el.querySelector('.job-state').textContent = data.status;
    el.querySelector('.progress-fill').style.width = `${p.percent || 0}%`;

    const parts = [];
    if (p.total_items > 1) parts.push(`item ${p.item}/${p.total_items}`);
    if (p.percent) parts.push(`${p.percent}%`);
    if (p.speed) parts.push(p.speed);
    if (p.eta) parts.push(`ETA ${p.eta}`);
    if (p.filename) parts.push(p.filename);
    el.querySelector('.job-meta').textContent = parts.join(' · ');

    if (['completed', 'failed', 'cancelled'].includes(data.status)) {
        clearInterval(job.timer);
        activeJobs.delete(jobId);
        el.querySelector('.job-cancel').classList.add('hidden');
        el.classList.add(`job-${data.status}`);
        if (data.status === 'failed' && data.error) {
            el.querySelector('.job-meta').textContent = data.error;
        }
        if (data.status === 'completed' && data.folder) {
            el.querySelector('.progress-fill').style.width = '100%';
            const openBtn = el.querySelector('.job-open');
            openBtn.classList.remove('hidden');
            openBtn.onclick = () => openFolder(data.folder);
        }
        refreshHistory();
    }
}

async function openFolder(path) {
    try {
        await api('/open-folder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path }),
        });
    } catch (e) { alert('Could not open folder: ' + e.message); }
}

// ---------- history ----------

async function toggleHistory() {
    const panel = document.getElementById('historyContainer');
    panel.classList.toggle('hidden');
    if (!panel.classList.contains('hidden')) refreshHistory();
}

async function refreshHistory() {
    const panel = document.getElementById('historyContainer');
    if (panel.classList.contains('hidden')) return;
    const list = document.getElementById('historyList');
    try {
        const data = await api('/history?limit=50');
        list.innerHTML = '';
        if (data.history.length === 0) {
            list.textContent = 'No downloads yet.';
            return;
        }
        data.history.forEach(h => {
            const row = document.createElement('div');
            row.className = 'history-item';
            row.innerHTML = `
                <span class="history-title"></span>
                <span class="history-status"></span>
                <button type="button" class="action-btn history-open hidden">Open</button>`;
            row.querySelector('.history-title').textContent = h.title || h.url || '';
            row.querySelector('.history-status').textContent = h.status || '';
            if (h.folder) {
                const btn = row.querySelector('.history-open');
                btn.classList.remove('hidden');
                btn.onclick = () => openFolder(h.folder);
            }
            list.appendChild(row);
        });
    } catch (e) {
        list.textContent = 'Could not load history: ' + e.message;
    }
}

async function clearHistory() {
    if (!confirm('Clear the whole download history?')) return;
    try { await api('/history', { method: 'DELETE' }); refreshHistory(); }
    catch (e) { alert(e.message); }
}

// ---------- yt-dlp update ----------

async function updateYtdlp() {
    const btn = document.getElementById('updateBtn');
    btn.disabled = true;
    btn.textContent = 'Updating…';
    try {
        const data = await api('/update-ytdlp', { method: 'POST' });
        btn.textContent = `yt-dlp ${data.version}`;
    } catch (e) {
        btn.textContent = 'Update failed';
        alert('Update failed: ' + e.message);
    } finally {
        setTimeout(() => { btn.disabled = false; btn.textContent = 'Update yt-dlp'; }, 4000);
    }
}

```

---

## `front/style.css`

```css
:root {
    --bg-start: #0f0c29;
    --bg-mid: #1a1148;
    --bg-end: #24243e;
    --card-bg: rgba(255, 255, 255, 0.06);
    --card-border: rgba(255, 255, 255, 0.1);
    --text: #f5f5fa;
    --text-muted: rgba(245, 245, 250, 0.55);
    --accent: #ff0033;
    --accent-glow: rgba(255, 0, 51, 0.45);
    --accent-2: #ff4d6d;
    --success: #4ade80;
    --error: #f87171;
}

* { box-sizing: border-box; }

html, body {
    margin: 0;
    padding: 0;
    min-height: 100vh;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: linear-gradient(135deg, var(--bg-start) 0%, var(--bg-mid) 50%, var(--bg-end) 100%);
    color: var(--text);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    overflow-x: hidden;
    position: relative;
}

.background-glow {
    position: fixed;
    top: -20%;
    left: 50%;
    transform: translateX(-50%);
    width: 800px;
    height: 800px;
    background: radial-gradient(circle, var(--accent-glow) 0%, transparent 60%);
    filter: blur(80px);
    opacity: 0.35;
    pointer-events: none;
    z-index: 0;
    animation: pulse 8s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 0.3; transform: translateX(-50%) scale(1); }
    50% { opacity: 0.5; transform: translateX(-50%) scale(1.1); }
}

.container {
    position: relative;
    z-index: 1;
    background: var(--card-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--card-border);
    padding: 2.5rem;
    border-radius: 20px;
    box-shadow:
        0 20px 60px rgba(0, 0, 0, 0.4),
        inset 0 1px 0 rgba(255, 255, 255, 0.08);
    width: 100%;
    max-width: 460px;
    animation: slideUp 0.6s cubic-bezier(0.2, 0.9, 0.3, 1);
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.header { text-align: center; margin-bottom: 1.75rem; }

.logo {
    width: 56px;
    height: 56px;
    margin: 0 auto 0.85rem;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    box-shadow: 0 8px 24px var(--accent-glow);
}

h1 {
    font-size: 1.6rem;
    font-weight: 700;
    margin: 0 0 0.4rem;
    letter-spacing: -0.02em;
    background: linear-gradient(180deg, #ffffff 0%, #c7c7d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.subtitle {
    margin: 0;
    color: var(--text-muted);
    font-size: 0.9rem;
}

.input-group { margin-bottom: 1.25rem; }

input[type="text"] {
    width: 100%;
    padding: 14px 16px;
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    color: var(--text);
    font-size: 0.95rem;
    font-family: inherit;
    transition: all 0.25s ease;
    outline: none;
}

input[type="text"]::placeholder { color: var(--text-muted); }

input[type="text"]:focus {
    border-color: var(--accent);
    background: rgba(0, 0, 0, 0.35);
    box-shadow: 0 0 0 4px rgba(255, 0, 51, 0.12);
}

/* Toggle switch */
.toggle-group { margin-bottom: 1.25rem; }

.toggle-switch {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 16px;
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.25s ease;
    user-select: none;
}

.toggle-switch:hover { border-color: rgba(255, 255, 255, 0.2); }

.toggle-switch input { position: absolute; opacity: 0; pointer-events: none; }

.toggle-track {
    position: relative;
    width: 44px;
    height: 24px;
    background: rgba(255, 255, 255, 0.12);
    border-radius: 999px;
    transition: background 0.25s ease;
    flex-shrink: 0;
}

.toggle-thumb {
    position: absolute;
    top: 2px;
    left: 2px;
    width: 20px;
    height: 20px;
    background: white;
    border-radius: 50%;
    transition: transform 0.25s cubic-bezier(0.2, 0.9, 0.3, 1);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.toggle-switch input:checked ~ .toggle-track {
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
}

.toggle-switch input:checked ~ .toggle-track .toggle-thumb {
    transform: translateX(20px);
}

.toggle-label { display: flex; flex-direction: column; gap: 2px; }
.toggle-title { font-size: 0.92rem; font-weight: 500; }
.toggle-sub { font-size: 0.78rem; color: var(--text-muted); }

/* Quality radio cards */
.quality-group {
    margin-bottom: 1.5rem;
    overflow: hidden;
    transition: opacity 0.3s ease, max-height 0.3s ease, margin 0.3s ease;
    max-height: 300px;
    opacity: 1;
}

.quality-group.hidden {
    opacity: 0;
    max-height: 0;
    margin-bottom: 0;
    pointer-events: none;
}

.quality-heading {
    display: block;
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 0.7rem;
}

.radio-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
}

.radio-card {
    position: relative;
    cursor: pointer;
    padding: 12px 14px;
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid var(--card-border);
    border-radius: 10px;
    transition: all 0.2s ease;
    overflow: hidden;
}

.radio-card-wide { grid-column: span 2; }

.radio-card input { position: absolute; opacity: 0; pointer-events: none; }

.radio-card:hover {
    border-color: rgba(255, 255, 255, 0.22);
    background: rgba(0, 0, 0, 0.35);
}

.radio-card:has(input:checked) {
    border-color: var(--accent);
    background: rgba(255, 0, 51, 0.12);
    box-shadow: 0 0 0 1px var(--accent), 0 4px 16px rgba(255, 0, 51, 0.18);
}

.radio-content {
    display: flex;
    flex-direction: column;
    gap: 2px;
}

.radio-title { font-size: 0.95rem; font-weight: 600; }
.radio-sub { font-size: 0.72rem; color: var(--text-muted); }

.radio-card:has(input:checked) .radio-sub { color: rgba(255, 255, 255, 0.75); }

.hidden-select {
    position: absolute;
    width: 1px;
    height: 1px;
    opacity: 0;
    pointer-events: none;
}

/* Button */
button {
    width: 100%;
    padding: 14px;
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    color: white;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    font-family: inherit;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    box-shadow: 0 6px 20px var(--accent-glow);
    position: relative;
    overflow: hidden;
}

button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s ease;
}

button:hover::before { left: 100%; }

button:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 28px var(--accent-glow);
}

button:active { transform: translateY(0); }

/* Status */
#status {
    margin-top: 1.25rem;
    padding: 0;
    text-align: center;
    font-weight: 500;
    font-size: 0.9rem;
    color: var(--text-muted);
    min-height: 1.2em;
    transition: all 0.3s ease;
}

#status:not(:empty) {
    padding: 12px;
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid var(--card-border);
    border-radius: 10px;
    color: var(--text);
}

@media (max-width: 480px) {
    .container { padding: 1.75rem 1.4rem; }
    h1 { font-size: 1.35rem; }
}

/* Folder picker row */
.folder-label {
    display: block;
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}

.folder-row {
    display: flex;
    gap: 8px;
    align-items: stretch;
}

.folder-row input[type="text"] {
    flex: 1;
    min-width: 0;
}

.browse-btn {
    width: auto;
    padding: 0 16px;
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid var(--card-border);
    color: var(--text);
    box-shadow: none;
    font-size: 0.9rem;
    font-weight: 500;
    flex-shrink: 0;
}

.browse-btn:hover {
    border-color: rgba(255, 255, 255, 0.22);
    background: rgba(0, 0, 0, 0.35);
    box-shadow: none;
    transform: none;
}

.browse-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

/* ============================
   PLAYLIST SELECTOR STYLES
   ============================ */

.playlist-group {
    margin-bottom: 1.25rem;
    background: rgba(0, 0, 0, 0.25);
    border: 1px solid var(--card-border);
    border-radius: 12px;
    overflow: hidden;
    transition: opacity 0.3s ease, max-height 0.35s ease, margin 0.3s ease;
    max-height: 600px;
    opacity: 1;
}

.playlist-group.hidden {
    opacity: 0;
    max-height: 0;
    margin-bottom: 0;
    pointer-events: none;
    border: none;
}

.playlist-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 14px;
    border-bottom: 1px solid var(--card-border);
    background: rgba(0, 0, 0, 0.15);
}

.playlist-title {
    font-size: 0.92rem;
    font-weight: 600;
    color: var(--text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding-right: 10px;
}

.playlist-actions {
    display: flex;
    gap: 6px;
    flex-shrink: 0;
}

.action-btn {
    width: auto;
    padding: 5px 10px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid var(--card-border);
    color: var(--text-muted);
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: none;
}

.action-btn:hover {
    background: rgba(255, 255, 255, 0.14);
    color: var(--text);
    border-color: rgba(255, 255, 255, 0.25);
    transform: none;
    box-shadow: none;
}

.playlist-list {
    max-height: 260px;
    overflow-y: auto;
    padding: 6px;
}

/* Custom scrollbar */
.playlist-list::-webkit-scrollbar {
    width: 6px;
}
.playlist-list::-webkit-scrollbar-track {
    background: transparent;
}
.playlist-list::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 10px;
}
.playlist-list::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.25);
}

.playlist-item {
    padding: 4px;
}

.playlist-label {
    position: relative;          /* ← ajoute cette ligne */
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.15s ease;
}

.playlist-label:hover {
    background: rgba(255, 255, 255, 0.05);
}

.playlist-checkbox {
    position: absolute;
    width: 1px;
    height: 1px;
    opacity: 0;
    pointer-events: none;
    top: 0;
    left: 0;
}

.playlist-checkmark {
    width: 18px;
    height: 18px;
    border: 2px solid rgba(255, 255, 255, 0.25);
    border-radius: 5px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
}

.playlist-checkbox:checked + .playlist-checkmark {
    background: linear-gradient(135deg, var(--accent), var(--accent-2));
    border-color: transparent;
}

.playlist-checkbox:checked + .playlist-checkmark::after {
    content: '';
    width: 5px;
    height: 9px;
    border: solid white;
    border-width: 0 2px 2px 0;
    transform: rotate(45deg) translate(-1px, -1px);
}

.playlist-video-title {
    font-size: 0.85rem;
    color: var(--text);
    line-height: 1.3;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.playlist-count {
    padding: 8px 14px;
    font-size: 0.78rem;
    color: var(--text-muted);
    text-align: right;
    border-top: 1px solid var(--card-border);
    background: rgba(0, 0, 0, 0.15);
}
/* ===================== v2 additions ===================== */

.hidden { display: none !important; }

.toolbar { display: flex; gap: 8px; justify-content: center; margin-top: 14px; flex-wrap: wrap; }

/* Video preview */
.preview-card {
    display: flex; gap: 14px; align-items: center;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px; padding: 12px; margin-bottom: 18px;
}
.preview-thumb { width: 120px; aspect-ratio: 16/9; object-fit: cover; border-radius: 8px; background: #111; }
.preview-title { font-weight: 600; font-size: 0.95rem; margin-bottom: 4px; }
.preview-sub { font-size: 0.8rem; opacity: 0.65; }
.profile-badge {
    display: inline-block; margin-top: 6px; padding: 2px 8px;
    font-size: 0.7rem; border-radius: 999px;
    background: rgba(80,200,120,0.15); color: #6fdc99;
    border: 1px solid rgba(80,200,120,0.35);
}

/* Playlist thumbnails + durations */
.playlist-thumb { width: 72px; aspect-ratio: 16/9; object-fit: cover; border-radius: 6px; margin: 0 10px; background: #111; flex-shrink: 0; }
.playlist-video-text { display: flex; flex-direction: column; min-width: 0; }
.playlist-video-duration { font-size: 0.72rem; opacity: 0.55; margin-top: 2px; }
.range-input {
    width: 100%; box-sizing: border-box; margin-bottom: 10px;
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px; padding: 10px 12px; color: inherit; font: inherit; font-size: 0.85rem;
}

/* Advanced options */
.advanced { margin-bottom: 18px; }
.advanced summary { cursor: pointer; font-size: 0.85rem; opacity: 0.75; padding: 6px 0; user-select: none; }
.advanced-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding-top: 10px; }
.advanced-grid label { display: flex; flex-direction: column; gap: 5px; font-size: 0.78rem; opacity: 0.85; }
.advanced-grid .advanced-wide { grid-column: 1 / -1; }
.advanced-grid select, .advanced-grid input[type="text"] {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px; padding: 9px 10px; color: inherit; font: inherit; font-size: 0.85rem;
}
.checkbox-line { flex-direction: row !important; align-items: center; gap: 8px !important; }

/* Job cards: progress, cancel, open folder */
#jobsContainer { margin-top: 18px; display: flex; flex-direction: column; gap: 10px; }
.job-card {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px; padding: 12px 14px;
}
.job-head { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 8px; }
.job-title { font-size: 0.85rem; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.job-state { font-size: 0.75rem; opacity: 0.7; text-transform: capitalize; flex-shrink: 0; }
.progress-track { height: 6px; border-radius: 999px; background: rgba(255,255,255,0.08); overflow: hidden; }
.progress-fill { height: 100%; width: 0; border-radius: 999px; background: linear-gradient(90deg, #ff4d4d, #ff7a4d); transition: width 0.4s ease; }
.job-completed .progress-fill { background: linear-gradient(90deg, #36c275, #6fdc99); }
.job-failed .progress-fill, .job-cancelled .progress-fill { background: rgba(255,255,255,0.18); }
.job-meta { font-size: 0.74rem; opacity: 0.6; margin-top: 7px; min-height: 1em; word-break: break-all; }
.job-actions { display: flex; gap: 8px; margin-top: 9px; }

/* History */
.history-group {
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px; padding: 14px; margin-top: 18px;
}
.history-item {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 4px; border-bottom: 1px solid rgba(255,255,255,0.06);
    font-size: 0.82rem;
}
.history-item:last-child { border-bottom: none; }
.history-title { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.history-status { font-size: 0.72rem; opacity: 0.55; text-transform: capitalize; }

```
