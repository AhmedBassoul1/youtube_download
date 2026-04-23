def get_command_video(folder_name, video_url):
    return [
        "yt-dlp",
        "--extractor-args", "youtube:player_client=android_vr,web;player_skip=configs",
        "-f", "bestvideo[height<=1080]+bestaudio/best",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "--merge-output-format", "mp4",
        "--postprocessor-args", "ffmpeg:-movflags +faststart",
        "-o", f"{folder_name}/%(title)s.%(ext)s", # Dossier de sortie
        video_url
    ]

def get_command_audio(video_url):
    return [
        "yt-dlp",
        "--extractor-args", "youtube:player_client=android_vr,web;player_skip=configs",
        "-f", "bestaudio/best",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "-o", f"{folder_name}/%(title)s.%(ext)s", # Dossier de sortie
        video_url
    ]