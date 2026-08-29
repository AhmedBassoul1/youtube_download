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

https://www.youtube.com/watch?v=eew6N-87FDs