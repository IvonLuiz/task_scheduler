class Task:
    def __init__(self, name, period, execution_time, deadline=None):
        self.name = name
        self.period = period
        self.execution_time = execution_time
        self.deadline = deadline or period
        self.remaining_time = 0
        self.next_release = 0
        self.instance = 0
        self.deadline_misses = []

    def release(self, time):
        if self.remaining_time > 0:
            self.deadline_misses.append((self.instance, time))  # perdeu o deadline anterior
        self.remaining_time = self.execution_time
        self.next_release = time + self.period
        self.instance += 1

    def __repr__(self):
        return f"{self.name}[{self.instance}]"
