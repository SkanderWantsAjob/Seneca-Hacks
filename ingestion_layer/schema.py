from pydantic import BaseModel, Field
from typing import List

class CaptionBatch(BaseModel):
    video_id: str
    batch_id: str
    duration: float
    timestamps: List[List[float]]  # [[start, end], ...]
    sentences: List[str]
