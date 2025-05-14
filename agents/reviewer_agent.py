import os
import logging
from bs4 import BeautifulSoup
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ReviewerAgent(BaseAgent):
    def __init__(self, name="Reviewer Agent"):
        super().__init__(name)

    def _read_file(self, filepath: str) -> str:
        """Dosya içeriğini okur ve hata durumunda loglar."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}", exc_info=True)
            return None

    def execute(self, task):
        site_folder = task.get('site_folder')
        logger.info(f"{self.name}: Reviewing website files in: {site_folder}")
        report = {"errors": [], "warnings": [], "info": []}

        if not site_folder or not os.path.isdir(site_folder):
            report["errors"].append(f"Site folder '{site_folder}' is invalid.")
            logger.error(report["errors"][-1])
            return report

        index_html_path = os.path.join(site_folder, "index.html")
        style_css_path = os.path.join(site_folder, "style.css")

        # HTML Kontrolleri
        html_content = self._read_file(index_html_path)
        if not html_content:
            report["errors"].append(f"index.html not found or unreadable in {site_folder}.")
        elif not html_content.strip():
            report["errors"].append("index.html is empty.")
        else:
            soup = BeautifulSoup(html_content, 'html.parser')
            if not soup.title or not soup.title.string.strip():
                report["warnings"].append("Missing or empty <title> tag.")
            if not soup.find('h1') or not soup.find('h1').string.strip():
                report["warnings"].append("Missing or empty <h1> tag.")
            if not soup.find('section', id='content'):
                report["warnings"].append("Missing <section id='content'>.")
            for img in soup.find_all('img'):
                if not img.get('alt', '').strip():
                    report["warnings"].append(f"Image missing alt text: {str(img)[:50]}...")

        # CSS Kontrolleri
        css_content = self._read_file(style_css_path)
        if not css_content:
            report["errors"].append(f"style.css not found or unreadable in {site_folder}.")
        elif not css_content.strip():
            report["warnings"].append("style.css is empty.")
        elif 'body {' not in css_content:
            report["info"].append("No 'body' style found in style.css.")

        # Rapor Özeti
        if not report["errors"] and not report["warnings"]:
            report["info"].append("Review completed, no major issues found.")
            logger.info(f"{self.name}: No issues found in {site_folder}.")
        return report