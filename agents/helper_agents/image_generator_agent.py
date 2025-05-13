# agents/helper_agents/image_generator_agent.py (can be added later)
from agents.base_agent import BaseAgent

class ImageGeneratorAgent(BaseAgent):
    def __init__(self, name="Image Generator Agent"):
        super().__init__(name)

    def execute(self):
        print(f"{self.name}: Image is being generated...")
        return ["generated_image.png"]