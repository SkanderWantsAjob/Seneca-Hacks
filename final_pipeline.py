# pipeline.py
from ingestion import CaptionIngestor
from highlight_detection import HighlightDetector
from aggregation import HighlightAggregator
from video_preparation import VideoPreparer
from storage import MetadataStore

def main():
    """
    Main orchestration pipeline for highlight detection.
    Assumes all layers are already implemented.
    """
    
    # -------------------------------
    # 1. Ingestion Layer
    # -------------------------------
    print("[Pipeline] Starting ingestion layer...")
    ingestor = CaptionIngestor(source="batches_folder_or_api")
    
    # Get batches one by one (could be streaming or batch)
    for batch in ingestor.get_batches():
        batch_id = batch.batch_id
        video_id = batch.video_id
        print(f"[Pipeline] Ingested batch {batch_id} for video {video_id}")
        
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
        print(f"[Pipeline] Aggregated highlights for batch {batch_id}")
        
        # -------------------------------
        # 4. Video Preparation Layer
        # -------------------------------
        video_preparer = VideoPreparer()
        video_clips = video_preparer.prepare_clips(video_id, aggregated_highlights)
        print(f"[Pipeline] Video clips prepared for batch {batch_id}")
        
        # -------------------------------
        # 5. Storage Layer
        # -------------------------------
        store = MetadataStore()
        store.save_highlights(video_id, batch_id, aggregated_highlights, video_clips)
        print(f"[Pipeline] Stored highlights for batch {batch_id}")
    
    print("[Pipeline] All batches processed successfully!")

if __name__ == "__main__":
    main()
