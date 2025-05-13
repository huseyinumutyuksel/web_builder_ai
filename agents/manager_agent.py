# agents/manager_agent.py

from agents.base_agent import BaseAgent
from agents.design_agent import DesignAgent
from agents.dynamic_agent import DynamicAgent
from agents.backend_agent import BackendAgent
from agents.editor_agent import EditorAgent
from agents.reviewer_agent import ReviewerAgent
from agents.server_agent import ServerAgent
import os
import schedule
import time
from threading import Thread

class ManagerAgent(BaseAgent):
    def __init__(self, name="Manager Agent"):
        super().__init__(name)
        self.agents = {}
        self.registered_sites = {}
        self.running_servers = {}
        self.scheduler_thread = None
        self.should_run = True

    def add_agent(self, agent):
        self.agents[agent.name] = agent
        print(f"{agent.name} added to the system.")

    def create_website(self, site_topic, user_content=None):
        print(f"\nCreating new website: {site_topic}")
        site_folder = f"output/sites/{site_topic.lower().replace(' ', '_')}"
        os.makedirs(site_folder, exist_ok=True)

        # Design Agent
        design_task = {"topic": site_topic}
        if user_content and user_content.get("theme"):
            design_task["theme"] = user_content["theme"]
        design_result = self.agents["Design Agent"].execute(design_task)
        print(f"Design Agent completed.")
        with open(os.path.join(site_folder, "index.html"), "w", encoding='utf-8') as f:
            f.write(design_result["html"])
        with open(os.path.join(site_folder, "style.css"), "w", encoding='utf-8') as f:
            f.write(design_result["css"])

        # Editor Agent
        content_task = {"topic": site_topic, "user_content": user_content}
        content_result = self.agents["Editor Agent"].execute(content_task)
        print(f"Editor Agent completed.")

        # Update index.html with content
        with open(os.path.join(site_folder, "index.html"), "r", encoding='utf-8') as f:
            html_content = f.read()

        html_content = html_content.replace("<title>General Website</title>", f"<title>{content_result['title']}</title>")
        html_content = html_content.replace("<h1>General Website</h1>", f"<h1>{content_result['title']}</h1>")

        main_content = ""
        for section in content_result.get("sections", []):
            main_content += f"<h2>{section['title']}</h2>{section['content']}"
        html_content = html_content.replace('<section id="content"><p>Bu, general website hakkında genel bir içerik alanıdır.</p></section>', f'<section id="content">{main_content}</section>')

        if content_result.get("images"):
            print(f"Görsel bağlantıları: {content_result['images']}")
            html_content += f'<img src="{content_result["images"][0]}" alt="{site_topic} görseli" style="max-width: 500px;">'
        # Dynamic Agent
        dynamic_result = self.agents["Dynamic Agent"].execute({})
        print(f"Dynamic Agent completed.")
        if dynamic_result.get("javascript"):
            html_content = html_content.replace('</body>', f'<script>{dynamic_result["javascript"]}</script></body>')

        with open(os.path.join(site_folder, "index.html"), "w", encoding='utf-8') as f:
            f.write(html_content)

        # Backend Agent
        backend_result = self.agents["Backend Agent"].execute({})
        print(f"Backend Agent completed: {backend_result['status']}")

        # Reviewer Agent
        review_result = self.agents["Reviewer Agent"].execute({"site_folder": site_folder})
        print(f"Reviewer Agent completed: {review_result}")
        if review_result["errors"]:
            print("Reviewer Agent found errors. Further action may be needed.")
            return # Hata varsa sunucuyu başlatmayalım şimdilik

        # Server Agent
        server_result = self.agents["Server Agent"].execute({"site_folder": site_folder})
        if server_result["success"]:
            print(f"Server Agent started. Website URL: {server_result['url']}")
            self.registered_sites[site_topic] = {"folder": site_folder, "url": server_result["url"]}
            self.running_servers[site_topic] = self.agents["Server Agent"] # Sunucuyu durdurmak için referans saklayalım
            self.schedule_content_update(site_topic, schedule_type="daily", time_str="21:00") # İlk oluşturmada güncellemeyi planla
        else:
            print(f"Server Agent failed to start: {server_result['message']}")

    def _get_latest_user_content(self, site_topic):
        # Burada siteye özel en güncel kullanıcı içeriğini döndürme mantığı olabilir.
        # Şimdilik ilk oluşturmadaki içeriği döndürüyoruz.
        for topic, data in self.registered_sites.items():
            if topic == site_topic:
                # Şu anda sadece 'title', 'theme', 'sections', 'images', 'videos' içeriyor
                # İleride daha dinamik bir yapı olabilir.
                return {"title": topic.replace("_", " ").title() + " - Updated",
                        "sections": [{"title": "Güncellenmiş İçerik", "type": "text", "content": f"{topic} için içerik otomatik olarak güncellendi."},
                                     {"title": "Yeni Bir Liste", "type": "list", "items": ["Öğe 1", "Öğe 2", "Öğe 3"]}],
                        "images": self.registered_sites[topic].get("images", []),
                        "videos": self.registered_sites[topic].get("videos", [])}
        return {"title": "Güncellenmiş Web Sitesi", "sections": [{"title": "Varsayılan Güncelleme", "type": "text", "content": "Web sitesi içeriği güncellendi."}]}


    def update_website_content(self, site_topic):
        print(f"Updating content for {site_topic}...")
        if site_topic in self.registered_sites:
            site_folder = self.registered_sites[site_topic]["folder"]
            content_task = {"topic": site_topic, "user_content": self._get_latest_user_content(site_topic)}
            content_result = self.agents["Editor Agent"].execute(content_task)
            print(f"Content Agent completed update.")

            # Update index.html with new content
            try:
                with open(os.path.join(site_folder, "index.html"), "r", encoding='utf-8') as f:
                    html_content = f.read()

                html_content = html_content.replace("<title>.*?</title>", f"<title>{content_result['title']}</title>")
                html_content = html_content.replace("<h1>.*?</h1>", f"<h1>{content_result['title']}</h1>")

                # İçerik bölümlerini güncelleme (basit bir yaklaşımla)
                content_placeholder = '<section id="content">.*?</section>'
                new_content = '<section id="content">'
                for section in content_result.get("sections", []):
                    new_content += f"<h2>{section['title']}</h2>{section['content']}"
                new_content += '</section>'
                import re
                html_content = re.sub(content_placeholder, new_content, html_content, 1)

                # Görseli de güncelleyebiliriz (şimdilik sadece ilk görseli değiştiriyoruz)
                if content_result.get("images"):
                    img_pattern = r'<img src=".*?" alt=".*?" style="max-width: 500px;">'
                    new_img_tag = f'<img src="{content_result["images"][0]}" alt="{site_topic} görseli" style="max-width: 500px;">'
                    html_content = re.sub(img_pattern, new_img_tag, html_content)


                with open(os.path.join(site_folder, "index.html"), "w", encoding='utf-8') as f:
                    f.write(html_content)
                print(f"Content updated for {site_topic}.")
            except FileNotFoundError:
                print(f"Error: index.html not found for {site_topic}.")
            except Exception as e:
                print(f"Error updating content for {site_topic}: {e}")
        else:
            print(f"Site {site_topic} not found in registered sites.")

    def schedule_content_update(self, site_topic, schedule_type="daily", time_str="21:00"):
        if schedule_type == "daily":
            schedule.every().day.at(time_str).do(self.update_website_content, site_topic=site_topic)
            print(f"Content update for {site_topic} scheduled daily at {time_str}.")
        elif schedule_type == "weekly":
            schedule.every().monday.at(time_str).do(self.update_website_content, site_topic=site_topic) # Örn: Her Pazartesi
            print(f"Content update for {site_topic} scheduled weekly (Mondays) at {time_str}.")
        # İstenirse aylık ve yıllık seçenekler de eklenebilir

        if not self.scheduler_thread:
            self.start_scheduler()

    def start_scheduler(self):
        if not self.scheduler_thread:
            self.scheduler_thread = Thread(target=self._run_scheduler)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            print("Scheduler started.")

    def _run_scheduler(self):
        while self.should_run:
            schedule.run_pending()
            time.sleep(1)

    def stop_scheduler(self):
        self.should_run = False
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join()
            self.scheduler_thread = None
            print("Scheduler stopped.")

    def stop_website(self, site_topic):
        if site_topic in self.running_servers:
            self.running_servers[site_topic].stop_server()
            del self.running_servers[site_topic]
            print(f"Server for {site_topic} stopped.")
        else:
            print(f"No running server found for {site_topic}.")