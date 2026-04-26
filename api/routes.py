from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from server import downloader as dl_engine
from server import command as cmd_engine
from typing import Optional
import os
import re
import sys
import subprocess

router = APIRouter()

# Keep your jobs store here
jobs = {}
print("API router initialized JOB  = ")
print(jobs)

class DownloadRequest(BaseModel):
    url: str
    is_audio: bool = False
    quality: str = "1080p"
    output_dir: Optional[str] = None  # NEW: parent folder chosen by the user

def validate_youtube_url(url):
    pattern = r'^(https?://)?(www\.|m\.)?(youtube\.com|youtu\.be)/(watch\?v=|playlist\?list=|embed/|v/)?([a-zA-Z0-9_-]{11}|[a-zA-Z0-9_-]{34})'
    return bool(re.match(pattern, url))


def _open_native_folder_dialog() -> str:
    """Open the OS-native folder picker and return the chosen absolute path,
    or '' if the user cancelled. Raises RuntimeError if no picker is available."""
    if sys.platform == "darwin":
        # macOS: AppleScript via osascript
        script = (
            'POSIX path of (choose folder with prompt "Choose download folder")'
        )
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            # User cancel returns non-zero with "User canceled." on stderr
            return ""
        return result.stdout.strip()

    if sys.platform == "win32":
        # Windows: PowerShell + Windows Forms FolderBrowserDialog.
        # STA threading model is required for Windows Forms dialogs.
        ps_script = (
            'Add-Type -AssemblyName System.Windows.Forms; '
            '$f = New-Object System.Windows.Forms.FolderBrowserDialog; '
            '$f.Description = "Choose download folder"; '
            '$f.ShowNewFolderButton = $true; '
            'if ($f.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) '
            '{ Write-Output $f.SelectedPath }'
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-STA", "-Command", ps_script],
            capture_output=True, text=True
        )
        return result.stdout.strip()

    # Linux: try zenity (GNOME), then kdialog (KDE)
    candidates = [
        ["zenity", "--file-selection", "--directory",
         "--title=Choose download folder"],
        ["kdialog", "--getexistingdirectory", os.path.expanduser("~")],
    ]
    for cmd in candidates:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            if result.returncode == 1:  # user cancelled
                return ""
        except FileNotFoundError:
            continue
    raise RuntimeError(
        "No folder picker available. Install 'zenity' (GNOME) or 'kdialog' (KDE)."
    )


@router.get("/pick-folder")
def pick_folder():
    """Open a native folder picker on the server machine (which is the user's
    machine in this local-only setup) and return the chosen absolute path."""
    try:
        path = _open_native_folder_dialog()
        return {"path": os.path.abspath(path) if path else ""}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _sanitize_folder_name(name: str) -> str:
    """Strip filesystem-illegal characters from a folder name."""
    cleaned = re.sub(r'[<>:"/\\|?*]', '', name).strip()
    return cleaned or "download"


def run_download_task(job_id: str, url: str, is_audio: bool, quality: str,
                      output_dir: Optional[str]):
    jobs[job_id] = {"status": "processing", "url": url}

    if not validate_youtube_url(url):
        jobs[job_id] = {"status": "failed", "error": "Invalid YouTube URL"}
        return

    try:
        # Resolve the parent folder: user-picked or current working dir (legacy behavior)
        if output_dir:
            base_dir = os.path.abspath(os.path.expanduser(output_dir))
            if not os.path.isdir(base_dir):
                raise Exception(f"Folder does not exist: {base_dir}")
            if not os.access(base_dir, os.W_OK):
                raise Exception(f"Folder is not writable: {base_dir}")
        else:
            base_dir = os.getcwd()

        # Get the playlist/video title and turn it into a safe subfolder name
        raw_title = dl_engine.get_playlist_name(url)
        if not raw_title or str(raw_title).startswith("Erreur"):
            raise Exception(f"Could not get title from URL: {raw_title}")
        sub_folder = _sanitize_folder_name(str(raw_title))

        full_output_dir = os.path.join(base_dir, sub_folder)
        os.makedirs(full_output_dir, exist_ok=True)

        if is_audio:
            full_cmd = cmd_engine.get_command_audio(full_output_dir, url, quality=quality)
        else:
            full_cmd = cmd_engine.get_command_video(full_output_dir, url, quality=quality)

        result = dl_engine.downloader(full_cmd)

        if result is False:
            raise Exception("Download failed")

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["folder"] = full_output_dir

    except Exception as e:
        jobs[job_id] = {"status": "failed", "error": str(e)}


@router.post("/download")
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid4())
    jobs[job_id] = {"status": "queued", "url": request.url}
    background_tasks.add_task(
        run_download_task,
        job_id,
        request.url,
        request.is_audio,
        request.quality,
        request.output_dir,
    )
    return {"job_id": job_id, "message": "Download started"}


@router.get("/status/{job_id}")
async def get_status(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})