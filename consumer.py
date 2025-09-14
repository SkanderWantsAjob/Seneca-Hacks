# consumer.py
import redis
import json
import logging
import asyncio
from pipeline import VideoProcessor
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

async def consume_video_queue():
    """Consume video processing jobs from Redis queue"""
    r = redis.Redis(host="localhost", port=6379, db=0)
    processor = VideoProcessor()
    
    while True:
        try:
            # Block until a job is available
            job_data = r.blpop("video_processing_queue", timeout=30)
            
            if job_data:
                _, job_json = job_data
                job = json.loads(job_json)
                
                logger.info(f"Processing job: {job['video_id']}")
                
                # Process the video
                highlights = await processor.process_video(
                    job["video_url"],
                    job["video_id"],
                    job["user_id"]
                )
                
                logger.info(f"Completed processing {job['video_id']}. Found {len(highlights)} highlights.")
                
                # You could publish results to another queue or update database here
                
        except Exception as e:
            logger.error(f"Error processing job: {e}")
            await asyncio.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    asyncio.run(consume_video_queue())