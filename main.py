from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as download_router
from server import diagnostics


@asynccontextmanager
async def lifespan(app):
    # Surface a missing JS runtime / ffmpeg up front, instead of letting them
    # reappear later as an opaque "HTTP Error 403: Forbidden".
    diagnostics.log_startup_report()
    yield


app = FastAPI(title="YouTube Downloader API", version="2.0.0", lifespan=lifespan)

# Restricted CORS: only the local frontend (was "*" + credentials, an invalid
# and insecure combination).
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080", "http://127.0.0.1:8080",
        "http://localhost:5500", "http://127.0.0.1:5500",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(download_router)


@app.get("/")
def read_root():
    return {"message": "Server is running. Access docs at /docs"}
