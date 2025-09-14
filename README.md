# 🎮 FlashCut
**AI-powered Highlight Detection for Esports Videos**

---

## 📖 Description
Esports tournaments happen **every single day**, across multiple games and regions. Fans are flooded with hours of matches, each packed with **intense plays, clutch moments, and crowd-hype commentary**.

### The Problem
- A single match can last **over an hour**.  
- Fans don’t always have time to rewatch everything.  
- The best moments often get buried inside long streams.

### Solution: FlashCut
We take a **video URL** (currently supporting static or live YouTube videos), extract the **commentator captions** (casters’ live reactions, hype, and analysis), and use AI to detect the most exciting highlights.

The output is a set of **automatically generated highlight videos** (shorts/reels) that serve as a clean summary of the best moments, ready to:
- ⚡ **Relive the hype** when you don’t have time for the full match.  
- 📱 **Share highlights on social media** to grow the fanbase.

---

## 🛠 How It Works

### 1. Caption Generation (Vosk)
- We transcribe the game commentary using [Vosk](https://alphacephei.com/vosk/).  
- Vosk is an **open-source speech recognition toolkit** (Apache 2.0 licensed).  
- Runs offline, supports multiple languages, and provides **timestamps + sentences**.

### 2. Highlight Detection (LLM via Groq API)
- We use the **Llama 3.3 70B model**, served through the [Groq API](https://console.groq.com/docs/overview).  
- Groq supports open-source models, offers a free tier (with usage limits), and has paid plans for higher scale.  
- The model scans commentary captions for excitement: when casters go wild or a surprising play happens.  
- Output: **highlight intervals in JSON**, with:
  - Start + end timestamps  
  - A short explanation for the reel caption (e.g., “Incredible turn of events during game-deciding team fight”)

### 3. Pipeline Orchestration (Layered)
#### Ingestion Layer
- The user provides a **video URL** (YouTube live or static).  
- The pipeline prepares it for processing.

#### Caption Extraction Layer
- Using Vosk, we generate **captions with timestamps**.  
- Result: a transcript with exact timing.

#### Highlight Analysis Layer
- Captions are sent in batches to the LLM (Llama 3.3 / 70B) via Groq API.  
- The model detects **exciting moments** with a precisely crafted prompt.  
- Output: a set of **highlight timestamps** with reason.

#### Video Processing Layer
- Using **FFmpeg**, the original video is cut into clips based on timestamps.  
- FFmpeg allows us to:
  - Trim highlights precisely  
  - Maintain video quality while optimizing file size

#### Delivery Layer
- Generated highlight clips are returned to the user, ready to watch or post.

---

## ▶️ How to Run the Project Step by Step

### 1. Prerequisites
**Install Redis with Docker:**
```bash
docker run -p 6379:6379 redis:7-alpine
```
Install FFmpeg

Ensure it is on your PATH.

Download a Vosk model
Example: vosk-model-small-en-us-0.15

Extract somewhere and update .env:

VOSK_MODEL_PATH=/path/to/vosk-model-small-en-us-0.15


Groq API key

Add your key to .env:

GROQ_API=sk_xxx_your_key

2. Install Python Dependencies
```bash

pip install -r requirements.txt
```

4. Start FastAPI App

In one terminal:
```bash

uvicorn main:app --reload --port 8000
````


API is live at http://127.0.0.1:8000

4. Start Workers

Terminal 2: Transcriber Worker
```bash


python transcriber_worker.py
```

Listens on video_processing_queue, streams captions with Vosk, downloads video.

Terminal 3: Highlight Worker
```bash


python highlight_worker.py
```


Listens to captions:{video_id}, calls LLM for highlights, cuts clips with FFmpeg.

5. Kick Off a Job

In another terminal (or Postman / cURL):
```bash


curl -X POST http://127.0.0.1:8000/api/v1/process-video \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://www.youtube.com/watch?v=wJDv-DhCfHk"}'
```


Response:

{
  "message": "Video processing job queued.",
  "video_id": "a6a5f6a2-6b4c-4b1a-bb12-...."
}

6. Observe

transcriber_worker prints batches of captions being published.

highlight_worker prints detected highlight intervals and creates .mp4 clips inside ./clips.

Highlights are stored in highlights.db.

7. Query Results
```bash

curl http://127.0.0.1:8000/api/v1/highlights/<video_id>
```


Example response:

{
  "highlights": [
    {
      "highlight_id": "...",
      "video_id": "...",
      "start_time": 54.0,
      "end_time": 72.0,
      "video_path": "clips/clip_1-00-49_____01-14.mp4",
      "title": "",
      "description": "",
      "platform": "",
      "status": "READY"
    }
  ]
}
