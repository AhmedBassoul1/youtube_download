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
