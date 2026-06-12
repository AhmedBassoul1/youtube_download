"""Desktop launcher used for the PyInstaller .exe build (see BUILDING.md).

Starts the FastAPI backend, serves the frontend, and opens the browser.
"""
import os
import sys
import threading
import webbrowser

import uvicorn
from fastapi.staticfiles import StaticFiles

from main import app


def _front_dir():
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "front")


app.mount("/app", StaticFiles(directory=_front_dir(), html=True), name="front")


def _open_ui():
    webbrowser.open("http://127.0.0.1:8000/app/")


if __name__ == "__main__":
    threading.Timer(1.5, _open_ui).start()
    uvicorn.run(app, host="127.0.0.1", port=8000)
