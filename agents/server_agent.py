# agents/server_agent.py
from agents.base_agent import BaseAgent
import http.server
import socketserver
import os
import threading
import logging

logger = logging.getLogger(__name__)

class SimpleWebServerFactory:
    """
    Handler oluşturmak için bir factory. Bu, her istek için site_folder'ı doğru ayarlamamızı sağlar.
    SimpleHTTPRequestHandler çalışma dizinini (CWD) kullandığı için,
    her sunucu thread'inin kendi CWD'sini ayarlaması önemlidir.
    """
    def __init__(self, directory):
        self.directory = directory

    def get_handler(self, *args, **kwargs):
        # Her handler instance'ı için doğru dizini ayarlayan bir closure döndür
        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            # Bu sınıfın __init__ metodu, dış scope'taki 'self.directory'yi kullanacak.
            # SimpleHTTPRequestHandler'ın kendisi zaten bu şekilde çalışır,
            # __init__ içinde os.chdir(directory) yapar eğer directory parametresi verilirse.
            # Ancak, biz thread başına CWD değiştirmeyi tercih ediyoruz.
            def __init__(self, *args, **kwargs):
                # SimpleHTTPRequestHandler Python 3.7+ 'directory' argümanını destekler.
                # Bu, os.chdir'a göre daha temizdir.
                super().__init__(*args, directory=self.outer_self.directory, **kwargs)
            
            # Yönlendirmeyi de burada yapalım, eğer path "/" ise index.html'e yönlendirsin.
            # Aslında SimpleHTTPRequestHandler bunu zaten yapıyor, directory verildiğinde.
            # def do_GET(self):
            #     if self.path == '/':
            #         self.path = '/index.html' # directory ile kullanıldığında /index.html olmalı
            #     super().do_GET()


        # CustomHandler'a dış SimpleWebServerFactory instance'ını (self) verelim
        CustomHandler.outer_self = self
        return CustomHandler


class ServerAgent(BaseAgent):
    def __init__(self, name="Server Agent", port=8000):
        super().__init__(name)
        self.port = port
        self.httpd_server = None # httpd ismini değiştirdim karışmasın diye
        self.server_thread = None
        self._original_cwd = os.getcwd() # Orijinal CWD'yi sakla (stop_server'da geri dönmek için)
        self.site_folder_to_serve = None # Hangi klasörün sunulduğunu belirtmek için

    def _start_server_thread_target(self, site_folder_abs_path, port):
        """Bu metod yeni thread'de çalışacak."""
        logger.info(f"{self.name} (Port {port}): Server thread started for {site_folder_abs_path}.")
        
        # Python 3.7+ SimpleHTTPRequestHandler 'directory' argümanını destekler.
        # Bu, os.chdir'dan daha temiz bir yoldur.
        # HandlerClass = http.server.SimpleHTTPRequestHandler
        # with socketserver.TCPServer(("", port), lambda *args, **kwargs: HandlerClass(*args, directory=site_folder_abs_path, **kwargs)) as self.httpd_server:
        
        # Daha da iyisi, her istek için doğru dizinin ayarlandığından emin olmak için bir factory kullanmak
        # veya SimpleHTTPRequestHandler'ı alt sınıf olarak alıp translate_path'i override etmek.
        # Şimdilik, SimpleHTTPRequestHandler'ın directory argümanını kullanalım.

        # Python 3.6 ve altı için os.chdir gerekebilir.
        # current_thread_cwd = os.getcwd()
        # os.chdir(site_folder_abs_path)
        # logger.info(f"{self.name} (Port {port}): CWD changed to {os.getcwd()} for serving.")

        handler_factory = SimpleWebServerFactory(site_folder_abs_path)

        try:
            # TCPServer'a handler factory'den handler'ı almasını söyleyelim
            with socketserver.TCPServer(("", port), handler_factory.get_handler) as self.httpd_server:
                self.site_folder_to_serve = site_folder_abs_path # Hangi klasörün sunulduğunu kaydet
                logger.info(f"{self.name}: Serving HTTP on port {port} from directory {site_folder_abs_path}...")
                self.httpd_server.serve_forever()
        except OSError as e: # Port zaten kullanılıyorsa
            logger.error(f"{self.name} (Port {port}): Could not start server. Port might be in use. Error: {e}")
            self.httpd_server = None # Sunucu başlatılamadı
        except Exception as e:
            logger.error(f"{self.name} (Port {port}): Server loop encountered an error: {e}", exc_info=True)
            self.httpd_server = None
        finally:
            # Python 3.6 ve altı için CWD'yi geri al
            # os.chdir(current_thread_cwd)
            # logger.info(f"{self.name} (Port {port}): CWD restored to {current_thread_cwd}.")
            if self.httpd_server is None: # Eğer sunucu hata ile sonlandıysa
                 logger.info(f"{self.name} (Port {port}): Server on port {port} has shut down (possibly due to an error).")
            else: # Normal shutdown ile sonlandıysa
                 logger.info(f"{self.name} (Port {port}): Server on port {port} has shut down.")


    def execute(self, task): # task'tan site_folder ve isteğe bağlı port alabilir
        requested_site_folder = task.get("site_folder")
        # Bu ServerAgent instance'ı için port __init__ ile ayarlandı.
        # Eğer task içinde port gelirse onu kullanabiliriz, ama bu instance'ın portunu değiştirir.
        # Bu nedenle, port genellikle __init__ ile sabitlenir. ManagerAgent her site için yeni ServerAgent oluşturmalı.
        
        if not requested_site_folder:
            logger.error(f"{self.name}: Site folder not provided in task.")
            return {"success": False, "message": "Site folder not provided."}

        site_folder_abs_path = os.path.abspath(requested_site_folder)

        if not os.path.isdir(site_folder_abs_path):
            logger.error(f"{self.name}: Site folder '{site_folder_abs_path}' not found or not a directory.")
            return {"success": False, "message": f"Site folder '{site_folder_abs_path}' not found."}

        if self.server_thread and self.server_thread.is_alive():
            logger.warning(f"{self.name}: Server on port {self.port} is already running for {self.site_folder_to_serve}. Cannot start a new one with the same agent instance unless stopped first.")
            # İsteğe bağlı olarak eski sunucuyu durdurup yenisini başlatabiliriz.
            # self.stop_server()
            return {"success": False, "message": f"Server already running on port {self.port}."}


        # Sunucuyu ayrı bir thread'de başlat
        self.server_thread = threading.Thread(
            target=self._start_server_thread_target, 
            args=(site_folder_abs_path, self.port),
            name=f"ServerThread-Port{self.port}"
        )
        self.server_thread.daemon = True  # Ana thread kapandığında bu thread de otomatik kapansın
        self.server_thread.start()

        # Sunucunun başlaması için kısa bir bekleme (isteğe bağlı, race condition önlemek için)
        #time.sleep(0.5) 

        if self.httpd_server: # Eğer _start_server_thread_target içinde sunucu başarıyla başlatıldıysa
            logger.info(f"{self.name}: Web server started successfully on port {self.port} for {site_folder_abs_path}.")
            return {"success": True, "url": f"http://localhost:{self.port}"}
        else:
            logger.error(f"{self.name}: Web server failed to start on port {self.port} for {site_folder_abs_path}.")
            # Thread join edilebilir ama daemon olduğu için ana program çıkınca zaten sonlanacak.
            if self.server_thread.is_alive():
                 self.server_thread.join(timeout=1) # Hata durumunda thread'in kapanmasını bekle
            return {"success": False, "message": "Server failed to start (check logs for details, port might be in use)."}


    def stop_server(self):
        logger.info(f"{self.name}: Attempting to stop the server on port {self.port}...")
        if self.httpd_server:
            try:
                self.httpd_server.shutdown() # Sunucuyu düzgünce kapat
                self.httpd_server.server_close() # Soketi kapat
                logger.info(f"{self.name}: Server shutdown initiated on port {self.port}.")
            except Exception as e:
                logger.error(f"{self.name}: Error during server shutdown on port {self.port}: {e}", exc_info=True)
            self.httpd_server = None
        else:
            logger.info(f"{self.name}: Server on port {self.port} was not running or already stopped.")

        if self.server_thread and self.server_thread.is_alive():
            try:
                self.server_thread.join(timeout=2) # Thread'in bitmesini bekle (max 2sn)
                if self.server_thread.is_alive():
                    logger.warning(f"{self.name}: Server thread on port {self.port} did not stop in time.")
                else:
                    logger.info(f"{self.name}: Server thread on port {self.port} joined successfully.")
            except Exception as e:
                logger.error(f"{self.name}: Error joining server thread on port {self.port}: {e}")
        
        self.server_thread = None
        self.site_folder_to_serve = None # Hangi klasörün sunulduğu bilgisini temizle
        
        # Orijinal CWD'ye geri dön (eğer global CWD değiştirildiyse - şu anki yapıda gerek yok)
        # if os.getcwd() != self._original_cwd:
        #    logger.info(f"{self.name}: Restoring CWD to {self._original_cwd}")
        #    os.chdir(self._original_cwd)
        logger.info(f"{self.name}: Server stop process completed for port {self.port}.")