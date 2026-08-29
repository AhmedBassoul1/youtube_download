"""Metadata extraction: video preview & playlist info with thumbnails and
durations (TODO items: thumbnails in playlist panel, video duration in
playlist panel, video preview before download)."""
import os
import re

import yt_dlp

from server import options as opt_engine

_FLAT_OPTS = {
    "extract_flat": "in_playlist",
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
}

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _flat_opts():
    """Same cookie jar as the downloader, so a video that previews fine is
    also one the downloader can actually reach."""
    opts = dict(_FLAT_OPTS)
    auto = os.path.join(_BASE_DIR, "cookies.txt")
    if opt_engine.is_valid_cookie_file(auto):
        opts["cookiefile"] = auto
    return opts


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

    with yt_dlp.YoutubeDL(_flat_opts()) as ydl:
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
    with yt_dlp.YoutubeDL(_flat_opts()) as ydl:
        info = ydl.extract_info(target, download=False)
    if not info or not info.get("title"):
        raise RuntimeError("Could not resolve a title for this URL")
    return info["title"], info.get("channel") or info.get("uploader") or ""
