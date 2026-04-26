import subprocess
import os
from plyer import notification
import yt_dlp
import re


def send_alert(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="YouTube Downloader",
            timeout=10
        )
    except Exception as e:
        print(f"Erreur notification : {e}")


def downloader(full_command):
    subprocess.run(full_command)


def _extract_playlist_id(url):
    """Return the playlist ID from a URL if there is one, else None."""
    m = re.search(r'[?&]list=([a-zA-Z0-9_-]+)', url)
    return m.group(1) if m else None


def _normalize_to_playlist_url(url):
    """If the URL has a `list=` parameter, return the canonical playlist URL.
    Otherwise return the URL unchanged. This forces yt-dlp to treat
    `watch?v=X&list=Y` as a playlist instead of a single video."""
    pid = _extract_playlist_id(url)
    if pid:
        return f"https://www.youtube.com/playlist?list={pid}"
    return url


def recuperer_noms_playlist(url_playlist):
    options = {
        'extract_flat': True,
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            infos = ydl.extract_info(url_playlist, download=False)
            if 'entries' in infos:
                return [e.get('title') for e in infos['entries'] if e]
            return []
    except Exception as e:
        print(f"Erreur lors de l'extraction : {e}")
        return []


def get_playlist_videos(url):
    """Return playlist metadata + 1-based-indexed videos, or None if the URL
    is a single video (no playlist component)."""
    # If there's no list= parameter, this is a single video — bail out early.
    if not _extract_playlist_id(url):
        print(f"[playlist-info] no list= parameter in URL, treating as single video")
        return None

    playlist_url = _normalize_to_playlist_url(url)
    print(f"[playlist-info] fetching: {playlist_url}")

    options = {
        'extract_flat': True,
        'quiet': True,
        'skip_download': True,
    }
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            infos = ydl.extract_info(playlist_url, download=False)
    except Exception as e:
        print(f"[playlist-info] yt-dlp error: {e}")
        return None

    entries = infos.get('entries')
    if not entries:
        print(f"[playlist-info] no entries returned (keys: {list(infos.keys())})")
        return None

    videos = []
    for idx, entry in enumerate(entries, 1):
        if not entry:
            continue
        videos.append({
            "index": idx,
            "id": entry.get('id', ''),
            "title": entry.get('title') or f"Video {idx}",
        })

    print(f"[playlist-info] OK: {len(videos)} videos in '{infos.get('title')}'")
    return {
        "playlist_title": infos.get('title', 'Playlist'),
        "videos": videos,
    }


def get_playlist_name(url):
    """Used by the download task to name the output subfolder.
    Works for both single videos and playlists."""
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
    }
    target = _normalize_to_playlist_url(url) if _extract_playlist_id(url) else url
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(target, download=False)
            return info_dict.get('title', None)
        except Exception as e:
            return f"Erreur : {e}"