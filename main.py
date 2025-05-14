# main.py

from agents.manager_agent import ManagerAgent
from agents.design_agent import DesignAgent
from agents.dynamic_agent import DynamicAgent
from agents.backend_agent import BackendAgent
from agents.editor_agent import EditorAgent
from agents.reviewer_agent import ReviewerAgent
from agents.server_agent import ServerAgent # Bu genel ServerAgent tanımı olacak


from dotenv import load_dotenv
load_dotenv()

# helper_agents'ın agents klasörü altında olduğunu varsayıyoruz.
# Eğer değilse, bu yolları kendi dosya yapınıza göre güncelleyin.
# Örn: Proje ana dizinindeyse: from image_generator_agent import ImageGeneratorAgent
try:
    from agents.helper_agents.image_generator_agent import ImageGeneratorAgent
    from agents.helper_agents.video_generator_agent import VideoGeneratorAgent
except ImportError:
    print("Warning: Could not import helper agents. Ensure they are in 'agents/helper_agents/' or adjust import paths.")
    # Fallback to dummy classes if not found, so the program can run partially
    class ImageGeneratorAgent: __init__=lambda s,n="DummyIGA":None; execute=lambda s,t=None:[]
    class VideoGeneratorAgent: __init__=lambda s,n="DummyVGA":None; execute=lambda s,t=None:[]


import time
import logging
import os

# Logging ayarları
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s',
                    handlers=[logging.StreamHandler()]) # Konsola log basar

# output klasörlerini oluştur
os.makedirs("output/sites", exist_ok=True)
os.makedirs("output/generated_images", exist_ok=True)
os.makedirs("output/generated_videos", exist_ok=True)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.info("Application starting...")

    manager = ManagerAgent()

    # Ajanları Manager'a ekle
    # Bu ajanlar, Manager tarafından gerektiğinde kullanılacak şablonlar/tanımlar gibidir.
    manager.add_agent(DesignAgent())
    manager.add_agent(DynamicAgent())
    manager.add_agent(BackendAgent())
    manager.add_agent(EditorAgent())
    manager.add_agent(ReviewerAgent())
    # manager.add_agent(ServerAgent()) # ServerAgent artık ManagerAgent içinde dinamik olarak yönetilecek
                                       # (her site için ayrı instance ve port)
                                       # Bu satırı kaldırmak daha doğru olur. Ya da manager bunu kullanmaz.
                                       # ManagerAgent.create_website içinde ServerAgent() doğrudan çağrılıyor.

    manager.add_agent(ImageGeneratorAgent()) # Bu yardımcı ajanlar EditorAgent tarafından kullanılabilir.
    manager.add_agent(VideoGeneratorAgent())


    # --- Web Sitesi 1 Oluşturma ---
    site_topic_1 = "AI Powered Web Development Solutions"
    # Bu görselin `main.py` ile aynı dizinde veya erişilebilir bir yolda olması beklenir.
    # Projenizin kök dizinine "ai_web_dev_concept.jpg" adında bir örnek görsel ekleyin.
    # Yoksa, ManagerAgent uyarı verecek ve görseli kopyalayamayacaktır.
    # Örnek bir placeholder görsel dosyası oluşturabilirsiniz:
    if not os.path.exists("ai_web_dev_concept.jpg"):
        try:
            with open("ai_web_dev_concept.jpg", "w") as f: f.write("This is a placeholder image.")
            logger.info("Created a placeholder 'ai_web_dev_concept.jpg'. Replace with a real image.")
        except IOError:
             logger.error("Could not create placeholder 'ai_web_dev_concept.jpg'.")


    user_content_spec_1 = {
        "title": "Yapay Zeka Destekli Web Geliştirme Çözümleri", # Sayfa <title> ve ana başlık için
        "main_heading": "AI ile Geleceğin Web Sitelerini İnşa Edin", # H1 için özel başlık
        "theme": "futuristic", # DesignAgent bunu ileride kullanabilir
        "banner_images": ["ai_web_dev_concept.jpg"], # Site geneli ana görseller (ManagerAgent kopyalar)
        "sections": [
            {"title": "Giriş: Yapay Zekanın Rolü", 
             "type": "text", 
             "source": "local", # "local" kaynak türü
             "content": "Yapay zeka (AI), web geliştirme süreçlerini kökten değiştiren devrim niteliğinde bir teknolojidir. Akıllı otomasyon, kişiselleştirilmiş kullanıcı deneyimleri ve veri odaklı tasarımlar sunarak, AI projelerin daha hızlı, daha verimli ve daha etkili bir şekilde hayata geçirilmesini sağlar."},
            {"title": "AI Destekli Geliştirmenin Avantajları", 
             "type": "list", 
             "items": [
                 "Gelişmiş Kullanıcı Deneyimi (UX) için Kişiselleştirme", 
                 "Otomatik Kod Üretimi ve Test Süreçleri", 
                 "Veri Analizi ile İçerik Optimizasyonu", 
                 "Akıllı Chatbotlar ve Sanal Asistanlar",
                 "Gelişmiş Güvenlik Protokolleri"
             ]},
            {"title": "AI Hakkında Daha Fazla Bilgi (Wikipedia'dan)", 
             "type": "text", 
             "source": "web_scrape", # "web_scrape" kaynak türü
             "url": "https://tr.wikipedia.org/wiki/Yapay_zeka", 
             "selector": "p"}, # Sadece <p> etiketlerini al
            {"title": "Örnek AI Projelerimizden Görseller", 
             "type": "images", # Bu bölüm için özel görseller (EditorAgent bulur/oluşturur)
             "count": 2,
             "image_topic": "artificial intelligence in web design" # EditorAgent bu konuyu kullanır
            }, 
            {"title": "Bizimle İletişime Geçin", "type": "form"}
        ],
        "videos": [] # Henüz kullanılmıyor
    }
    manager.create_website(site_topic_1, user_content_spec_1)

    # --- Web Sitesi 2 Oluşturma (Farklı portta) ---
    site_topic_2 = "Sustainable Energy Solutions"
    user_content_spec_2 = {
        "title": "Sürdürülebilir Enerji Çözümleri",
        "main_heading": "Yeşil Bir Gelecek İçin Enerji",
        "banner_images": [], # Bu site için banner görseli yok
        "sections": [
            {"title": "Sürdürülebilir Enerji Nedir?", "type": "text", "source": "local", "content": "Sürdürülebilir enerji, gelecek nesillerin kendi ihtiyaçlarını karşılama yeteneğinden ödün vermeden bugünün ihtiyaçlarını karşılayan enerji üretimi ve kullanımıdır."},
            {"title": "Yenilenebilir Enerji Kaynakları", "type": "list", "items": ["Güneş Enerjisi", "Rüzgar Enerjisi", "Hidroelektrik Enerji", "Jeotermal Enerji", "Biyokütle Enerjisi"]},
            {"title": "Enerji Verimliliği İpuçları", "type": "text", "source": "local", "content": "Evde ve işyerinde enerji tasarrufu yaparak hem çevreyi koruyabilir hem de faturalarınızı azaltabilirsiniz. LED ampuller kullanın, cihazları fişten çekin, yalıtıma önem verin."}
        ]
    }
    # manager.create_website(site_topic_2, user_content_spec_2) # İkinci siteyi de oluşturmak için yorumu kaldırın


    # Zamanlayıcıyı başlat (periyodik içerik güncellemeleri için)
    # manager.start_scheduler() # Eğer zamanlanmış görevler varsa (örn: schedule_content_update çağrıldıysa)

    # Örnek zamanlanmış görev (test için her 1 dakikada bir site_topic_1'i güncelle)
    # manager.schedule_content_update(site_topic_1, schedule_type="every_x_minutes", time_str="1")


    # Sunucuların ve zamanlayıcının çalışması için ana thread'i açık tutalım
    logger.info("Application setup complete. Servers are running if started.")
    logger.info("Use Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1) # Ana thread'i meşgul etmeden çalışır durumda tutar
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Shutting down...")
    finally:
        logger.info("Performing cleanup...")
        manager.stop_scheduler() # Önce zamanlayıcıyı durdur
        
        # Tüm çalışan sunucuları durdur
        # registered_sites bir dictionary olduğu için .keys() kopyasını alarak iterate etmek daha güvenli olabilir
        # eğer stop_website metodu bu dictionary'yi değiştiriyorsa.
        # Ancak şu anki stop_website sadece ServerAgent'ı durduruyor, dict'ten silmiyor.
        # Yine de kopyasını almak iyi bir pratiktir:
        active_sites = list(manager.registered_sites.keys()) 
        for site_topic in active_sites:
            logger.info(f"Stopping server for site: {site_topic}")
            manager.stop_website(site_topic)
        
        logger.info("Application shut down gracefully.")