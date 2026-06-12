# Building releases

## Windows .exe (PyInstaller)

```powershell
pip install pyinstaller
pyinstaller --onefile --name yt-downloader ^
  --add-data "front;front" ^
  --hidden-import uvicorn.logging ^
  --hidden-import uvicorn.loops.auto ^
  --hidden-import uvicorn.protocols.http.auto ^
  main_desktop.py
```

`main_desktop.py` (included in the repo) starts the API and opens the UI in the
default browser. FFmpeg must be installed on the target machine, or bundled
with `--add-binary "C:\path\to\ffmpeg.exe;."`.

macOS / Linux equivalents: same command with `:` instead of `;` in `--add-data`.

## APK

This project is a Python/FastAPI desktop app: packaging it as a native Android
APK is not practical (yt-dlp + FFmpeg + a local web server inside Android would
require a rewrite with Kivy/Chaquopy or Termux packaging). Recommended
alternatives:

1. Use the web UI from a phone browser pointing at the desktop server on the
   local network (`uvicorn main:app --host 0.0.0.0`).
2. Wrap the frontend in a thin WebView app (Capacitor / TWA) that talks to a
   self-hosted server.
