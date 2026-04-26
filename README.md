# 🎬 YouTube Downloader

<div align="center">

A sleek, modern YouTube video & audio downloader with a glassmorphic web UI and a FastAPI backend powered by `yt-dlp`.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![yt-dlp](https://img.shields.io/badge/yt--dlp-FF0000?logo=youtube&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## ✨ Features

- 🎥 **Video downloads** in multiple qualities — 4K, 1080p, 720p, 480p, or Data Saver mode.
- 🎵 **Audio-only mode** — extract MP3 at the highest available bitrate.
- ✅ **Selective Playlist Downloading** — Fetch playlist metadata, see all videos, and choose exactly which ones you want to download.
- 📂 **Smart Folders** — Automatically creates a folder named after the playlist/video.
- 🌗 **Modern UI** — Glassmorphic design, animated background glow, responsive layout.
- ⚡ **Async processing** — Background tasks via FastAPI so the UI stays snappy.
- 🔔 **Desktop notifications** — System alerts via `plyer` when the job is ready.

---

## 📁 Project Structure

```
youtube_downloader/
│
├── api/                # FastAPI routes
│   └── routes.py       # /download, /info, and /status endpoints
│
├── server/             # Core download logic
│   ├── command.py      # Builds yt-dlp command strings
│   └── downloader.py   # Subprocess runner & playlist parser
│
├── front/              # Web frontend
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── main.py             # FastAPI app entry point
└── requirements.txt
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/AhmedBassoul1/youtube_download.git
cd youtube_downloader
```

### 2. Setup (Virtual Environment & Dependencies)

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
python -m venv venv
source venv/bin/activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

> ⚠️ Ensure **FFmpeg** is installed on your system — required for video merging.

---

## 🎯 Usage

Start the backend:

```bash
uvicorn main:app --reload
```

Open the frontend by opening `front/index.html` in your browser.

### How to download

**Single Video:**
Paste the link, select audio/video settings, and hit **Download**.

**Playlist:**
1. Paste the playlist URL.
2. Click the **Fetch** button.
3. A list of videos will appear. Use the checkboxes to select the specific videos you want (or use "Select All").
4. Select your quality/format settings.
5. Hit **Download**. The server will process only your selected items.

---

## 🔌 API Reference

### `POST /info`

Fetches metadata for a video or playlist. Used to populate the selection UI.

**Request:**

```json
{
  "url": "..."
}
```

**Response:**

```json
{
  "is_playlist": true,
  "title": "...",
  "videos": [
    { "index": 1, "title": "..." }
  ]
}
```

---

### `POST /download`

Starts a download job.

**Request body:**

```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "is_audio": false,
  "quality": "1080p",
  "output_dir": "/path/to/save",
  "playlist_items": "1,3,5"
}
```

> Note: `playlist_items` is optional. If left null, the entire playlist is downloaded.

**Response:**

```json
{
  "job_id": "uuid-string",
  "message": "Download started"
}
```

---

### `GET /status/{job_id}`

Returns the current status: `queued`, `processing`, `completed`, or `failed`.

---

## ⚠️ Disclaimer

This tool is intended for **personal use only**. Downloading copyrighted material without permission may violate YouTube's Terms of Service and applicable copyright laws. Use responsibly.

---

<div align="center">

Made with ❤️ and a lot of ☕

</div>
