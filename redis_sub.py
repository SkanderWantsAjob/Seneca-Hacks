import redis
import json

from highlight_detection import HighlightDetector
from highlight_maker import VideoCutter;

r = redis.Redis(host="localhost", port=6379, db=0)
pubsub = r.pubsub()
pubsub.subscribe("captions")

print("Listening for captions...")

for message in pubsub.listen():
    if message["type"] == "message":
        data = json.loads(message["data"])
        print("Received batch:", data)
        detector = HighlightDetector()
        highlights_json = detector.detect_highlights(data)


        if isinstance(highlights_json, str):
            highlights_json = json.loads(highlights_json)
            print("\033[91mWarning: Parsed highlights_json from string\033[0m")
        
        if len(highlights_json["intervals"]) == 0:
            print("\033[95mNo highlights detected in this batch")
            print(highlights_json, "\033[0m")
            continue
            
        print("\033[94mDetected highlights:", highlights_json, "\033[0m")
        video_cutter = VideoCutter("https://www.youtube.com/watch?v=wJDv-DhCfHk")
        video_cutter.cut_intervals(highlights_json)

    