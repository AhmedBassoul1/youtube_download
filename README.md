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
