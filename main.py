# main.py

from agents.manager_agent import ManagerAgent
from agents.design_agent import DesignAgent
from agents.dynamic_agent import DynamicAgent
from agents.backend_agent import BackendAgent
from agents.editor_agent import EditorAgent
from agents.reviewer_agent import ReviewerAgent
from agents.server_agent import ServerAgent
from agents.helper_agents.image_generator_agent import ImageGeneratorAgent
from agents.helper_agents.video_generator_agent import VideoGeneratorAgent
import time

if __name__ == "__main__":
    manager = ManagerAgent()

    designer = DesignAgent()
    dynamic_coder = DynamicAgent()
    backend_developer = BackendAgent()
    content_editor = EditorAgent()
    site_reviewer = ReviewerAgent()
    server_deployer = ServerAgent()
    image_generator = ImageGeneratorAgent()
    video_generator = VideoGeneratorAgent()

    manager.add_agent(designer)
    manager.add_agent(dynamic_coder)
    manager.add_agent(backend_developer)
    manager.add_agent(content_editor)
    manager.add_agent(site_reviewer)
    manager.add_agent(server_deployer)
    manager.add_agent(image_generator)
    manager.add_agent(video_generator)

    site_topic = "AI Powered Web Development Solutions"
    user_content = {
        "title": "AI-Powered Web Development Solutions",
        "theme": "futuristic",
        "sections": [
            {"title": "Giriş", "type": "text", "source": "local", "content": "Yapay zekanın modern web geliştirmedeki dönüştürücü gücünü keşfedin."},
            {"title": "AI Hakkında (Wikipedia'dan)", "type": "text", "source": "web_scrape", "url": "https://tr.wikipedia.org/wiki/Yapay_zeka", "selector": "p"},
            {"title": "AI ile İçerik Oluşturma", "type": "list", "items": ["Metin oluşturma", "Görsel seçimi", "Video önerileri"]},
            {"title": "AI Ajanlarımız", "type": "images", "count": 2},
            {"title": "İletişim Formu", "type": "form"}
        ],
        "images": ["ai_web_dev_concept.jpg"],
        "videos": []
    }
    manager.create_website(site_topic, user_content)

    # Sunucunun başlaması için biraz bekleyelim
    time.sleep(2)

    # Zamanlayıcının çalışması için ana thread'i açık tutalım (Ctrl+C ile sonlandırılabilir)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
        manager.stop_scheduler()
        if site_topic in manager.running_servers:
            manager.stop_website(site_topic)