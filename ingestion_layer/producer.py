from tasks import ingest_batch

example_batch = {
    "video_id": "044_jsjcmOKtVqs",
    "batch_id": "040",
    "duration": 31.48145,
    "timestamps": [[0.0, 15.61], [15.61, 16.91], [16.91, 17.86],[17.86, 20]],
    "sentences": [
        "screen going up against RNG in the blue...",
        "and let's just zoom in",
        "Skerritt on spence",
        "oh my god this is the best entrance ever made in history"
        
    ]
}

result = ingest_batch.delay(example_batch)
print(result.get())  # Waits until worker finishes
