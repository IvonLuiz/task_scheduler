class Task:
    def __init__(self, name, period, execution_time, deadline=None):
        self.name = name
        self.period = period  # Integer time ticks
        self.execution_time = execution_time  # Integer time ticks
        self.deadline = deadline or period  # Integer time ticks
        self.remaining_time = 0
        self.next_release = 0
        self.instance = 0
        self.release_time = 0  # Time of the current instance's release
        self.deadline_misses = []

    def release(self, current_tick):
        """Release a new instance of the task"""
        if self.remaining_time > 0:
            # Task missed deadline
            self.deadline_misses.append(self.instance)
        
        self.release_time = current_tick
        self.remaining_time = self.execution_time
        self.next_release = current_tick + self.period
        self.instance += 1

    def __repr__(self):
        return f"{self.name}[{self.instance}]"
