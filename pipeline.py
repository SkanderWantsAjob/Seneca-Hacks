# pipeline.py
import json
import redis
import os
import wave
import subprocess
import logging
import asyncio
from dotenv import load_dotenv
from vosk import Model, KaldiRecognizer
from pytube import YouTube
import uuid
import re
from typing import List, Dict, Any
from highlight_detection import HighlightDetector
from highlight_maker import VideoCutter
import aiofiles

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Redis setup
r = redis.Redis(host="localhost", port=6379, db=0)

class VideoProcessor:
    """Main video processing class that coordinates the pipeline"""
    
    def __init__(self):
        self.vosk_model = Model(os.getenv("VOSK_MODEL_PATH"))
        self.highlight_detector = HighlightDetector()
        
    async def process_video(self, youtube_url: str, video_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Main processing pipeline"""
        try:
            # 1. Download video
            video_path = await self.download_video(youtube_url, video_id)
            
            # 2. Extract audio and transcribe
            transcript = await self.transcribe_video(video_path, video_id)
            
            # 3. Detect highlights
            highlights = self.highlight_detector.detect_highlights(transcript)
            
            # 4. Cut highlights
            highlight_videos = await self.cut_highlights(video_path, highlights, video_id)
            
            return highlight_videos
            
        except Exception as e:
            logger.error(f"Error processing video {video_id}: {e}")
            raise
    
    async def download_video(self, youtube_url: str, video_id: str) -> str:
        """Download YouTube video"""
        yt = YouTube(youtube_url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').first()
        
        # Create user directory if it doesn't exist
        user_dir = f"videos/{video_id}"
        os.makedirs(user_dir, exist_ok=True)
        
        video_path = f"{user_dir}/original.mp4"
        stream.download(output_path=user_dir, filename="original.mp4")
        
        return video_path
    
    async def transcribe_video(self, video_path: str, video_id: str) -> List[Dict]:
        """Extract audio and transcribe using VOSK"""
        # Extract audio to WAV format
        audio_path = f"videos/{video_id}/audio.wav"
        command = [
            'ffmpeg', '-i', video_path, 
            '-ar', '16000', '-ac', '1', 
            '-f', 'wav', audio_path
        ]
        
        subprocess.run(command, check=True)
        
        # Transcribe using VOSK
        transcript = []
        rec = KaldiRecognizer(self.vosk_model, 16000)
        rec.SetWords(True)
        
        with wave.open(audio_path, 'rb') as wf:
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if 'result' in result:
                        transcript.extend(result['result'])
            
            # Final result
            final_result = json.loads(rec.FinalResult())
            if 'result' in final_result:
                transcript.extend(final_result['result'])
        
        # Clean up audio file
        os.remove(audio_path)
        
        return transcript
    
    async def cut_highlights(self, video_path: str, highlights: List[Dict], video_id: str) -> List[Dict]:
        """Cut video at highlight timestamps"""
        highlight_videos = []
        video_cutter = VideoCutter(video_path)
        
        for i, highlight in enumerate(highlights):
            highlight_id = str(uuid.uuid4())
            output_path = f"videos/{video_id}/highlight_{i}.mp4"
            
            # Cut the video segment
            success = video_cutter.cut_segment(
                highlight['start_time'],
                highlight['end_time'],
                output_path
            )
            
            if success:
                highlight_videos.append({
                    'highlight_id': highlight_id,
                    'start_time': highlight['start_time'],
                    'end_time': highlight['end_time'],
                    'video_path': output_path,
                    'title': f"Highlight {i+1}",
                    'description': f"Auto-generated highlight from video {video_id}"
                })
        
        return highlight_videos

async def process_video(video_url: str, video_id: str, user_id: str):
    """Main processing function"""
    processor = VideoProcessor()
    return await processor.process_video(video_url, video_id, user_id)