# agents/manager_agent.py

from agents.base_agent import BaseAgent
# Diğer agent importları olduğu gibi kalır
from agents.design_agent import DesignAgent
from agents.dynamic_agent import DynamicAgent
from agents.backend_agent import BackendAgent
from agents.editor_agent import EditorAgent
from agents.reviewer_agent import ReviewerAgent
from agents.server_agent import ServerAgent
# from agents.helper_agents.image_generator_agent import ImageGeneratorAgent # main.py'de import ediliyor, burada gerek yok
# from agents.helper_agents.video_generator_agent import VideoGeneratorAgent

import os
import schedule
import time
from threading import Thread
import shutil # Görsel kopyalamak için eklendi
from bs4 import BeautifulSoup # HTML manipülasyonu için eklendi
import re # Gerekirse diye duruyor ama BeautifulSoup tercih edilecek
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ManagerAgent(BaseAgent):
    def __init__(self, name="Manager Agent"):
        super().__init__(name)
        self.agents = {}
        self.registered_sites = {} # Site bilgilerini (klasör, URL, kullanıcı içeriği) saklar
        self.running_servers = {} # site_topic -> ServerAgent instance
        self.scheduler_thread = None
        self.should_run_scheduler = True # Adını değiştirdim daha anlaşılır olması için

    def add_agent(self, agent):
        self.agents[agent.name] = agent
        logger.info(f"{agent.name} added to the system.")

    def _copy_local_assets(self, source_assets_list, site_folder):
        copied_asset_paths = []
        if not source_assets_list:
            return copied_asset_paths
            
        for asset_file_name in source_assets_list:
            # Proje ana dizininde olduğunu varsayıyoruz, gerekirse bir kaynak klasörü belirtilebilir.
            # Örn: source_asset_path = os.path.join("project_assets", asset_file_name)
            source_asset_path = asset_file_name 
            
            # Güvenlik için: Path traversal saldırılarını önlemek adına basename kullanıyoruz.
            base_name = os.path.basename(asset_file_name)
            destination_asset_path = os.path.join(site_folder, base_name)
            
            try:
                if os.path.exists(source_asset_path):
                    shutil.copy(source_asset_path, destination_asset_path)
                    logger.info(f"Copied asset {source_asset_path} to {destination_asset_path}")
                    copied_asset_paths.append(base_name) # Sadece dosya adını döndür (HTML'de kullanılacak)
                else:
                    logger.warning(f"Source asset {source_asset_path} not found. Cannot copy.")
            except Exception as e:
                logger.error(f"Error copying asset {source_asset_path} to {destination_asset_path}: {e}")
        return copied_asset_paths


    def create_website(self, site_topic, user_content_spec=None):
        logger.info(f"Creating new website: {site_topic}")
        site_folder_name = site_topic.lower().replace(' ', '_').replace('[^\w\s-]', '') # Basit normalleştirme
        site_folder_path = f"output/sites/{site_folder_name}"
        os.makedirs(site_folder_path, exist_ok=True)

        # 1. Design Agent: Temel HTML ve CSS yapısını oluşturur
        design_task = {"topic": site_topic}
        if user_content_spec and user_content_spec.get("theme"):
            design_task["theme"] = user_content_spec["theme"]
        
        design_agent = self.agents.get("Design Agent")
        if not design_agent:
            logger.error("Design Agent not found!")
            return
        design_result = design_agent.execute(design_task)
        logger.info("Design Agent completed.")

        # HTML ve CSS dosyalarını yaz
        index_html_path = os.path.join(site_folder_path, "index.html")
        style_css_path = os.path.join(site_folder_path, "style.css")
        with open(index_html_path, "w", encoding='utf-8') as f:
            f.write(design_result["html"])
        with open(style_css_path, "w", encoding='utf-8') as f:
            f.write(design_result["css"])

        # 2. Editor Agent: İçeriği üretir
        editor_agent = self.agents.get("Editor Agent")
        if not editor_agent:
            logger.error("Editor Agent not found!")
            return

        # EditorAgent'a hem site konusunu hem de kullanıcıdan gelen detaylı içeriği verelim
        content_task = {"topic": site_topic, "user_content": user_content_spec}
        processed_content = editor_agent.execute(content_task)
        logger.info("Editor Agent completed.")

        # 3. HTML'i BeautifulSoup ile güncelle (içerik, başlık vb.)
        try:
            with open(index_html_path, "r", encoding='utf-8') as f:
                html_doc = f.read()
            
            soup = BeautifulSoup(html_doc, 'html.parser')

            # Sayfa başlığını (<title>) güncelle
            if soup.title:
                soup.title.string = processed_content.get("page_title", site_topic)
            else:
                new_title_tag = soup.new_tag("title")
                new_title_tag.string = processed_content.get("page_title", site_topic)
                if soup.head:
                    soup.head.append(new_title_tag)


            # Ana başlığı (<h1>) güncelle
            h1_tag = soup.find('h1')
            if h1_tag:
                h1_tag.string = processed_content.get("main_heading", site_topic)
            
            # İçerik bölümlerini ekle
            content_section_tag = soup.find('section', id='content')
            if content_section_tag:
                content_section_tag.clear() # Mevcut placeholder içeriği temizle
                for section in processed_content.get("sections", []):
                    section_title_tag = soup.new_tag('h2')
                    section_title_tag.string = section.get("title", "Bölüm")
                    content_section_tag.append(section_title_tag)
                    
                    # HTML içeriğini doğrudan ekle (EditorAgent'tan geldiği için güvenli varsayılıyor)
                    # Gerçekte XSS önlemleri için sanitization gerekebilir.
                    section_content_div = soup.new_tag('div')
                    section_content_div.append(BeautifulSoup(section.get("content", ""), 'html.parser'))
                    content_section_tag.append(section_content_div)
            else:
                logger.warning("Could not find <section id='content'> in the HTML template.")

            # 4. Yerel "banner" görsellerini kopyala ve HTML'e ekle
            copied_banner_images = []
            if processed_content.get("banner_images"):
                copied_banner_images = self._copy_local_assets(processed_content["banner_images"], site_folder_path)

            banner_section_tag = soup.find('section', id='banner-image-section')
            if banner_section_tag:
                banner_section_tag.clear()
                for img_name in copied_banner_images:
                    img_tag = soup.new_tag('img', src=img_name, alt=f"{site_topic} görseli")
                    img_tag['style'] = "max-width: 600px; margin: 10px auto; display: block;"
                    banner_section_tag.append(img_tag)
            elif copied_banner_images: # Eğer banner bölümü yoksa ama resim varsa body'e ekle
                 logger.warning("Banner section not found, appending images to body.")
                 for img_name in copied_banner_images:
                    img_tag = soup.new_tag('img', src=img_name, alt=f"{site_topic} görseli")
                    img_tag['style'] = "max-width: 500px;"
                    if soup.body:
                        soup.body.append(img_tag)


            # 5. Dynamic Agent: JavaScript ekler
            dynamic_agent = self.agents.get("Dynamic Agent")
            if dynamic_agent:
                dynamic_result = dynamic_agent.execute({}) # Şu an için task almıyor
                logger.info("Dynamic Agent completed.")
                if dynamic_result.get("javascript"):
                    script_tag = soup.new_tag('script')
                    script_tag.string = dynamic_result["javascript"]
                    if soup.body: # body'nin sonuna ekle
                        soup.body.append(script_tag)
                    else: # body yoksa head'e ekle (ideal değil ama fallback)
                         if soup.head: soup.head.append(script_tag)
            else:
                logger.warning("Dynamic Agent not found.")

            # Güncellenmiş HTML'i dosyaya yaz
            with open(index_html_path, "w", encoding='utf-8') as f:
                f.write(str(soup))
            logger.info(f"HTML content updated and saved to {index_html_path}")

        except Exception as e:
            logger.error(f"Error during HTML content processing or file writing: {e}", exc_info=True)
            # Hata durumunda devam etmeyebiliriz.
            return

        # 6. Backend Agent (simülasyon)
        backend_agent = self.agents.get("Backend Agent")
        if backend_agent:
            backend_result = backend_agent.execute({}) # Task almıyor
            logger.info(f"Backend Agent completed: {backend_result['status']}")
        else:
            logger.warning("Backend Agent not found.")

        # 7. Reviewer Agent
        reviewer_agent = self.agents.get("Reviewer Agent")
        if reviewer_agent:
            review_result = reviewer_agent.execute({"site_folder": site_folder_path})
            logger.info(f"Reviewer Agent completed: {review_result}")
            if review_result.get("errors"):
                logger.warning(f"Reviewer Agent found errors: {review_result['errors']}. Server will still be started.")
                # Hata varsa sunucuyu başlatmama kararı verilebilir. Şimdilik devam ediyor.
        else:
            logger.warning("Reviewer Agent not found.")

        # 8. Server Agent: Siteyi sunar
        server_agent = self.agents.get("Server Agent") # Server agent genellikle tek bir instance olur.
                                                       # Eğer her site için ayrı server agent gerekiyorsa,
                                                       # main.py'de her create_website için yeni bir tane oluşturulmalı.
                                                       # Şu anki yapıda tek server_agent var, bu sorun olabilir.
                                                       # Çözüm: Her site için yeni bir ServerAgent instance'ı oluşturmak veya
                                                       # ServerAgent'ı birden fazla siteyi yönetebilecek şekilde tasarlamak.
                                                       # Şimdilik, var olanı kullanmaya çalışalım ama bu potansiyel bir sorundur.
                                                       # YA DA ServerAgent'ı her çağrıda yeni bir portta başlatacak şekilde ayarlamak.
                                                       # Basitlik adına, her site için ayrı bir ServerAgent instance'ı daha iyi olurdu.
                                                       # Bu düzeltme main.py tarafında yapılmalı.
                                                       # Şimdilik var olanı kullanıyoruz:

        if "Server Agent" not in self.agents:
             logger.error("Server Agent definition not found in manager.agents. Cannot start server.")
             return

        # Her site için farklı bir portta yeni bir sunucu başlatalım.
        # Basit port yönetimi:
        current_port = 8000 + len(self.running_servers) # Her yeni site için portu artır
        
        # Yeni bir ServerAgent instance'ı oluşturalım (eğer her site kendi sunucusunu alacaksa)
        # VEYA mevcut ServerAgent'ın portunu ve site klasörünü değiştirelim (bu thread-safe olmayabilir)
        # En temizi: Her site için yeni ServerAgent. Bu manager'ın server agent'ını kullanmak yerine
        # yeni bir tane oluşturup yönetmek anlamına gelir.
        # Şimdilik, Manager'daki tek ServerAgent'ın execute'unu çağırıyoruz, bu da onun iç portunu kullanır.
        # Bu, birden fazla site aynı anda çalıştırılırsa sorun yaratır.
        # Doğru yaklaşım: Her site için ayrı bir ServerAgent instance'ı.
        # Manager'ın içindeki self.agents["Server Agent"] genel bir şablon gibi düşünülmeli.
        
        # GEÇİCİ ÇÖZÜM: Her site için yeni bir ServerAgent oluşturalım (main.py'de tanımlanan genel yerine)
        # Bu, ManagerAgent'ın iç yapısını biraz değiştirir. Ya da ServerAgent.execute'u port alacak şekilde güncelleriz.
        # ServerAgent'ın portu __init__ ile ayarlanıyor. Bu yüzden her site için yeni instance en mantıklısı.
        
        # Eğer her site için ayrı bir sunucu isteniyorsa:
        temp_server_agent = ServerAgent(name=f"Server for {site_topic}", port=current_port) # Yeni instance, yeni port
        server_result = temp_server_agent.execute({"site_folder": site_folder_path})


        if server_result.get("success"):
            logger.info(f"Server for {site_topic} started. Website URL: {server_result['url']}")
            self.registered_sites[site_topic] = {
                "folder": site_folder_path, 
                "url": server_result['url'],
                "user_content_spec": user_content_spec, # Gelecekteki güncellemeler için sakla
                "server_agent_instance": temp_server_agent, # Sunucuyu durdurmak için
                "port": current_port
            }
            # self.running_servers[site_topic] = temp_server_agent # Bu satır üstteki server_agent_instance ile aynı
            
            # İçerik güncelleme planlaması (isteğe bağlı)
            # self.schedule_content_update(site_topic, schedule_type="daily", time_str="23:55")
        else:
            logger.error(f"Server Agent failed to start for {site_topic}: {server_result.get('message')}")

        # Saklanan orijinal kullanıcı içeriği
        self.registered_sites[site_topic]["user_content_spec"] = user_content_spec


    def _get_latest_user_content_for_update(self, site_topic):
        # Bu metod, bir güncelleme için en son kullanıcı tercihlerini/içeriklerini getirmelidir.
        # Bu, bir veritabanından, dosyadan veya başka bir kaynaktan gelebilir.
        # Şimdilik, ilk oluşturmadaki içeriği alıp basit bir değişiklik yapalım.
        original_spec = self.registered_sites.get(site_topic, {}).get("user_content_spec")
        if not original_spec:
            return {"title": "Güncellenmiş Web Sitesi (Varsayılan)", 
                    "sections": [{"title": "Varsayılan Güncelleme", "type": "text", "source":"local", "content": "Web sitesi içeriği otomatik olarak güncellendi."}]}

        updated_spec = original_spec.copy() # Derin kopya gerekebilir iç içe dict/list varsa
        updated_spec["title"] = original_spec.get("title", site_topic) + " - (Güncellendi)"
        
        # Örnek bir bölüm ekleyelim veya değiştirelim
        if "sections" not in updated_spec or not updated_spec["sections"]:
            updated_spec["sections"] = []
        
        updated_spec["sections"].insert(0, {
            "title": "Otomatik Güncelleme Notu", 
            "type": "text", 
            "source": "local", # Önemli: source belirtilmeli
            "content": f"Bu içerik {time.strftime('%Y-%m-%d %H:%M:%S')} tarihinde otomatik olarak güncellenmiştir. AI sistemimiz yeni bilgiler eklemiş olabilir."
        })
        # Mevcut bir bölümün içeriğini de değiştirebiliriz.
        # Örneğin, ilk bölümün sonuna bir not ekleyebiliriz.
        if len(updated_spec["sections"]) > 1 and updated_spec["sections"][1].get("type") == "text":
             current_content = updated_spec["sections"][1].get("content","")
             updated_spec["sections"][1]["content"] = current_content + "\n\n**Güncelleme:** Yeni bilgiler eklendi."


        logger.info(f"Generated updated content spec for {site_topic}")
        return updated_spec


    def update_website_content(self, site_topic):
        logger.info(f"Attempting to update content for {site_topic}...")
        if site_topic not in self.registered_sites:
            logger.error(f"Site {site_topic} not found in registered sites. Cannot update.")
            return

        site_info = self.registered_sites[site_topic]
        site_folder_path = site_info["folder"]
        index_html_path = os.path.join(site_folder_path, "index.html")

        # 1. Güncel içerik speklerini al (veya oluştur)
        latest_user_content_spec = self._get_latest_user_content_for_update(site_topic)

        # 2. Editor Agent ile yeni içeriği işle
        editor_agent = self.agents.get("Editor Agent")
        if not editor_agent:
            logger.error("Editor Agent not found! Cannot update content.")
            return
        
        content_task = {"topic": site_topic, "user_content": latest_user_content_spec}
        processed_content = editor_agent.execute(content_task)
        logger.info(f"Editor Agent completed content update processing for {site_topic}.")

        # 3. HTML'i BeautifulSoup ile güncelle
        try:
            with open(index_html_path, "r", encoding='utf-8') as f:
                html_doc = f.read()
            
            soup = BeautifulSoup(html_doc, 'html.parser')

            if soup.title:
                soup.title.string = processed_content.get("page_title", site_topic + " - Güncel")
            
            h1_tag = soup.find('h1')
            if h1_tag:
                h1_tag.string = processed_content.get("main_heading", site_topic + " - Güncel")
            
            content_section_tag = soup.find('section', id='content')
            if content_section_tag:
                content_section_tag.clear() 
                for section in processed_content.get("sections", []):
                    section_title_tag = soup.new_tag('h2')
                    section_title_tag.string = section.get("title", "Bölüm")
                    content_section_tag.append(section_title_tag)
                    
                    section_content_div = soup.new_tag('div')
                    section_content_div.append(BeautifulSoup(section.get("content", ""), 'html.parser'))
                    content_section_tag.append(section_content_div)
            
            # Banner görsellerini de güncelleyebiliriz (eğer yeni görseller varsa)
            # Bu örnekte banner görselleri ilk oluşturmadaki gibi kalıyor.
            # İstenirse _get_latest_user_content_for_update banner_images'ı da güncelleyebilir.

            with open(index_html_path, "w", encoding='utf-8') as f:
                f.write(str(soup))
            logger.info(f"Content updated successfully for {site_topic} in {index_html_path}.")

        except FileNotFoundError:
            logger.error(f"Error: index.html not found for {site_topic} at {index_html_path} during update.")
        except Exception as e:
            logger.error(f"Error updating content for {site_topic}: {e}", exc_info=True)


    def schedule_content_update(self, site_topic, schedule_type="daily", time_str="21:00"):
        if site_topic not in self.registered_sites:
            logger.warning(f"Cannot schedule update for {site_topic}, not a registered site.")
            return

        job_function = lambda: self.update_website_content(site_topic=site_topic)
        
        if schedule_type == "daily":
            schedule.every().day.at(time_str).do(job_function).tag(site_topic, 'content-update')
            logger.info(f"Content update for {site_topic} scheduled daily at {time_str}.")
        elif schedule_type == "weekly":
            # Örnek: Her Pazartesi belirli bir saatte
            schedule.every().monday.at(time_str).do(job_function).tag(site_topic, 'content-update')
            logger.info(f"Content update for {site_topic} scheduled weekly (Mondays at {time_str}).")
        elif schedule_type == "every_x_minutes": # Test için
            try:
                minutes = int(time_str) # time_str burada dakika sayısı olmalı
                schedule.every(minutes).minutes.do(job_function).tag(site_topic, 'content-update')
                logger.info(f"Content update for {site_topic} scheduled every {minutes} minutes.")
            except ValueError:
                 logger.error(f"Invalid time_str '{time_str}' for 'every_x_minutes'. Must be an integer.")
                 return
        else:
            logger.warning(f"Unsupported schedule type: {schedule_type}")
            return

        if not self.scheduler_thread or not self.scheduler_thread.is_alive():
            self.start_scheduler()

    def start_scheduler(self):
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            logger.info("Scheduler is already running.")
            return
            
        self.should_run_scheduler = True
        self.scheduler_thread = Thread(target=self._run_scheduler_loop, name="SchedulerThread")
        self.scheduler_thread.daemon = True # Ana program sonlandığında thread de sonlansın
        self.scheduler_thread.start()
        logger.info("Scheduler started.")

    def _run_scheduler_loop(self):
        logger.info("Scheduler loop started.")
        while self.should_run_scheduler:
            schedule.run_pending()
            time.sleep(1) # 1 saniyede bir kontrol et
        logger.info("Scheduler loop stopped.")

    def stop_scheduler(self):
        logger.info("Attempting to stop scheduler...")
        self.should_run_scheduler = False
        # Tüm planlanmış görevleri iptal et (isteğe bağlı, tag kullanarak)
        # schedule.clear('content-update') # Sadece bu uygulamaya ait görevleri temizle
        # schedule.clear() # Tüm görevleri temizler
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            try:
                self.scheduler_thread.join(timeout=5) # Thread'in bitmesini bekle (max 5sn)
                if self.scheduler_thread.is_alive():
                    logger.warning("Scheduler thread did not stop in time.")
            except Exception as e:
                logger.error(f"Error stopping scheduler thread: {e}")
        self.scheduler_thread = None
        logger.info("Scheduler stopped.")

    def stop_website(self, site_topic):
        logger.info(f"Attempting to stop website server for {site_topic}...")
        if site_topic in self.registered_sites:
            server_agent_instance = self.registered_sites[site_topic].get("server_agent_instance")
            if server_agent_instance:
                server_agent_instance.stop_server() # Bu metod ServerAgent'ta olmalı
                logger.info(f"Server for {site_topic} stopped.")
            else:
                logger.warning(f"No server agent instance found for {site_topic} to stop.")
            
            # İsteğe bağlı: Kayıtlı sitelerden de kaldırabiliriz veya sadece sunucuyu durdurabiliriz.
            # del self.registered_sites[site_topic] # Eğer tamamen kaldırılacaksa
        else:
            logger.warning(f"No running server found for {site_topic} in registered sites.")

    def execute(self, task=None): # BaseAgent ile uyumlu hale getirildi
        # ManagerAgent'ın ana execute'u genellikle site oluşturma veya yönetme komutlarını alır.
        # Örnek: task = {"action": "create_site", "topic": "...", "user_content": {...}}
        #         task = {"action": "stop_site", "topic": "..."}
        # Şimdilik main.py doğrudan create_website çağırıyor.
        super().execute(task) 
        if task:
            action = task.get("action")
            if action == "create_site":
                self.create_website(task.get("topic"), task.get("user_content"))
            elif action == "update_site":
                self.update_website_content(task.get("topic"))
            elif action == "stop_site":
                self.stop_website(task.get("topic"))
            # ... diğer eylemler