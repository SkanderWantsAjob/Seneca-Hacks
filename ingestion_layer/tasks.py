from celery import Celery
from schemas import CaptionBatch
import json

# Create Celery app
app = Celery(
    "ingestion_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@app.task
def ingest_batch(batch_data):
    """
    Receives a batch, validates it, and returns a ready-to-process batch.
    Downstream workers will pick it up from here.
    """
    try:
        # Validate using Pydantic
        batch = CaptionBatch(**batch_data)
        print(f"[Ingestion] Valid batch: {batch.batch_id} for video {batch.video_id}")
        # Here you could push to a processing queue or database
        return batch.dict()
    except Exception as e:
        print(f"[Ingestion] Invalid batch: {e}")
        return {"error": str(e)}
