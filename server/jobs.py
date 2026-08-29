"""Job manager: parallel downloads, real-time progress, cancellation,
post-download hooks, desktop notifications, history persistence.

Replaces the old fire-and-forget subprocess.run() which gave no progress,
no cancel, no error detail, and ran one download at a time.
"""
import os
import re
import shlex
import shutil
import subprocess
import sys
import threading
import uuid
import warnings
from concurrent.futures import ThreadPoolExecutor

import yt_dlp

from server import options as opt_engine
from server import storage

try:
    from plyer import notification as _plyer_notification
except Exception:  # plyer is optional
    _plyer_notification = None


def send_alert(title, message):
    """Desktop notification, best-effort.

    On Linux we call notify-send directly. Going through plyer there means
    hitting its optional python-dbus dependency, which makes it print a
    UserWarning on every single notification -- noise in the server log for a
    feature that is not even essential. plyer is still used on macOS/Windows.
    """
    if sys.platform.startswith("linux") and shutil.which("notify-send"):
        try:
            subprocess.Popen(["notify-send", "-a", "YouTube Downloader",
                              str(title), str(message)],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except OSError:
            pass

    if _plyer_notification:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                _plyer_notification.notify(title=title, message=message,
                                           app_name="YouTube Downloader",
                                           timeout=10)
        except Exception:
            pass


class CancelledError(Exception):
    pass


class _CollectingLogger:
    """Captures yt-dlp's own diagnostics.

    With ignoreerrors="only_download", yt-dlp swallows per-item errors and just
    returns a non-zero code, so the job used to fail with the useless message
    "Some items failed to download". We keep the real lines and report the
    first one instead.
    """

    def __init__(self):
        self.errors = []
        self.warnings = []

    def debug(self, msg):
        pass

    def info(self, msg):
        pass

    def warning(self, msg):
        self.warnings.append(str(msg))
        print(f"[yt-dlp warning] {msg}")

    def error(self, msg):
        self.errors.append(str(msg))
        print(f"[yt-dlp error] {msg}")

    # yt-dlp routes some purely informational notices through logger.error
    # (deprecation notices, update nags); they must not shadow the real cause.
    _NOISE = ("deprecated feature", "you are using an outdated version",
              "please update", "unable to obtain version")

    def first_error(self):
        for line in self.errors:
            cleaned = re.sub(r"\x1b\[[0-9;]*m", "", str(line))
            cleaned = cleaned.replace("ERROR:", "").strip()
            if not cleaned or any(n in cleaned.lower() for n in self._NOISE):
                continue
            return cleaned
        return ""


# YouTube rejects media URLs (HTTP 403) when the signing client, the cookie
# session and the requesting client disagree. Rather than guess once, walk a
# short ladder: yt-dlp's own choice, then two cookie-capable clients, then the
# same without cookies in case the jar is stale.
_ATTEMPT_LADDER = (
    {"label": "default clients, cookies",  "player_client": "",           "use_cookies": True},
    {"label": "tv client, cookies",        "player_client": "tv",         "use_cookies": True},
    {"label": "web_safari client, cookies", "player_client": "web_safari", "use_cookies": True},
    {"label": "default clients, no cookies", "player_client": "",         "use_cookies": False},
)

_RETRYABLE = ("403", "forbidden", "requested format is not available",
              "unable to download video data", "fragment", "precondition check failed",
              "sign in to confirm", "the page needs to be reloaded")


def _is_retryable(msg: str) -> bool:
    m = (msg or "").lower()
    return any(t in m for t in _RETRYABLE)


def _explain(msg: str) -> str:
    """Append the actionable cause when yt-dlp's message alone is a dead end."""
    m = (msg or "").lower()
    if "403" in m or "forbidden" in m:
        from server import diagnostics
        if not diagnostics.has_usable_js_runtime():
            return (f"{msg} — no JavaScript runtime found, so yt-dlp cannot solve "
                    f"YouTube's 'n' signature challenge. Install Deno "
                    f"(curl -fsSL https://deno.land/install.sh | sh) or Node 22+, "
                    f"then restart the server.")
        return (f"{msg} — tried every player client, with and without cookies. "
                f"Your cookies.txt is likely expired: re-export it from a browser "
                f"where you are signed in to YouTube.")
    return msg


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
            settings = storage.get_settings()

            def make_opts(attempt):
                o = opt_engine.build_ydl_opts(
                    output_dir=params["output_dir"],
                    is_audio=params.get("is_audio", False),
                    quality=params.get("quality", "1080p"),
                    video_container=params.get("video_container", "mp4"),
                    audio_format=params.get("audio_format", "mp3"),
                    playlist_items=params.get("playlist_items"),
                    subtitles_langs=params.get("subtitles_langs"),
                    filename_template=params.get("filename_template"),
                    duplicate_policy=params.get("duplicate_policy", "skip"),
                    cookies_browser=settings.get("cookies_browser", ""),
                    cookies_file=settings.get("cookies_file", ""),
                    progress_hook=self._progress_hook(job_id),
                    player_client=attempt["player_client"],
                    use_cookies=attempt["use_cookies"],
                )
                return o

            last_error = ""
            for i, attempt in enumerate(_ATTEMPT_LADDER):
                with self._lock:
                    job = self._jobs.get(job_id)
                    if not job or job["cancel"].is_set():
                        raise CancelledError()

                logger = _CollectingLogger()
                ydl_opts = make_opts(attempt)
                ydl_opts["logger"] = logger

                if i:
                    print(f"[job {job_id[:8]}] retry {i}: {attempt['label']}")

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ret = ydl.download([params["download_url"]])

                if ret == 0:
                    break

                last_error = logger.first_error() or "Some items failed to download"
                # Only a blocked-media error is worth retrying with another
                # client/cookie combination. A private video or a dead URL will
                # fail identically every time.
                if not _is_retryable(last_error):
                    break

            if ret != 0:
                raise RuntimeError(_explain(last_error))

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
