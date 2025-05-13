# agents/reviewer_agent.py
from agents.base_agent import BaseAgent
from bs4 import BeautifulSoup
import os # os.path.exists için eklendi
import logging

logger = logging.getLogger(__name__)

class ReviewerAgent(BaseAgent):
    def __init__(self, name="Reviewer Agent"):
        super().__init__(name)

    def execute(self, task): # İmza zaten task alıyordu
        site_folder = task.get('site_folder')
        logger.info(f"{self.name}: Reviewing website files in: {site_folder}")
        report = {"errors": [], "warnings": [], "info": []}

        if not site_folder or not os.path.isdir(site_folder): # Klasör var mı ve klasör mü?
            report["errors"].append(f"Site folder path '{site_folder}' is missing or not a directory.")
            logger.error(report["errors"][-1])
            return report

        index_html_path = os.path.join(site_folder, "index.html")
        style_css_path = os.path.join(site_folder, "style.css")

        # index.html kontrolleri
        if os.path.exists(index_html_path):
            try:
                with open(index_html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    if not html_content.strip():
                        report["errors"].append("index.html is empty.")
                    else:
                        soup = BeautifulSoup(html_content, 'html.parser')
                        if not soup.find('title') or not soup.find('title').string.strip():
                            report["warnings"].append("No <title> tag or empty title found in index.html.")
                        if not soup.find('h1') or not soup.find('h1').string.strip():
                            report["warnings"].append("No <h1> tag or empty h1 found in index.html.")
                        if not soup.find('section', id='content'):
                            report["warnings"].append("No <section id='content'> found in index.html.")
                        # img etiketlerinde alt özelliği var mı kontrolü
                        for img_tag in soup.find_all('img'):
                            if not img_tag.get('alt', '').strip():
                                report["warnings"].append(f"Image missing alt text: {str(img_tag)[:50]}...")
            except Exception as e:
                error_msg = f"Error parsing index.html: {e}"
                report["errors"].append(error_msg)
                logger.error(error_msg, exc_info=True)
        else:
            report["errors"].append(f"index.html not found in {site_folder}.")

        # style.css kontrolleri
        if os.path.exists(style_css_path):
            try:
                with open(style_css_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                    if not css_content.strip():
                        report["warnings"].append("style.css is empty.")
                    elif 'body {' not in css_content: # Çok basit bir kontrol
                        report["info"].append("No basic 'body' style found in style.css. This might be intentional.")
            except Exception as e:
                error_msg = f"Error reading style.css: {e}"
                report["errors"].append(error_msg)
                logger.error(error_msg, exc_info=True)
        else:
            report["errors"].append(f"style.css not found in {site_folder}.")

        if report["errors"]:
            logger.error(f"{self.name}: Found critical issues: {report['errors']}")
        if report["warnings"]:
            logger.warning(f"{self.name}: Found warnings: {report['warnings']}")
        
        if not report["errors"] and not report["warnings"]:
            logger.info(f"{self.name}: No major issues found during review of {site_folder}.")
            report["info"].append("Review completed, no major issues found.")

        return report