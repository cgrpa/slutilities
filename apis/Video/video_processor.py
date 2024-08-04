import subprocess
import os

class VideoProcessor:
    def __init__(self):
        self.ffmpeg_path = "ffmpeg"

    def extract_audio(self, input_video_path, output_audio_path):
        if not os.path.isfile(input_video_path):
            raise FileNotFoundError(f"Input video file '{input_video_path}' does not exist.")
        
        command = [
            self.ffmpeg_path,
            '-i', input_video_path,
            '-vn',  # No video
            '-acodec', 'pcm_s16le',  # Audio codec: PCM signed 16-bit little-endian
            '-ar', '44100',  # Audio sample rate: 44100 Hz
            '-ac', '2',  # Audio channels: 2 (stereo)
            output_audio_path
        ]

        try:
            subprocess.run(command, check=True)
            print(f"Audio extracted successfully to '{output_audio_path}'")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")
            raise
