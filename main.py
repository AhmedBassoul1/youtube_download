from fastapi import FastAPI
from api.routes import router as download_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="YouTube Downloader API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router from your api folder
app.include_router(download_router)

@app.get("/")
def read_root():
    return {"message": "Server is running. Access docs at /docs"}