"""Builds yt_dlp option dictionaries.

Replaces the old subprocess-based command.py. Using the Python API instead of
shelling out gives us: real-time progress hooks, cancellation, structured
errors, and no command-injection surface.
"""
import re

QUALITY_MAP = {
    "4k":    "bestvideo[height<=2160]+bestaudio/best[height<=2160]/best",
    "1080p": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
    "720p":  "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
    "480p":  "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
    "low":   "bestvideo[height<=360]+bestaudio/best[height<=360]/best",
}

VIDEO_CONTAINERS = {"mp4", "mkv", "webm"}
AUDIO_FORMATS = {"mp3", "m4a", "opus", "flac"}

USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

# TODO item: playlist range syntax "1-10, 15, 20-30"
_RANGE_RE = re.compile(r"^\s*\d+\s*(-\s*\d+\s*)?(,\s*\d+\s*(-\s*\d+\s*)?)*$")

# Whitelist of yt-dlp template fields allowed in custom filename templates.
_ALLOWED_TEMPLATE_FIELDS = {
    "title", "ext", "id", "uploader", "channel", "upload_date",
    "playlist_title", "playlist_index", "autonumber", "resolution", "duration",
}
_TEMPLATE_FIELD_RE = re.compile(r"%\((\w+)\)")


def validate_playlist_range(expr: str) -> bool:
    return bool(_RANGE_RE.match(expr))


def sanitize_filename_template(template: str) -> str:
    """Validate a user-supplied output template. Falls back to a safe default
    on anything suspicious (path separators, unknown fields)."""
    default = "%(title)s.%(ext)s"
    if not template or not isinstance(template, str):
        return default
    if "/" in template or "\\" in template or ".." in template:
        return default
    fields = _TEMPLATE_FIELD_RE.findall(template)
    if not fields or any(f not in _ALLOWED_TEMPLATE_FIELDS for f in fields):
        return default
    if "%(ext)s" not in template:
        template += ".%(ext)s"
    return template


def build_ydl_opts(output_dir: str,
                   is_audio: bool = False,
                   quality: str = "1080p",
                   video_container: str = "mp4",
                   audio_format: str = "mp3",
                   playlist_items: str = None,
                   subtitles_langs: list = None,
                   filename_template: str = None,
                   duplicate_policy: str = "skip",
                   progress_hook=None,
                   postprocessor_hook=None) -> dict:
    template = sanitize_filename_template(filename_template or "%(title)s.%(ext)s")

    # TODO item: duplicate detection (Skip / Overwrite / Rename)
    if duplicate_policy == "rename":
        # include the unique video id so re-downloads never collide
        if "%(id)s" not in template:
            template = template.replace(".%(ext)s", " [%(id)s].%(ext)s")

    opts = {
        "outtmpl": f"{output_dir}/{template}",
        "http_headers": {"User-Agent": USER_AGENT},
        "extractor_args": {"youtube": {"player_client": ["android_vr", "web"],
                                       "player_skip": ["configs"]}},
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "ignoreerrors": "only_download",   # one failed playlist item doesn't kill the job
        "overwrites": duplicate_policy == "overwrite",
        "nooverwrites": duplicate_policy == "skip",
        "retries": 5,
        "fragment_retries": 5,
        "socket_timeout": 30,
    }

    if playlist_items:
        opts["playlist_items"] = playlist_items.replace(" ", "")

    if progress_hook:
        opts["progress_hooks"] = [progress_hook]
    if postprocessor_hook:
        opts["postprocessor_hooks"] = [postprocessor_hook]

    if is_audio:
        if audio_format not in AUDIO_FORMATS:
            audio_format = "mp3"
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": audio_format,
            "preferredquality": "0",
        }]
    else:
        if video_container not in VIDEO_CONTAINERS:
            video_container = "mp4"
        opts["format"] = QUALITY_MAP.get(quality, QUALITY_MAP["1080p"])
        opts["merge_output_format"] = video_container
        opts["postprocessor_args"] = {"ffmpeg": ["-movflags", "+faststart"]} \
            if video_container == "mp4" else {}
        opts["fixup"] = "detect_or_warn"

    # TODO item: subtitles download with language selection
    if subtitles_langs:
        opts["writesubtitles"] = True
        opts["writeautomaticsub"] = True
        opts["subtitleslangs"] = [l.strip() for l in subtitles_langs if l.strip()]

    return opts
