from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from uuid import uuid4
from server import downloader as dl_engine
from server import command as cmd_engine
import os

router = APIRouter()

# Keep your jobs store here
jobs = {}
print("API router initialized JOB  = ")
print(jobs)

class DownloadRequest(BaseModel):
    url: str
    is_audio: bool = False
    quality: str = "1080p"

def run_download_task(job_id: str, url: str, is_audio: bool, quality: str):
    """Background task to handle the download."""
    jobs[job_id] = {"status": "processing", "url": url}
    try:
        # Generate output directory (logic from your notebook)
        output_dir = dl_engine.get_playlist_name(url)
        output_dir = dl_engine.re.sub(r'[<>:"/\\|?*]', '', output_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Get command
        if is_audio:
            full_cmd = cmd_engine.get_command_audio(output_dir, url, quality=quality)
        else:
            full_cmd = cmd_engine.get_command_video(output_dir, url, quality=quality)

        # Run process
        dl_engine.downloader(full_cmd)
        
        jobs[job_id]["status"] = "completed"
    except Exception as e:
        jobs[job_id] = {"status": "failed", "error": str(e)}

@router.post("/download")
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid4())
    jobs[job_id] = {"status": "queued", "url": request.url}
    background_tasks.add_task(
        run_download_task, 
        job_id, 
        request.url, 
        request.is_audio, 
        request.quality  
    )    
    return {"job_id": job_id, "message": "Download started"}

@router.get("/status/{job_id}")
async def get_status(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})