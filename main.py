# main.py
from fastapi import FastAPI, HTTPException,Depends,File
from pydantic import BaseModel
from typing import Optional
from pipeline import process_video
from firebase_setup import get_user_tier
from dependencies import get_current_user_id
from database import get_ready_to_publish_highlights, get_db_connection,create_table
from firebase_setup import get_user_tier # Assuming you have this file
import uuid
import datetime
import aiofiles
import os
# Initialize the database table
create_table()

app = FastAPI(title="Video Highlight Automation API")

# Request model for publishing a single highlight
class PublishRequest(BaseModel):
    highlight_id: str
    platform: str # e.g., 'youtube', 'tiktok'

# Request model to process a new video
class ProcessVideoRequest(BaseModel):
    user_id: str
    video_id: str

# --------------------
# Standard Tier Endpoints (for manual publishing)
# --------------------

@app.post("/api/v1/process-video")
async def process_video_endpoint(
    video_file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
    background_tasks: BackgroundTasks = None
):
    """
    Triggers the video processing pipeline for an uploaded video file.
    The current user's ID is automatically provided via the token.
    """
    user_tier = get_user_tier(user_id)
    if not user_tier:
        raise HTTPException(status_code=403, detail="User's tier could not be determined.")
    
    # ... (file saving logic remains the same)
    
    # Pass the user_id to the background task
    background_tasks.add_task(process_video, video_id, user_id)
    
    return {
        "message": "Video processing has started.",
        "video_id": video_id,
        "user_tier": user_tier
    }

@app.get("/api/v1/highlights")
async def get_highlights_for_user(user_id: str = Depends(get_current_user_id)):
    """Retrieves all highlights for the current user."""
    highlights = get_ready_to_publish_highlights(user_id)
    return {"highlights": highlights}

@app.post("/api/v1/publish/{highlight_id}")
async def publish_highlight_manual(highlight_id: str, request: PublishRequest):
    """
    Allows a standard user to manually publish a specific highlight.
    """
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM highlights WHERE highlight_id = ?", (highlight_id,))
    highlight = cursor.fetchone()
    conn.close()

    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found.")
    
    # Simulate calling the social media poster tool
    # In a real app, this would use the social media poster tool
    print(f"Manually publishing highlight {highlight['highlight_id']} to {request.platform}")

    # Update the status to published
    conn = get_db_connection()
    conn.execute("UPDATE highlights SET status = 'PUBLISHED' WHERE highlight_id = ?", (highlight_id,))
    conn.commit()
    conn.close()

    return {"message": f"Highlight {highlight_id} published successfully to {request.platform}."}

# --------------------
# Premium Tier Agent (The agent would hit this)
# --------------------



@app.post("/api/v1/agent-publish")
async def agent_publish_endpoint(request: PublishRequest):
    """
    This endpoint is used by the premium agent to publish highlights automatically.
    """
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM highlights WHERE highlight_id = ?", (request.highlight_id,))
    highlight = cursor.fetchone()
    conn.close()

    if not highlight:
        raise HTTPException(status_code=404, detail="Highlight not found.")
    
    # Check if the user is a premium user before allowing agent publishing
    user_tier = get_user_tier(highlight['user_id'])
    if user_tier != 'premium':
        raise HTTPException(status_code=403, detail="User is not a premium subscriber. Manual publishing required.")

    # Simulate calling the social media poster tool
    # In a real app, the agent would use its internal logic here.
    print(f"Agent-publishing highlight {highlight['highlight_id']} to {request.platform}")

    # Update the status to published by the agent
    conn = get_db_connection()
    conn.execute("UPDATE highlights SET status = 'AGENT_PUBLISHED' WHERE highlight_id = ?", (request.highlight_id,))
    conn.commit()
    conn.close()

    return {"message": f"Highlight {request.highlight_id} published by agent to {request.platform}."}