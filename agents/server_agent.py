import os
import threading
import logging
import http.server
import socketserver
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class SimpleWebServerFactory:
    def __init__(self, directory):
        self.directory = directory

    def get_handler(self, *args, **kwargs):
        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=self.outer_self.directory, **kwargs)
        CustomHandler.outer_self = self
        return CustomHandler

class ServerAgent(BaseAgent):
    def __init__(self, name="Server Agent", port=8000):
        super().__init__(name)
        self.port = port
        self.httpd_server = None
        self.server_thread = None
        self.site_folder_to_serve = None

    def _start_server(self, site_folder, port):
        handler_factory = SimpleWebServerFactory(site_folder)
        try:
            with socketserver.TCPServer(("", port), handler_factory.get_handler) as httpd:
                self.httpd_server = httpd
                self.site_folder_to_serve = site_folder
                logger.info(f"{self.name}: Serving on port {port} from {site_folder}")
                httpd.serve_forever()
        except OSError as e:
            logger.error(f"{self.name}: Port {port} in use: {e}")
            self.httpd_server = None
        except Exception as e:
            logger.error(f"{self.name}: Server error: {e}", exc_info=True)

    def execute(self, task):
        site_folder = task.get("site_folder")
        if not site_folder or not os.path.isdir(site_folder):
            logger.error(f"{self.name}: Invalid site folder: {site_folder}")
            return {"success": False, "message": "Invalid site folder"}

        if self.server_thread and self.server_thread.is_alive():
            return {"success": False, "message": f"Server already running on port {self.port}"}

        self.server_thread = threading.Thread(
            target=self._start_server,
            args=(site_folder, self.port),
            name=f"ServerThread-Port{self.port}",
            daemon=True
        )
        self.server_thread.start()
        return {"success": True, "url": f"http://localhost:{self.port}"}

    def stop_server(self):
        if self.httpd_server:
            self.httpd_server.shutdown()
            self.httpd_server.server_close()
            self.server_thread.join(timeout=2)
            logger.info(f"{self.name}: Server stopped on port {self.port}")
            self.httpd_server = None
            self.server_thread = None
            self.site_folder_to_serve = None