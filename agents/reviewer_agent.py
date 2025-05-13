# agents/reviewer_agent.py
from agents.base_agent import BaseAgent
from bs4 import BeautifulSoup

class ReviewerAgent(BaseAgent):
    def __init__(self, name="Reviewer Agent"):
        super().__init__(name)

    def execute(self, task):
        print(f"{self.name}: Reviewing website files in: {task.get('site_folder')}")
        site_folder = task.get('site_folder')
        report = {"errors": []}

        if not site_folder:
            report["errors"].append("Site folder path is missing.")
            return report

        index_html_path = f"{site_folder}/index.html"
        style_css_path = f"{site_folder}/style.css"

        try:
            with open(index_html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                soup = BeautifulSoup(html_content, 'html.parser')

                # Basit bir kontrol: title etiketi var mı?
                if not soup.find('title'):
                    report["errors"].append("No <title> tag found in index.html.")

                # Basit bir kontrol: h1 etiketi var mı?
                if not soup.find('h1'):
                    report["errors"].append("No <h1> tag found in index.html.")

        except FileNotFoundError:
            report["errors"].append(f"index.html not found in {site_folder}.")
        except Exception as e:
            report["errors"].append(f"Error parsing index.html: {e}")

        try:
            with open(style_css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
                # Basit bir kontrol: body için temel bir stil tanımı var mı?
                if 'body {' not in css_content:
                    report["errors"].append("No basic 'body' style found in style.css.")
        except FileNotFoundError:
            report["errors"].append(f"style.css not found in {site_folder}.")
        except Exception as e:
            report["errors"].append(f"Error reading style.css: {e}")

        if report["errors"]:
            print(f"{self.name}: Found the following issues: {report['errors']}")
        else:
            print(f"{self.name}: No major issues found.")

        return report