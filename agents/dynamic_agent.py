# agents/dynamic_agent.py
from agents.base_agent import BaseAgent

class DynamicAgent(BaseAgent):
    def __init__(self, name="Dynamic Agent"):
        super().__init__(name)

    def execute(self, task=None): # İmza güncellendi (task=None eklendi)
        print(f"{self.name}: Generating basic Javascript...")
        javascript_code = """
        document.addEventListener('DOMContentLoaded', function() {
            var mainContent = document.getElementById('content');
            if (mainContent) {
                var helloButton = document.createElement('button');
                helloButton.textContent = 'Tıkla ve Merhaba De!';
                helloButton.style.marginTop = '20px';
                helloButton.style.padding = '10px 15px';
                helloButton.style.backgroundColor = '#007bff';
                helloButton.style.color = 'white';
                helloButton.style.border = 'none';
                helloButton.style.borderRadius = '4px';
                helloButton.style.cursor = 'pointer';

                helloButton.addEventListener('click', function() {
                    alert('Merhaba! Bu dinamik bir butondur.');
                });
                // Butonu doğrudan mainContent yerine son bölümden sonra ekleyebiliriz.
                // Veya belirli bir ID'ye sahip bir elemente ekleyebiliriz.
                // Şimdilik content'in sonuna ekleyelim.
                var lastSectionP = mainContent.querySelector('p:last-of-type');
                if (lastSectionP && lastSectionP.parentNode) {
                    lastSectionP.parentNode.insertBefore(helloButton, lastSectionP.nextSibling);
                } else {
                     mainContent.appendChild(helloButton);
                }

            }
        });
        """
        return {"javascript": javascript_code}