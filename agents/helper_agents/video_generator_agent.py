import os
import subprocess
import uuid
import logging
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class VideoGeneratorAgent(BaseAgent):
    def __init__(self, name="Video Generator Agent"):
        super().__init__(name)
        self.output_folder = "output/generated_videos"
        os.makedirs(self.output_folder, exist_ok=True)

    def execute(self, task=None):
        prompt = task.get("prompt", "Default Video Topic") if task else "Default Video Topic"
        duration = task.get("duration", 10) if task else 10  # seconds

        logger.info(f"{self.name}: Generating video for '{prompt}' with duration {duration}s")
        
        try:
            # Generate a unique filename
            filename = f"video_{prompt.replace(' ', '_')}_{uuid.uuid4().hex[:6]}.mp4"
            filepath = os.path.join(self.output_folder, filename)
            
            # FFmpeg command: Create a video with a black background and text
            cmd = [
                "ffmpeg",
                "-f", "lavfi",
                "-i", f"color=c=black:s=640x480:d={duration}",
                "-vf", f"drawtext=text='{prompt}':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=(h-text_h)/2",
                "-c:a", "aac",
                "-strict", "experimental",
                "-y",  # Overwrite output file if it exists
                filepath
            ]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            logger.info(f"{self.name}: Video saved to {filepath}")
            return [filepath]
        except subprocess.CalledProcessError as e:
            logger.error(f"{self.name}: FFmpeg error: {e}", exc_info=True)
            return ["Error: Video generation failed"]
        except FileNotFoundError:
            logger.error(f"{self.name}: FFmpeg not found. Please install FFmpeg.")
            return ["Error: FFmpeg not installed"]