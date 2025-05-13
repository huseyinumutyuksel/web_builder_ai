# agents/backend_agent.py
from agents.base_agent import BaseAgent

class BackendAgent(BaseAgent):
    def __init__(self, name="Backend Agent"):
        super().__init__(name)

    def execute(self, task):
        print(f"{self.name}: Simulating backend initialization...")
        # İleride backend işlemleri burada gerçekleştirilecek
        backend_status = "Backend is ready and running."
        return {"status": backend_status}