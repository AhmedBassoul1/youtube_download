# 🎬 YouTube Downloader

A simple and flexible Python tool to download YouTube videos and playlists in high quality — either as **MP4 video (up to 1080p)** or as **MP3 audio**. Built on top of [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) and controlled through a clean Jupyter Notebook interface.

---

## ✨ Features

- 📹 **Video download** up to **1080p** (best video + best audio, merged as MP4)
- 🎵 **Audio-only download** in **MP3** at the highest available quality
- 📂 **Automatic folder creation** based on the playlist/video title
- 📝 **Playlist track listing** — generates a `A_ordre.txt` file preserving the original order of videos in a playlist
- 🔔 **Desktop notifications** when downloads complete (via `plyer`)
- 🛠️ Optimized `yt-dlp` arguments to bypass common YouTube restrictions (SABR streaming, etc.)
- 🎯 Works for **single videos** *and* **entire playlists**

---

## 📦 Project Structure

```
youtube_downloader/
│
├── command.py          # Builds the yt-dlp CLI commands (video / audio)
├── downloader.py       # Core functions: download, playlist parsing, notifications
├── downloader.ipynb    # Notebook interface — this is what you run
└── README.md           # You are here
```

### File overview

| File | Role |
|------|------|
| `command.py` | Contains `get_command_video()` and `get_command_audio()` which return the full `yt-dlp` command as a list of arguments. |
| `downloader.py` | Wrappers around `yt-dlp`: `downloader()` to run a command, `get_playlist_name()` to fetch the playlist title, `recuperer_noms_playlist()` to list all video titles, and `send_alert()` for desktop notifications. |
| `downloader.ipynb` | Entry point — paste your link, pick video or audio, run the cells. |

---

## 🔧 Requirements

- **Python 3.10+**
- **[ffmpeg](https://ffmpeg.org/)** installed and available in your system `PATH` (required to merge video + audio and to convert to MP3)
- Python packages:
  - `yt-dlp`
  - `plyer`
  - `jupyter` / `notebook` (or VS Code with the Jupyter extension)

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/youtube_downloader.git
cd youtube_downloader
```

### 2. Create a virtual environment (recommended)

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install yt-dlp plyer notebook
```

Or, if you create a `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Install ffmpeg

- **Windows** — download from [ffmpeg.org](https://ffmpeg.org/download.html) and add the `bin/` folder to your `PATH`, or install via [Chocolatey](https://chocolatey.org/): `choco install ffmpeg`
- **macOS** — `brew install ffmpeg`
- **Linux (Debian/Ubuntu)** — `sudo apt install ffmpeg`

Verify the installation:
```bash
ffmpeg -version
yt-dlp --version
```

---

## 📖 How to Use

### Quick start (Notebook)

1. Open `downloader.ipynb` in **Jupyter**, **JupyterLab**, or **VS Code**.
2. Run the first cell to import the module:
   ```python
   import downloader as d
   import importlib
   importlib.reload(d)
   ```
3. Paste your YouTube link:
   ```python
   link_to_download = "https://www.youtube.com/watch?v=VIDEO_ID"
   # or a playlist:
   # link_to_download = "https://www.youtube.com/playlist?list=PLAYLIST_ID"
   ```
4. Create the output folder (named after the video/playlist title):
   ```python
   output_dir = d.get_playlist_name(link_to_download)
   output_dir = d.re.sub(r'[<>:"/\\|?*]', '', output_dir)
   if not d.os.path.exists(output_dir):
       d.os.makedirs(output_dir)
   ```
5. Pick your format and build the command:
   ```python
   # For VIDEO (MP4, up to 1080p)
   full_cmd = d.command.get_command_video(output_dir, link_to_download)

   # For AUDIO (MP3)
   # full_cmd = d.command.get_command_audio(output_dir, link_to_download)
   ```
6. Launch the download:
   ```python
   d.downloader(full_cmd)
   ```

### (Optional) Save the playlist track order

If you downloaded a playlist, you can export the original order of titles into a text file:

```python
titres = d.recuperer_noms_playlist(link_to_download)

path = f"{output_dir}/A_ordre.txt"
with open(path, "w", encoding="utf-8") as f:
    for nom in titres:
        f.write(nom + "\n")
```

This is useful because `yt-dlp` doesn't always download files in the original playlist order.

---

## ⚙️ Configuration

You can tweak the download parameters directly in `command.py`:

- **Max resolution** — change `bestvideo[height<=1080]` to `720`, `1440`, `2160`, etc.
- **Output filename pattern** — change `%(title)s.%(ext)s` (see [yt-dlp output template docs](https://github.com/yt-dlp/yt-dlp#output-template))
- **Audio format** — replace `mp3` with `m4a`, `opus`, `flac`, etc.
- **Audio quality** — `--audio-quality 0` is best; higher numbers = lower quality

---

## 🐛 Troubleshooting

**`WARNING: [youtube] ... Some formats have been skipped ... SABR streaming`**
YouTube is restricting certain client formats. The tool already works around this by using the `android_vr` player client. If problems persist, update `yt-dlp`:
```bash
pip install -U yt-dlp
```

**`No supported JavaScript runtime could be found`**
Some extractions need a JS runtime. Install [Deno](https://deno.land/) and make sure it's in your `PATH`.

**`ffmpeg not found`**
Make sure `ffmpeg` is installed and available in your system `PATH` (see installation step 4).

**Desktop notifications don't appear**
`plyer` behavior depends on your OS. On Linux you may need `libnotify-bin`; on Windows 10/11 it should work out of the box.

---

## 📝 Notes

- Downloaded files go into a folder **named after the video or playlist title** (with invalid filesystem characters stripped out).
- For very large playlists, downloads run sequentially — be patient.
- This tool is intended for **personal use only**. Respect copyright and YouTube's Terms of Service.

---

## 📜 License

This project is provided as-is for educational and personal use. Please don't use it to download content you don't have the right to.

---

## 🙏 Credits

- [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) — the engine that does the heavy lifting
- [`ffmpeg`](https://ffmpeg.org/) — audio/video processing
- [`plyer`](https://github.com/kivy/plyer) — cross-platform notifications
