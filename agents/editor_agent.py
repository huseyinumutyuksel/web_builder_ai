# agents/editor_agent.py
from agents.base_agent import BaseAgent
import requests
from bs4 import BeautifulSoup

class EditorAgent(BaseAgent):
    def __init__(self, name="Editor Agent"):
        super().__init__(name)

    def _find_relevant_text(self, topic, num_paragraphs=1):
        """İnternetten konuyla ilgili metin parçaları bulur."""
        search_query = f"about {topic}"
        try:
            response = requests.get(f"https://www.google.com/search?q={search_query}", headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            relevant_paragraphs = [p.text for p in paragraphs if len(p.text) > 100][:num_paragraphs]
            return relevant_paragraphs[0] if relevant_paragraphs else f"{topic.capitalize()} hakkında genel bilgiler."
        except requests.exceptions.RequestException as e:
            print(f"{self.name}: İnternetten metin bulurken hata oluştu: {e}")
            return f"{topic.capitalize()} hakkında genel bilgiler."

    def _find_relevant_images(self, topic, num_images=1):
        """İnternetten konuyla ilgili görsel bağlantıları bulur."""
        search_query = f"{topic} image"
        try:
            response = requests.get(f"https://www.google.com/search?q={search_query}&tbm=isch", headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            image_tags = soup.find_all('img')
            image_links = [img['src'] for img in image_tags if 'http' in img.get('src', '')][:num_images]
            return image_links
        except requests.exceptions.RequestException as e:
            print(f"{self.name}: İnternetten görsel bulurken hata oluştu: {e}")
            return []

    def _generate_form(self):
        """Basit bir iletişim formu HTML'i oluşturur."""
        return """
        <form>
            <div>
                <label for="name">Adınız:</label>
                <input type="text" id="name" name="name">
            </div>
            <div>
                <label for="email">E-posta Adresiniz:</label>
                <input type="email" id="email" name="email">
            </div>
            <div>
                <label for="message">Mesajınız:</label>
                <textarea id="message" name="message"></textarea>
            </div>
            <button type="submit">Gönder</button>
        </form>
        """

    def _scrape_web(self, url, selector="p"):
        """Belirtilen URL'den metin içeriği çeker."""
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            response.raise_for_status()
            print(f"Web kazıma başarılı. Status kodu: {response.status_code}")
            soup = BeautifulSoup(response.text, 'html.parser')
            elements = soup.select(selector)
            print(f"Bulunan element sayısı: {len(elements)}")
            for i, element in enumerate(elements[:5]): # İlk 5 elementi yazdır
                print(f"Element {i}: {element.text[:100]}...")
            content = "\n".join([element.text for element in elements])
            return content
        except requests.exceptions.RequestException as e:
            print(f"{self.name}: Web kazıma hatası: {e}")
            return "Web içeriği alınamadı."
    
    def _process_source(self, section_info, topic):
        """Bölüm kaynağına göre içeriği işler."""
        source = section_info.get("source")
        if source == "web_scrape":
            url = section_info.get("url")
            selector = section_info.get("selector", "p")
            return self._scrape_web(url, selector)
        elif source == "local":
            return section_info.get("content") or self._find_relevant_text(topic) # Eğer yerel içerik yoksa internetten ara
        elif source == "api":
            # API veri çekme mantığını buraya ekleyeceğiz
            return "API'den içerik (henüz uygulanmadı)"
        elif source == "local_folder":
            # Yerel dosyalardan içerik okuma mantığını buraya ekleyeceğiz
            return "Yerel klasörden içerik (henüz uygulanmadı)"
        else:
            return self._find_relevant_text(topic) # Varsayılan olarak internetten metin ara

    def execute(self, task):
        print(f"{self.name}: Generating content based on task: {task}")
        topic = task.get("topic", "General Topic")
        user_content = task.get("user_content", {})

        title = user_content.get("title", f"{topic.capitalize()} Hakkında")
        sections_data = user_content.get("sections", [])
        images = user_content.get("images", self._find_relevant_images(topic))
        videos = user_content.get("videos", [])

        processed_sections = []
        for section_info in sections_data:
            title = section_info.get("title", "Bölüm Başlığı")
            section_type = section_info.get("type", "text")
            content = ""

            if section_type == "text":
                content = self._process_source(section_info, topic)
            elif section_type == "list":
                items = section_info.get("items", [])
                if items:
                    list_items = "<ul><li>" + "</li><li>".join(items) + "</li></ul>"
                    content = list_items
                else:
                    content = "Bu bölümde listelenecek öğe bulunmuyor."
            elif section_type == "images":
                num_images = section_info.get("count", 1)
                relevant_images = self._find_relevant_images(topic, num_images)
                if relevant_images:
                    content = "".join([f'<img src="{img}" alt="{title} görseli" style="max-width: 300px; margin-right: 10px;">' for img in relevant_images])
                else:
                    content = "Bu bölümde görsel bulunmuyor."
            elif section_type == "form":
                content = self._generate_form()
            else:
                content = "Bu bölüm türü desteklenmiyor."

            processed_sections.append({"title": title, "content": content})

        content_data = {
            "title": title,
            "sections": processed_sections,
            "images": images,
            "videos": videos
        }
        return content_data