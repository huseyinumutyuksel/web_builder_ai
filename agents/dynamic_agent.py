# agents/dynamic_agent.py
from agents.base_agent import BaseAgent

class DynamicAgent(BaseAgent):
    def __init__(self, name="Dynamic Agent"):
        super().__init__(name)

    def execute(self, task):
        print(f"{self.name}: Generating basic Javascript...")
        javascript_code = """
        document.addEventListener('DOMContentLoaded', function() {
            var mainContent = document.getElementById('content');
            if (mainContent) {
                var helloButton = document.createElement('button');
                helloButton.textContent = 'Tıkla ve Merhaba De!';
                helloButton.addEventListener('click', function() {
                    alert('Merhaba!');
                });
                mainContent.appendChild(helloButton);
            }
        });
        """
        return {"javascript": javascript_code}