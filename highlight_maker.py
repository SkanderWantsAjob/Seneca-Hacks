import os
import subprocess

def resolve_url(video_path):
    if video_path.startswith("http"):
        # Use yt-dlp to get direct URL
        direct_url = subprocess.check_output(
            ["yt-dlp", "-g", video_path], text=True
        ).strip()
        return direct_url
    return video_path
class VideoCutter:
    def __init__(self, video_path, output_dir="clips"):
        self.video_path = resolve_url(video_path)
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
            start_time = max(0, interval["start"] - 7 )
            end_time = interval["end"] - 5
            duration = end_time - start_time
            

            start_min, start_sec = divmod(int(start_time), 60)
            end_min, end_sec = divmod(int(end_time), 60)

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
                "-i", self.video_path,     # input first
                "-ss", str(start_time),    # then seek
                "-t", str(duration),
                "-c:v", "libx264",
                "-c:a", "aac",
                "-b:a", "128k",
                "-ac", "2",
                output_file
            ]



            print(f"\033[93mCreating clip {self.clip_index}: {start_min:02d}:{start_sec:02d}s → {end_min:02d}:{end_sec:02d}s\033[0m")

            subprocess.run(cmd, check=True)
            
