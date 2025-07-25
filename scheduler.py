class Scheduler:
    def __init__(self, tasks, algorithm="RM", simulation_time=20):
        self.tasks = tasks
        self.algorithm = algorithm
        self.simulation_time = simulation_time
        self.ready_queue = []
        self.timeline = []

    def schedule(self):
        for t in range(self.simulation_time):
            # Libera novas instâncias
            for task in self.tasks:
                if t == task.next_release:
                    task.release(t)

            # Adiciona tarefas prontas
            for task in self.tasks:
                if task.remaining_time > 0 and task not in self.ready_queue:
                    self.ready_queue.append(task)

            # Seleciona a tarefa
            current = self.select_task(t)

            if current:
                current.remaining_time -= 1
                self.timeline.append(current.name)
                if current.remaining_time == 0:
                    self.ready_queue.remove(current)
            else:
                self.timeline.append("idle")

        return self.timeline

    def select_task(self, current_time):
        if not self.ready_queue:
            return None

        if self.algorithm == "RM":
            return min(self.ready_queue, key=lambda t: t.period)
        elif self.algorithm == "EDF":
            return min(self.ready_queue, key=lambda t: t.deadline * t.instance)
        else:
            raise ValueError("Algoritmo inválido: use 'RM' ou 'EDF'")

    def get_deadline_misses(self):
        misses = []
        for task in self.tasks:
            for instance, time in task.deadline_misses:
                deadline_time = task.period * instance
                misses.append(f"{task.name}[{instance}] perdeu deadline em t={deadline_time}")
        return misses
