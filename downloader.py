import subprocess
import os
import sys
from plyer import notification
import command 
import re
import yt_dlp


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

def recuperer_noms_playlist(url_playlist):
    options = {
        'extract_flat': True,
        'quiet': True,
        'force_generic_extactor': False,
    }

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            infos = ydl.extract_info(url_playlist, download=False)
            
            if 'entries' in infos:
                noms_videos = [entree.get('title') for entree in infos['entries'] if entree]
                return noms_videos
            else:
                return []

    except Exception as e:
        print(f"Erreur lors de l'extraction : {e}")
        return []

def get_playlist_name(url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False)
            
            playlist_title = info_dict.get('title', None)
            return playlist_title
            
        except Exception as e:
            return f"Erreur : {e}"
