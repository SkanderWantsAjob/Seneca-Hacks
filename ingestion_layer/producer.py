from tasks import ingest_batch

if __name__ == "__main__":
    # Example batch
    example_batch = {
        "video_id": "044_jsjcmOKtVqs",
        "batch_id": "040",
        "duration": 31.48145,
        "timestamps": [[0.0, 15.61], [15.61, 16.91], [16.91, 17.86]],
        "sentences": [
            "screen going up against RNG in the blue...",
            "and let's just zoom in",
            "Skerritt on spence"
        ]
    }

    # Send batch to ingestion queue
    result = ingest_batch.delay(example_batch)
    print("Batch sent to ingestion queue.")
    print(result.get())  # Blocks until the worker finishes
