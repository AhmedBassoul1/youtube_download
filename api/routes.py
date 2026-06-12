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
