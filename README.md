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

- 🎥 **Video downloads** in multiple qualities — 4K, 1080p, 720p, 480p, or Data Saver mode
- 🎵 **Audio-only mode** — extract MP3 at the highest available bitrate
- 📂 **Playlist support** — automatically creates a folder named after the playlist
- 🌗 **Modern UI** — glassmorphic design, animated background glow, responsive layout
- ⚡ **Async processing** — background tasks via FastAPI so the UI stays snappy
- 📊 **Live status polling** — track download progress (queued → processing → completed/failed)
- 🔔 **Desktop notifications** — system alerts via `plyer` when ready

---

## 📁 Project Structure

```
youtube_downloader/
│
├── api/                    # FastAPI routes
│   ├── __init__.py
│   └── routes.py           # /download and /status endpoints
│
├── server/                 # Core download logic
│   ├── __init__.py
│   ├── command.py          # Builds yt-dlp command strings
│   └── downloader.py       # Subprocess runner & playlist parser
│
├── front/                  # Web frontend (vanilla HTML/CSS/JS)
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── favicon.ico
│
├── main.py                 # FastAPI app entry point
├── downloader.ipynb        # Jupyter notebook (prototyping)
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/AhmedBassoul1/youtube_download.git
cd youtube_downloader
```

### 2. Create and activate a virtual environment

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

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
pip install fastapi uvicorn pydantic
```

> 💡 **Note:** The base `requirements.txt` includes `yt-dlp`, `plyer`, and `notebook`. You'll also need `fastapi`, `uvicorn`, and `pydantic` to run the API.

### 4. Install FFmpeg (required for video merging)

`yt-dlp` needs FFmpeg to merge separate video and audio streams.

- **Windows:** [Download from ffmpeg.org](https://ffmpeg.org/download.html) and add to `PATH`
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt install ffmpeg`

---

## 🎯 Usage

### Start the backend server

From the project root:

```bash
uvicorn main:app --reload
```

The API will be running at **http://127.0.0.1:8000**.
Interactive docs are available at **http://127.0.0.1:8000/docs**.

### Open the frontend

Simply open `front/index.html` in your browser, or serve it with a lightweight server:

```bash
cd front
python -m http.server 5500
```

Then visit **http://127.0.0.1:5500**.

### Download a video

1. Paste a YouTube URL (single video or playlist)
2. Toggle **Audio only** if you just want the MP3
3. Pick a quality preset
4. Hit **Download** — the file lands in a folder named after the video/playlist title

---

## 🔌 API Reference

### `POST /download`

Starts a new download job.

**Request body:**
```json
{
  "url": "https://www.youtube.com/watch?v=...",
  "is_audio": false,
  "quality": "1080p"
}
```

**Quality options:** `4k`, `1080p`, `720p`, `480p`, `low`

**Response:**
```json
{
  "job_id": "uuid-string",
  "message": "Download started"
}
```

### `GET /status/{job_id}`

Returns the current status of a download job.

**Response:**
```json
{
  "status": "processing",
  "url": "https://www.youtube.com/watch?v=..."
}
```

**Possible statuses:** `queued`, `processing`, `completed`, `failed`, `not_found`

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, Uvicorn, Pydantic |
| Downloader | yt-dlp, FFmpeg |
| Frontend | Vanilla HTML / CSS / JavaScript |
| Notifications | plyer |
| Fonts | Inter (Google Fonts) |

---

## ⚙️ Configuration

### Quality mapping (in `server/command.py`)

| Preset | Max height |
|--------|-----------|
| `4k`     | 2160p |
| `1080p`  | 1080p |
| `720p`   | 720p  |
| `480p`   | 480p  |
| `low`    | 360p  |

### Output

Downloads are saved to a folder named after the playlist (or video) title in the directory where the server is running. Special characters (`<>:"/\\|?*`) are stripped from the folder name.

---

## 🐛 Troubleshooting

- **`ffmpeg not found`** — Install FFmpeg and ensure it's in your system `PATH`.
- **`Could not connect to server`** in the UI — Make sure `uvicorn main:app --reload` is running on port 8000.
- **CORS errors** — `main.py` already enables `allow_origins=["*"]`; if you've modified it, double-check.
- **Downloads stuck on `processing`** — Check the terminal running uvicorn for `yt-dlp` errors (may need a yt-dlp update: `pip install -U yt-dlp`).
- **Permission denied writing files** — Run the server from a directory where you have write access.

---

## 📜 License

This project is licensed under the MIT License — feel free to fork and modify.

---

## ⚠️ Disclaimer

This tool is intended for personal use only. Downloading copyrighted material without permission may violate YouTube's Terms of Service and applicable copyright laws. Use responsibly and only download content you have the right to access.

---

<div align="center">

Made with ❤️ and a lot of ☕

</div>
