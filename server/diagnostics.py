"""Environment checks for the things that silently break YouTube downloads.

The two failures that look like application bugs but are not:

* No supported JavaScript runtime. YouTube protects media URLs with an "n"
  signature challenge that yt-dlp can only solve by executing JavaScript. With
  no runtime, extraction succeeds and format selection succeeds, then the media
  request comes back "HTTP Error 403: Forbidden". Nothing in the traceback
  points at the real cause.
* Missing ffmpeg. Video+audio are downloaded as separate streams and must be
  muxed; without ffmpeg the merge step fails after a full download.

Both are reported at startup and through GET /diagnostics.
"""
import os
import shutil

from server import options as opt_engine

# Minimum versions yt-dlp accepts, mirrored here for the human-readable hint.
_RUNTIME_HINTS = {
    "deno": "deno >= 2.3.0 — install: curl -fsSL https://deno.land/install.sh | sh",
    "node": "node >= 22.0.0 — install: https://nodejs.org (or nvm install 22)",
    "bun": "bun >= 1.2.11 — install: curl -fsSL https://bun.sh/install | bash",
    "quickjs": "quickjs (qjs) >= 2023-12-09",
}


def js_runtimes() -> dict:
    """Which JS runtimes yt-dlp can actually use on this machine."""
    try:
        from yt_dlp.globals import supported_js_runtimes
    except Exception:
        return {}

    found = {}
    for name, cls in supported_js_runtimes.value.items():
        try:
            info = cls().info
        except Exception:
            info = None
        if info is None:
            found[name] = None
        else:
            found[name] = {"version": info.version, "supported": info.supported,
                           "path": info.path}
    return found


def has_usable_js_runtime() -> bool:
    return any(v and v.get("supported") for v in js_runtimes().values())


def cookie_status() -> dict:
    auto = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "cookies.txt")
    return {"path": auto if os.path.exists(auto) else "",
            "present": os.path.exists(auto),
            "valid_format": opt_engine.is_valid_cookie_file(auto)}


def report() -> dict:
    runtimes = js_runtimes()
    usable = [n for n, v in runtimes.items() if v and v.get("supported")]
    problems = []
    if not usable:
        problems.append(
            "No supported JavaScript runtime found. YouTube media URLs will "
            "return HTTP 403 because the 'n' signature challenge cannot be "
            "solved. Install one of: "
            + " | ".join(_RUNTIME_HINTS.values()))
    if not shutil.which("ffmpeg"):
        problems.append(
            "ffmpeg not found on PATH. Video and audio streams cannot be "
            "merged, and audio extraction (mp3/m4a/opus/flac) will fail.")
    return {
        "js_runtimes": runtimes,
        "usable_js_runtimes": usable,
        "ffmpeg": shutil.which("ffmpeg") or "",
        "cookies": cookie_status(),
        "problems": problems,
        "ok": not problems,
    }


def log_startup_report():
    r = report()
    print("--- youtube-downloader environment ---")
    print(f"  JS runtime : {', '.join(r['usable_js_runtimes']) or 'NONE'}")
    print(f"  ffmpeg     : {r['ffmpeg'] or 'NOT FOUND'}")
    c = r["cookies"]
    print(f"  cookies.txt: {'valid' if c['valid_format'] else ('present but not Netscape format' if c['present'] else 'none')}")
    for p in r["problems"]:
        print(f"  !! {p}")
    print("--------------------------------------")
    return r
