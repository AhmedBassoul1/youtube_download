def get_command_video(folder_name, video_url, quality="1080p", playlist_items=None):
    quality_map = {
        "4k": "bestvideo[height<=2160]+bestaudio/best",
        "1080p": "bestvideo[height<=1080]+bestaudio/best",
        "720p": "bestvideo[height<=720]+bestaudio/best",
        "480p": "bestvideo[height<=480]+bestaudio/best",
        "low": "bestvideo[height<=360]+bestaudio/best"
    }
    
    format_str = quality_map.get(quality, "bestvideo[height<=1080]+bestaudio/best")

    cmd = [
        "yt-dlp",
        "--extractor-args", "youtube:player_client=android_vr,web;player_skip=configs",
        "-f", format_str,
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "--merge-output-format", "mp4",
        "--postprocessor-args", "ffmpeg:-movflags +faststart",
        "-o", f"{folder_name}/%(title)s.%(ext)s",
    ]
    
    if playlist_items:
        cmd.extend(["--playlist-items", ",".join(map(str, playlist_items))])
    
    cmd.append(video_url)
    return cmd

def get_command_audio(folder_name, video_url, quality="1080p", playlist_items=None):
    cmd = [
        "yt-dlp",
        "--extractor-args", "youtube:player_client=android_vr,web;player_skip=configs",
        "-f", "bestaudio/best",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "-o", f"{folder_name}/%(title)s.%(ext)s",
    ]
    
    if playlist_items:
        cmd.extend(["--playlist-items", ",".join(map(str, playlist_items))])
    
    cmd.append(video_url)
    return cmd