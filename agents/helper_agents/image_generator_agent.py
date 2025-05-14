import os
import uuid
import logging
from PIL import Image, ImageDraw, ImageFont
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ImageGeneratorAgent(BaseAgent):
    def __init__(self, name="Image Generator Agent"):
        super().__init__(name)
        self.output_folder = "output/generated_images"
        os.makedirs(self.output_folder, exist_ok=True)

    def execute(self, task=None):
        prompt = task.get("prompt", "Default Topic") if task else "Default Topic"
        width = task.get("width", 300) if task else 300
        height = task.get("height", 200) if task else 200

        logger.info(f"{self.name}: Generating image for '{prompt}' ({width}x{height})")
        try:
            img = Image.new('RGB', (width, height), color=(73, 109, 137))
            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()
            text_bbox = draw.textbbox((0, 0), prompt, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            draw.text(((width - text_width) / 2, (height - text_height) / 2), prompt, fill=(255, 255, 0), font=font)
            
            filename = f"{prompt.replace(' ', '_')}_{uuid.uuid4().hex[:6]}.png"
            filepath = os.path.join(self.output_folder, filename)
            img.save(filepath)
            logger.info(f"{self.name}: Image saved to {filepath}")
            return [filepath]
        except Exception as e:
            logger.error(f"{self.name}: Error generating image: {e}", exc_info=True)
            return [f"https://via.placeholder.com/{width}x{height}.png?text={prompt.replace(' ', '+')}"]