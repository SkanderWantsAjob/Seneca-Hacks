import redis
import json

from highlight_detection import HighlightDetector

r = redis.Redis(host="localhost", port=6379, db=0)
pubsub = r.pubsub()
pubsub.subscribe("captions")

print("Listening for captions...")

for message in pubsub.listen():
    if message["type"] == "message":
        data = json.loads(message["data"])
        detector = HighlightDetector()
        highlights_json = detector.detect_highlights(data)
        print(highlights_json)