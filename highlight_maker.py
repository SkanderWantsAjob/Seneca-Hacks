import os
import subprocess

class VideoCutter:
    def __init__(self, video_path, output_dir="clips"):
        self.video_path = video_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.clip_index = 1  # keep count across multiple calls

    def cut_intervals(self, entry):
        # entry is a dict like {'intervals': [...]}
        intervals = entry.get("intervals", [])
        if not intervals:
            return  # skip if empty

        for interval in intervals:
            self.clip_index += 1
            start_time = max(0, interval["start"] - 5)
            end_time = interval["end"] + 2
            duration = end_time - start_time
            

            start_min, start_sec = divmod(int(interval["start"] - 5), 60)
            end_min, end_sec = divmod(int(interval["end"] + 2), 60)

            output_file = os.path.join(
                self.output_dir,
                f"clip_{self.clip_index}-{start_min:02d}-{start_sec:02d}_____{end_min:02d}-{end_sec:02d}.mp4"
            )

        #     cmd = [
        #         "ffmpeg", "-y", "-loglevel", "error", "-i", self.video_path,
        #     "-ss", str(start_time), "-t", str(duration),
        #     "-c:v", "libx264",  # re-encode video for exact cut
        #     "-c:a", "aac",      # re-encode audio
        #     "-strict", "experimental",  # for some older ffmpeg versions
        #     output_file
        # ]

            cmd = [
            "ffmpeg", "-y", "-loglevel", "error",
            "-ss", str(start_time),
            "-i", self.video_path,
            "-t", str(duration),
            "-c:v", "libx264",
            "-c:a", "aac",
            "-b:a", "128k",      # force audio bitrate
            "-ac", "2",           # stereo
            "-map", "0",          # include all streams
            output_file
            ]


            print(f"\033[93mCreating clip {self.clip_index}: {start_min:02d}:{start_sec:02d}s → {end_min:02d}:{end_sec:02d}s\033[0m")

            subprocess.run(cmd, check=True)
            
