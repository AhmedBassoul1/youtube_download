"""Builds yt_dlp option dictionaries.

Replaces the old subprocess-based command.py. Using the Python API instead of
shelling out gives us: real-time progress hooks, cancellation, structured
errors, and no command-injection surface.
"""
import os
import re


def _quality_chain(max_height: int) -> str:
    """Format chain with real fallbacks.

    The old chain was `bestvideo[h<=N]+bestaudio/bestvideo+bestaudio/best`:
    if no separate video+audio pair survived client filtering, yt-dlp had
    nothing left that satisfied the height cap and raised "Requested format
    is not available". We now also try progressive (muxed) formats, then a
    height-capped `best`, then plain `best` as a last resort.
    """
    return (
        f"bestvideo[height<={max_height}]+bestaudio/"
        f"best[height<={max_height}]/"
        f"bestvideo+bestaudio/"
        f"best"
    )


QUALITY_MAP = {
    "4k":    _quality_chain(2160),
    "1080p": _quality_chain(1080),
    "720p":  _quality_chain(720),
    "480p":  _quality_chain(480),
    "low":   _quality_chain(360),
}

VIDEO_CONTAINERS = {"mp4", "mkv", "webm"}
AUDIO_FORMATS = {"mp3", "m4a", "opus", "flac"}

# Project root — used to auto-discover a cookies.txt sitting next to the app.
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# TODO item: playlist range syntax "1-10, 15, 20-30"
_RANGE_RE = re.compile(r"^\s*\d+\s*(-\s*\d+\s*)?(,\s*\d+\s*(-\s*\d+\s*)?)*$")

# Whitelist of yt-dlp template fields allowed in custom filename templates.
_ALLOWED_TEMPLATE_FIELDS = {
    "title", "ext", "id", "uploader", "channel", "upload_date",
    "playlist_title", "playlist_index", "autonumber", "resolution", "duration",
}
_TEMPLATE_FIELD_RE = re.compile(r"%\((\w+)\)")


def is_valid_cookie_file(path: str) -> bool:
    """A malformed cookie jar makes yt-dlp abort before it lists any format,
    so we check the Netscape header rather than handing it a broken file."""
    if not path or not os.path.isfile(path) or not os.access(path, os.R_OK):
        return False
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return "netscape http cookie file" in f.readline().strip().lower()
    except OSError:
        return False


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
                   cookies_browser: str = "",
                   cookies_file: str = "",
                   progress_hook=None,
                   postprocessor_hook=None,
                   player_client: str = "",
                   use_cookies: bool = True) -> dict:
    template = sanitize_filename_template(filename_template or "%(title)s.%(ext)s")

    # TODO item: duplicate detection (Skip / Overwrite / Rename)
    if duplicate_policy == "rename":
        # include the unique video id so re-downloads never collide
        if "%(id)s" not in template:
            template = template.replace(".%(ext)s", " [%(id)s].%(ext)s")

    opts = {
        "outtmpl": f"{output_dir}/{template}",
        # NOTE: no hardcoded http_headers User-Agent and no forced
        # player_client anymore. Pinning player_client to ["web"] meant every
        # extraction went through the one client that YouTube now gates behind
        # a PO token; yt-dlp discarded the gated formats and then reported
        # "Requested format is not available". Letting yt-dlp choose its own
        # client rotation (and send the matching UA per client) fixes it.
        "quiet": True,
        "no_warnings": False,   # warnings explain *why* formats disappear
        "noprogress": True,
        "ignoreerrors": "only_download",   # one failed playlist item doesn't kill the job
        "overwrites": duplicate_policy == "overwrite",
        "nooverwrites": duplicate_policy == "skip",
        "retries": 5,
        "fragment_retries": 5,
        "socket_timeout": 30,
    }

    # Cookies: explicit file > cookies.txt found next to the app > browser.
    # Auto-discovery matters because age/bot-gated videos otherwise expose
    # zero downloadable formats, which surfaces as "format is not available".
    explicit = (cookies_file or "").strip()
    auto_cookies = os.path.join(_BASE_DIR, "cookies.txt")
    if not use_cookies:
        pass  # retry ladder disables cookies: stale jars cause HTTP 403
    elif explicit and is_valid_cookie_file(explicit):
        opts["cookiefile"] = explicit
    elif is_valid_cookie_file(auto_cookies):
        opts["cookiefile"] = auto_cookies
    elif cookies_browser and cookies_browser.strip():
        # "firefox" works on Linux without secretstorage; "chrome" needs it
        opts["cookiesfrombrowser"] = (cookies_browser.strip(),)

    # Only pinned when the retry ladder asks for a specific client.
    if player_client:
        opts["extractor_args"] = {"youtube": {"player_client": [player_client]}}

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
