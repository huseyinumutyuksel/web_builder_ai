# agents/editor_agent.py
from agents.base_agent import BaseAgent
import requests
from bs4 import BeautifulSoup
import logging # Logging için eklendi

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EditorAgent(BaseAgent):
    def __init__(self, name="Editor Agent"):
        super().__init__(name)

    def _find_relevant_text(self, topic, num_paragraphs=1):
        """
        İnternetten konuyla ilgili metin parçaları bulur.
        UYARI: Google arama sonuçlarını doğrudan kazımak güvenilir değildir ve Google'ın
        kullanım koşullarına aykırı olabilir. Bu fonksiyon demo amaçlıdır.
        Gerçek uygulamalarda güvenilir API'ler kullanılmalıdır.
        """
        logger.info(f"Searching for text on '{topic}' using web scraping (Google Search).")
        search_query = f"about {topic}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        try:
            # Basit bir arama motoru URL'i, gerçek bir API daha iyi olurdu.
            # DuckDuckGo HTML sonuçları daha parse edilebilir olabilir.
            # response = requests.get(f"https://html.duckduckgo.com/html/?q={search_query}", headers=headers, timeout=10)
            response = requests.get(f"https://www.google.com/search?q={search_query}", headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Google'ın yapısı sık değiştiği için bu seçiciler güvenilir olmayabilir.
            # Örnek olarak birkaç potansiyel seçici:
            # paragraphs = soup.select("div.VwiC3b, div.s3v9rd, div.AP7Wnd") # Örnek seçiciler
            paragraphs_tags = soup.find_all('p')
            
            relevant_paragraphs = []
            for p in paragraphs_tags:
                text = p.get_text(separator=' ', strip=True)
                if len(text) > 150 and topic.lower() in text.lower(): # Daha ilgili metinler bulmaya çalışalım
                    relevant_paragraphs.append(text)
                    if len(relevant_paragraphs) >= num_paragraphs:
                        break
            
            if relevant_paragraphs:
                return "\n\n".join(relevant_paragraphs)
            else:
                logger.warning(f"Could not find sufficiently long/relevant paragraphs for '{topic}' via Google Search.")
                return f"{topic.capitalize()} hakkında internetten otomatik olarak anlamlı bir metin bulunamadı. Lütfen manuel olarak ekleyin veya farklı bir kaynak deneyin."

        except requests.exceptions.Timeout:
            logger.error(f"Timeout while trying to find text for '{topic}'.")
            return f"{topic.capitalize()} hakkında bilgi alınırken zaman aşımı oluştu."
        except requests.exceptions.RequestException as e:
            logger.error(f"Error finding text from internet for '{topic}': {e}")
            return f"{topic.capitalize()} hakkında bilgi alınırken bir hata oluştu: {e}"

    def _find_relevant_images(self, topic, num_images=1):
        """
        İnternetten konuyla ilgili görsel bağlantıları bulur.
        UYARI: Google Görsel arama sonuçlarını doğrudan kazımak güvenilir değildir.
        Bu fonksiyon demo amaçlıdır. Gerçek uygulamalarda API'ler kullanılmalıdır.
        """
        logger.info(f"Searching for images of '{topic}' using web scraping (Google Images).")
        search_query = f"{topic} image"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        image_links = []
        try:
            # response = requests.get(f"https://www.google.com/search?q={search_query}&tbm=isch", headers=headers, timeout=10)
            # response.raise_for_status()
            # soup = BeautifulSoup(response.text, 'html.parser')
            # image_tags = soup.find_all('img', limit=num_images * 2) # Biraz fazla alıp ayıklayalım

            # Alternatif olarak, daha basit bir görsel API veya placeholder kullanılabilir
            # Örnek: picsum.photos (rastgele görseller)
            for i in range(num_images):
                # Daha anlamlı görseller için konuyla ilgili anahtar kelimeler kullanılabilir
                # ancak bu placeholder servisi bunu desteklemez.
                # Gerçek bir API ( örn: Unsplash, Pexels) daha iyi olurdu.
                width = 300 + i*50
                height = 200 + i*30
                image_links.append(f"https://picsum.photos/{width}/{height}?random&topic={topic.replace(' ','_')}")

            # Güvenilir olmayan Google scraping yerine placeholder kullandık.
            # for img in image_tags:
            #     src = img.get('src')
            #     if src and src.startswith('http') and not "gstatic.com" in src: # Basit filtreleme
            #         image_links.append(src)
            #         if len(image_links) >= num_images:
            #             break
            if not image_links and num_images > 0: # Eğer picsum da başarısız olursa (gerçi genelde olmaz)
                 logger.warning(f"Could not find images for '{topic}' via placeholder. Returning default.")
                 image_links.append(f"https://via.placeholder.com/300x200.png?text=No+Image+Found+for+{topic.replace(' ','+')}")


        except requests.exceptions.Timeout:
            logger.error(f"Timeout while trying to find images for '{topic}'.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error finding images from internet for '{topic}': {e}")
        
        if not image_links and num_images > 0: # Hata durumunda veya hiç bulunamazsa
            logger.warning(f"No images found for '{topic}'. Providing placeholders.")
            for i in range(num_images):
                 image_links.append(f"https://via.placeholder.com/300x200.png?text={topic.replace(' ','+')}+{i+1}")
        return image_links[:num_images]


    def _generate_form(self):
        """Basit bir iletişim formu HTML'i oluşturur."""
        return """
        <form action="#" method="post">
            <div>
                <label for="name">Adınız:</label>
                <input type="text" id="name" name="name" required>
            </div>
            <div>
                <label for="email">E-posta Adresiniz:</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div>
                <label for="message">Mesajınız:</label>
                <textarea id="message" name="message" rows="5" required></textarea>
            </div>
            <button type="submit">Gönder</button>
        </form>
        """

    def _scrape_web(self, url, selector="p"):
        """Belirtilen URL'den metin içeriği çeker."""
        logger.info(f"Scraping web content from {url} using selector '{selector}'")
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            response.raise_for_status()
            logger.info(f"Web scraping successful. Status code: {response.status_code} from {url}")
            soup = BeautifulSoup(response.text, 'html.parser')
            elements = soup.select(selector)
            
            if not elements:
                logger.warning(f"No elements found with selector '{selector}' at {url}.")
                # Fallback to trying to get all paragraphs if specific selector fails
                elements = soup.find_all('p')
                if not elements:
                    logger.warning(f"No paragraph elements found either at {url}.")
                    return "Belirtilen URL'den içerik alınamadı veya seçiciyle eşleşen element bulunamadı."

            # İlk birkaç paragrafı veya anlamlı bir bölümü alalım
            content_parts = []
            char_count = 0
            for element in elements:
                text = element.get_text(separator=' ', strip=True)
                if len(text) > 50: # Çok kısa metinleri atlayalım
                    content_parts.append(text)
                    char_count += len(text)
                    if char_count > 2000 and len(content_parts) > 2 : # Çok uzun olmasın
                        break
            content = "\n\n".join(content_parts)
            return content if content else "Belirtilen URL veya seçici ile anlamlı içerik bulunamadı."
        except requests.exceptions.Timeout:
            logger.error(f"Timeout during web scraping from {url}.")
            return "Web içeriği alınırken zaman aşımı oluştu."
        except requests.exceptions.RequestException as e:
            logger.error(f"Web scraping error from {url}: {e}")
            return f"Web içeriği alınamadı: {e}"
    
    def _process_source(self, section_info, topic):
        """Bölüm kaynağına göre içeriği işler."""
        source_type = section_info.get("source")
        content = section_info.get("content") # Yerel içerik öncelikli

        if source_type == "local":
            if content:
                return content
            else:
                logger.warning(f"Local source specified for section '{section_info.get('title')}' but no content provided. Falling back to web search for topic '{topic}'.")
                return self._find_relevant_text(topic) # Eğer yerel içerik yoksa internetten ara
        elif source_type == "web_scrape":
            url = section_info.get("url")
            selector = section_info.get("selector", "p") # Varsayılan seçici 'p'
            if not url:
                logger.error("Web scrape source specified but no URL provided.")
                return "Web kazıma için URL belirtilmemiş."
            return self._scrape_web(url, selector)
        elif source_type == "api":
            # API veri çekme mantığını buraya ekleyeceğiz
            logger.info("API source type (not yet implemented).")
            return "API'den içerik (henüz uygulanmadı)"
        elif source_type == "local_folder":
            # Yerel dosyalardan içerik okuma mantığını buraya ekleyeceğiz
            logger.info("Local folder source type (not yet implemented).")
            return "Yerel klasörden içerik (henüz uygulanmadı)"
        elif content: # Eğer source belirtilmemiş ama content varsa onu kullan
             return content
        else: # Varsayılan veya bilinmeyen kaynak türü
            logger.info(f"Defaulting to web search for section '{section_info.get('title')}' on topic '{topic}'.")
            return self._find_relevant_text(topic) 

    def execute(self, task): # İmza zaten task alıyordu
        logger.info(f"Editor Agent starting content generation for task: {task.get('topic')}")
        topic = task.get("topic", "General Topic")
        user_content_spec = task.get("user_content", {}) # Adını değiştirdim karışıklığı önlemek için

        # Ana başlık kullanıcıdan veya konudan türetilebilir
        final_title = user_content_spec.get("title", f"{topic.capitalize()} Web Sitesi")
        
        sections_data = user_content_spec.get("sections", [])
        
        # user_content_spec'ten gelen ana görselleri alalım, bunlar EditorAgent tarafından değiştirilmez.
        # Bu görseller ManagerAgent tarafından siteye genel olarak eklenebilir.
        top_level_images = user_content_spec.get("images", [])
        top_level_videos = user_content_spec.get("videos", [])

        processed_sections = []
        for section_info in sections_data:
            section_title = section_info.get("title", "Bölüm Başlığı")
            section_type = section_info.get("type", "text")
            logger.info(f"Processing section: '{section_title}' of type '{section_type}'")
            
            content_html = ""

            if section_type == "text":
                content_html = self._process_source(section_info, topic)
            elif section_type == "list":
                items = section_info.get("items", [])
                if items:
                    list_items_html = "<ul>\n"
                    for item in items:
                        list_items_html += f"  <li>{item}</li>\n"
                    list_items_html += "</ul>"
                    content_html = list_items_html
                else:
                    content_html = "<p>Bu bölümde listelenecek öğe bulunmuyor.</p>"
            elif section_type == "images": # Bu bölüm içindeki görselleri ifade eder
                num_images = section_info.get("count", 1)
                # Konu başlığına göre veya bölüm başlığına göre görsel aranabilir.
                image_search_topic = section_info.get("image_topic", section_title) # Bölüme özel görsel konusu
                relevant_image_urls = self._find_relevant_images(image_search_topic, num_images)
                if relevant_image_urls:
                    content_html = "".join([f'<img src="{img_url}" alt="{section_title} için görsel" style="max-width: 100%; height: auto; margin: 5px;">' for img_url in relevant_image_urls])
                else:
                    content_html = "<p>Bu bölüm için uygun görsel bulunamadı.</p>"
            elif section_type == "form":
                content_html = self._generate_form()
            else:
                logger.warning(f"Unsupported section type: {section_type}")
                content_html = f"<p>Bu bölüm türü ('{section_type}') desteklenmiyor.</p>"

            processed_sections.append({"title": section_title, "content": content_html})

        content_data_for_manager = {
            "page_title": final_title, # Sayfa başlığı (HTML <title> için)
            "main_heading": user_content_spec.get("main_heading", final_title), # Ana H1 başlığı için
            "sections": processed_sections,
            "banner_images": top_level_images, # Bunlar ManagerAgent'ın kullanacağı ana görseller
            "videos": top_level_videos # Henüz kullanılmıyor
        }
        logger.info(f"Editor Agent finished content processing for '{topic}'.")
        return content_data_for_manager