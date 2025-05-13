# agents/base_agent.py

class BaseAgent:
    def __init__(self, name):
        self.name = name
        print(f"{self.name} agent started.")

    def assign_task(self, task):
        print(f"{self.name}: New task - {task}")

    def execute(self, task=None): # İmza güncellendi
        """
        Executes the agent's primary task.
        The task parameter is optional to allow for agents that might not need explicit input for their execute method.
        """
        print(f"{self.name}: Working on task: {task if task else 'general duties'}...")
        # Base implementation can be a no-op or raise NotImplementedError
        # to force subclasses to implement it.
        # For this project, a simple print statement is fine.

    def task_completed(self, result):
        print(f"{self.name}: Task completed. Result: {result}")