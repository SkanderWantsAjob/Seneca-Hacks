from ingestion import CaptionIngestor
from highlight_detection import HighlightDetector
from aggregation import HighlightAggregator
from video_preparation import VideoPreparer
from storage import MetadataStore

def process_video(video_id: str, user_id: str):
    """
    Core pipeline logic for highlight detection,
    designed to be called by an external process like an API.
    """
    # -------------------------------
    # 1. Ingestion Layer
    # -------------------------------
    print(f"[Pipeline] Starting ingestion for video {video_id}...")
    ingestor = CaptionIngestor(source="batches_folder_or_api")
    
    # Get batches one by one (could be streaming or batch)
    for batch in ingestor.get_batches():
        # Using the provided video_id for a single video.
        batch_id = batch.batch_id
        
        # -------------------------------
        # 2. Highlight Detection Layer
        # -------------------------------
        detector = HighlightDetector()
        highlight_json = detector.detect_highlights(batch)
        print(f"[Pipeline] Highlights detected for batch {batch_id}")
        
        # -------------------------------
        # 3. Aggregation Layer
        # -------------------------------
        aggregator = HighlightAggregator()
        aggregated_highlights = aggregator.merge(video_id, highlight_json)
        print(f"[Pipeline] Aggregated highlights for video {video_id}")
        
        # -------------------------------
        # 4. Video Preparation Layer
        # -------------------------------
        video_preparer = VideoPreparer()
        video_clips = video_preparer.prepare_clips(video_id, aggregated_highlights)
        print(f"[Pipeline] Video clips prepared for video {video_id}")
        
        # -------------------------------
        # 5. Storage Layer
        # -------------------------------
        store = MetadataStore()
        store.save_highlights(user_id, video_id, aggregated_highlights, video_clips)
        print(f"[Pipeline] Stored highlights for video {video_id} for user {user_id}")
    
    print(f"[Pipeline] All batches processed successfully for video {video_id}!")