# agents/server_agent.py
from agents.base_agent import BaseAgent
import http.server
import socketserver
import os
import threading

class SimpleWebServer(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

class ServerAgent(BaseAgent):
    def __init__(self, name="Server Agent", port=8000):
        super().__init__(name)
        self.port = port
        self.server = None
        self.server_thread = None
        self.site_folder = None

    def start_server(self, site_folder):
        self.site_folder = site_folder
        os.chdir(self.site_folder)
        handler = SimpleWebServer
        with socketserver.TCPServer(("", self.port), handler) as httpd:
            print(f"{self.name}: Serving at port {self.port} from {self.site_folder}")
            self.server = httpd
            httpd.serve_forever()

    def execute(self, task):
        print(f"{self.name}: Starting local web server...")
        self.site_folder = task.get("site_folder")
        if not self.site_folder or not os.path.exists(self.site_folder):
            return {"success": False, "message": "Site folder not found."}

        self.server_thread = threading.Thread(target=self.start_server, args=(self.site_folder,))
        self.server_thread.daemon = True  # Ana thread kapandığında bu da kapansın
        self.server_thread.start()

        return {"success": True, "url": f"http://localhost:{self.port}"}

    def stop_server(self):
        if self.server:
            print(f"{self.name}: Stopping the server.")
            self.server.shutdown()
            self.server_thread.join()
            os.chdir("..") # Ana dizine geri dön
            self.server = None
            self.server_thread = None