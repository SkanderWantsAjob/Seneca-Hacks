import subprocess
import json
import redis
import os
from dotenv import load_dotenv
from vosk import Model, KaldiRecognizer
load_dotenv()
# Connect to Redis
r = redis.Redis(host="localhost", port=6379, db=0)

# Load model
model = Model(os.getenv("VOSK_MODEL_PATH"))
rec = KaldiRecognizer(model, 16000)
rec.SetWords(True)

# Command to get audio from YouTube link (replace URL with user input)
url = "https://www.youtube.com/watch?v=wJDv-DhCfHk"
cmd = [
    "yt-dlp", "-o", "-", url,
    "|", "ffmpeg", "-i", "pipe:0",
    "-ar", "16000", "-ac", "1", "-f", "s16le", "pipe:1"
]

# Run pipeline
proc = subprocess.Popen(" ".join(cmd), shell=True, stdout=subprocess.PIPE)

first_start_time = 0.0
batch = []
while True:
    data = proc.stdout.read(4000)
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
                # Publish to Redis channel
                r.publish("captions", json.dumps(batch))
                batch = []
                batch.append(final_obj)
                first_start_time = start_time   
