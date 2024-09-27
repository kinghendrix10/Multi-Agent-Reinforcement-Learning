# /environment.py
class TaskEnvironment:
    def __init__(self):
        self.tasks = []
        self.current_task = None

    def add_task(self, task):
        self.tasks.append(task)

    def get_next_task(self):
        if self.tasks:
            self.current_task = self.tasks.pop(0)
            return self.current_task
        return None

    def reset(self):
        self.tasks = []
        self.current_task = None
