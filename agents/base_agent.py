# agents/base_agent.py

class BaseAgent:
    def __init__(self, name):
        self.name = name
        print(f"{self.name} agent started.")

    def assign_task(self, task):
        print(f"{self.name}: New task - {task}")

    def execute(self):
        print(f"{self.name}: Working...")

    def task_completed(self, result):
        print(f"{self.name}: Task completed. Result: {result}")