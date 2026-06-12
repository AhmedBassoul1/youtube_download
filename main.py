from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router as download_router

app = FastAPI(title="YouTube Downloader API", version="2.0.0")

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
