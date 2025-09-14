import os
import subprocess
import tempfile
import yt_dlp
import wave
import json
import redis
from vosk import Model, KaldiRecognizer
from dotenv import load_dotenv
from highlight_maker import VideoCutter
from highlight_detection import HighlightDetector

load_dotenv()
r = redis.Redis(host="localhost", port=6379, db=0)

# Path to Vosk model
model = Model(os.getenv("VOSK_MODEL_PATH"))
rec = KaldiRecognizer(model, 16000)
rec.SetWords(True)

def download_youtube_chunk(url, start_time, duration, output_path):
    """Download a small chunk from YouTube using ffmpeg and yt-dlp"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']

    cmd = [
        'ffmpeg', '-y', '-loglevel', 'error',
        '-ss', str(start_time),
        '-t', str(duration),
        '-i', audio_url,
        '-ar', '16000',  # Vosk requires 16kHz
        '-ac', '1',      # mono
        output_path
    ]
    subprocess.run(cmd, check=True)

def transcribe_chunk(wav_path):
    wf = wave.open(wav_path, "rb")
    batch = []
    first_start_time = 0.0

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break

        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            if "result" in result:
                words = result["result"]
                start_time = words[0]["start"]
                end_time = words[-1]["end"]
                final_obj = {
                    "text": result["text"],
                    "start": start_time,
                    "end": end_time
                }
                if end_time - first_start_time < 60.0:
                    batch.append(final_obj)
                else:
                    r.publish("captions", json.dumps(batch))
                    batch = [final_obj]
                    first_start_time = start_time
    # publish remaining
    if batch:
        r.publish("captions", json.dumps(batch))

def main(youtube_url, chunk_duration=60):
    temp_dir = tempfile.mkdtemp()
    current_time = 0

    video_cutter = VideoCutter("video.mp4")  # optional: replace with downloaded video if needed
    detector = HighlightDetector()

    print("Streaming YouTube, processing chunks...")

    while True:
        wav_path = os.path.join(temp_dir, f"chunk_{current_time}.wav")
        try:
            download_youtube_chunk(youtube_url, current_time, chunk_duration, wav_path)
        except subprocess.CalledProcessError:
            print("Reached end of stream or error.")
            break

        transcribe_chunk(wav_path)
        current_time += chunk_duration

if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=XXXXXXX"  # your live/replay URL
    main(youtube_url)
