# agents/helper_agents/image_generator_agent.py
from agents.base_agent import BaseAgent
import os
import uuid # Benzersiz dosya adları için
# Pillow (PIL) gibi bir kütüphane ile gerçekten görsel oluşturulabilir.
# from PIL import Image, ImageDraw, ImageFont

class ImageGeneratorAgent(BaseAgent):
    def __init__(self, name="Image Generator Agent"):
        super().__init__(name)
        self.output_folder = "output/generated_images"
        os.makedirs(self.output_folder, exist_ok=True)

    def execute(self, task=None): # İmza güncellendi
        """
        Task (dict, optional):
            - "prompt": (str) Görsel için metin istemi.
            - "width": (int) Piksel cinsinden genişlik.
            - "height": (int) Piksel cinsinden yükseklik.
        Returns:
            (list): Oluşturulan görsel dosyalarının yollarını içeren bir liste.
        """
        prompt = "Default Topic"
        width = 300
        height = 200

        if task:
            prompt = task.get("prompt", prompt)
            width = task.get("width", width)
            height = task.get("height", height)

        print(f"{self.name}: Generating image for prompt='{prompt}' ({width}x{height})...")
        
        # Gerçek bir görsel oluşturma yerine placeholder kullanalım
        # Pillow ile basit bir görsel oluşturma örneği (isteğe bağlı):
        # try:
        #     img = Image.new('RGB', (width, height), color = (73, 109, 137))
        #     d = ImageDraw.Draw(img)
        #     try:
        #         font = ImageFont.truetype("arial.ttf", 20)
        #     except IOError:
        #         font = ImageFont.load_default()
        #     text_bbox = d.textbbox((0,0), prompt, font=font)
        #     text_width = text_bbox[2] - text_bbox[0]
        #     text_height = text_bbox[3] - text_bbox[1]
        #     d.text(((width-text_width)/2, (height-text_height)/2), prompt, fill=(255,255,0), font=font)
        #     filename = f"{prompt.replace(' ','_')}_{uuid.uuid4().hex[:6]}.png"
        #     filepath = os.path.join(self.output_folder, filename)
        #     img.save(filepath)
        #     print(f"{self.name}: Image saved to {filepath}")
        #     return [filepath]
        # except Exception as e:
        #     print(f"{self.name}: Error generating image with Pillow: {e}")
        #     # Fallback to placeholder URL
        
        # Placeholder URL'i (picsum.photos gibi) veya yerel bir placeholder dosyası döndürelim
        # Şimdilik sadece bir dosya adı döndürüyoruz, bu dosyanın var olması gerekir.
        # Veya EditorAgent'taki gibi bir URL döndürebiliriz.
        # Bu ajan "gerçek" bir dosya oluşturmalı.
        
        # Basit bir placeholder dosyası oluşturalım (eğer Pillow yoksa veya istenmiyorsa)
        filename = f"placeholder_{prompt.replace(' ','_')}_{uuid.uuid4().hex[:6]}.png"
        filepath = os.path.join(self.output_folder, filename)
        try:
            with open(filepath, "w") as f: # Gerçek bir PNG değil, sadece bir dosya.
                f.write(f"Placeholder image for: {prompt}\nSize: {width}x{height}")
            print(f"{self.name}: Placeholder image file created at {filepath}")
            return [filepath] # Dosya yolunu döndür
        except Exception as e:
            print(f"{self.name}: Error creating placeholder image file: {e}")
            return [f"https://via.placeholder.com/{width}x{height}.png?text={prompt.replace(' ','+')}"] # Fallback URL