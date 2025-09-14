# main.py
from fastapi import FastAPI, HTTPException, Depends, File, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from pipeline import process_video, VideoProcessor
from firebase_setup import get_user_tier
from dependencies import get_current_user
from database import get_ready_to_publish_highlights, get_db_connection, create_table, save_highlight
from firebase_setup import get_user_tier
import uuid
import datetime
import aiofiles
import os
import json
from redis.asyncio import Redis
from redis_config import get_redis_pool, lifespan
from models import User
import asyncio

# Initialize the database table
create_table()

app = FastAPI(title="Video Highlight Automation API", lifespan=lifespan)

# Request models
class ProcessVideoRequest(BaseModel):
    video_url: str

class PublishRequest(BaseModel):
    highlight_id: str
    platform: str  # e.g., 'youtube', 'tiktok'

class HighlightResult(BaseModel):
    highlight_id: str
    start_time: float
    end_time: float
    video_path: str
    title: str
    description: str

async def get_redis_client() -> Redis:
    redis_pool = await get_redis_pool()
    return redis_pool

@app.post("/api/v1/process-video")
async def process_video_endpoint(
    request: ProcessVideoRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    redis_client: Redis = Depends(get_redis_client)
):
    """
    Triggers the video processing pipeline for a given video URL.
    """
    user_tier = get_user_tier(user.id)
    if not user_tier:
        raise HTTPException(status_code=403, detail="User's tier could not be determined.")

    # Generate a unique video ID for the entire pipeline
    video_id = str(uuid.uuid4())

    # Create the job payload
    job_payload = {
        "video_id": video_id,
        "video_url": request.video_url,
        "user_id": user.id,
        "timestamp": datetime.datetime.now().isoformat()
    }
    
    # Push the job onto the Redis queue
    await redis_client.rpush("video_processing_queue", json.dumps(job_payload))
    
    # Start processing in background
    background_tasks.add_task(process_video_task, job_payload)

    return {
        "message": "Video processing started.",
        "video_id": video_id,
        "user_id": user.id,
    }

async def process_video_task(job_payload: dict):
    """Background task to process video"""
    try:
        processor = VideoProcessor()
        highlights = await processor.process_video(
            job_payload["video_url"],
            job_payload["video_id"],
            job_payload["user_id"]
        )
        
        # Save highlights to database
        for highlight in highlights:
            save_highlight(
                highlight_id=str(uuid.uuid4()),
                user_id=job_payload["user_id"],
                video_id=job_payload["video_id"],
                start_time=highlight["start_time"],
                end_time=highlight["end_time"],
                video_path=highlight["video_path"],
                title=highlight.get("title", ""),
                description=highlight.get("description", ""),
                status="READY"
            )
            
    except Exception as e:
        print(f"Error processing video: {e}")

@app.get("/api/v1/highlights/{video_id}")
async def get_highlights(video_id: str, user: User = Depends(get_current_user)):
    """Retrieves all highlights for a specific video."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM highlights WHERE video_id = ? AND user_id = ?",
        (video_id, user.id)
    )
    highlights = cursor.fetchall()
    conn.close()
    
    return {"highlights": highlights}

@app.post("/api/v1/publish/{highlight_id}")
async def publish_highlight(highlight_id: str, request: PublishRequest, user: User = Depends(get_current_user)):
    """Publish a highlight to social media."""
    conn = get_db_connection()
    cursor = conn.execute(
        "SELECT * FROM highlights WHERE highlight_id = ? AND user_id = ?",
        (highlight_id, user.id)
    )
    highlight = cursor.fetchone()
    
    if not highlight:
        conn.close()
        raise HTTPException(status_code=404, detail="Highlight not found.")
    
    # Check user tier for publishing method
    user_tier = get_user_tier(user.id)
    
    if user_tier == 'premium':
        # Auto-publish for premium users
        # This would integrate with your social media posting service
        print(f"Auto-publishing highlight {highlight_id} to {request.platform}")
        status = "AGENT_PUBLISHED"
    else:
        # Manual review for standard users
        print(f"Highlight {highlight_id} ready for manual publishing to {request.platform}")
        status = "READY_FOR_MANUAL_PUBLISH"
    
    # Update status
    conn.execute(
        "UPDATE highlights SET status = ?, platform = ? WHERE highlight_id = ?",
        (status, request.platform, highlight_id)
    )
    conn.commit()
    conn.close()
    
    return {"message": f"Highlight {highlight_id} processed for publishing to {request.platform}."}

@app.get("/api/v1/status/{video_id}")
async def get_processing_status(video_id: str, user: User = Depends(get_current_user)):
    """Get processing status for a video."""
    # You might want to implement more sophisticated status tracking
    return {"status": "processing", "video_id": video_id}