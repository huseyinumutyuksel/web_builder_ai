# agents/helper_agents/video_generator_agent.py (can be added later)
from agents.base_agent import BaseAgent

class VideoGeneratorAgent(BaseAgent):
    def __init__(self, name="Video Generator Agent"):
        super().__init__(name)

    def execute(self):
        print(f"{self.name}: Video is being generated...")
        return ["generated_video.mp4"]