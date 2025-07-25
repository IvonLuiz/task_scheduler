from task import Task
from scheduler import Scheduler


def print_timeline(timeline):
    print("Tempo: ", ' '.join([str(i).rjust(2) for i in range(len(timeline))]))
    print("Exec.: ", ' '.join(timeline))

#Exemplo 1
tasks = [
    Task("T1", period=4, execution_time=1),
    Task("T2", period=5, execution_time=2),
]

print("Rate Monotonic:")
rm = Scheduler(tasks, algorithm="RM", simulation_time=20)
timeline_rm = rm.schedule()
print_timeline(timeline_rm)
for miss in rm.get_deadline_misses():
    print("⚠️", miss)

#Exemplo 2
tasks = [
    Task("T1", period=4, execution_time=2),
    Task("T2", period=5, execution_time=3),
]

print("Rate Monotonic:")
rm = Scheduler(tasks, algorithm="RM", simulation_time=20)
timeline_rm = rm.schedule()
print_timeline(timeline_rm)
for miss in rm.get_deadline_misses():
    print("⚠️", miss)

#Exemplo 3
tasks = [
    Task("T1", period=4, execution_time=1),
    Task("T2", period=5, execution_time=2),
]

print("\nEarliest Deadline First:")
edf = Scheduler(tasks, algorithm="EDF", simulation_time=20)
timeline_edf = edf.schedule()
print_timeline(timeline_edf)
for miss in edf.get_deadline_misses():
    print("⚠️", miss)

#Exemplo 4
tasks = [
    Task("T1", period=4, execution_time=2),
    Task("T2", period=5, execution_time=3),
]

print("\nEarliest Deadline First:")
edf = Scheduler(tasks, algorithm="EDF", simulation_time=20)
timeline_edf = edf.schedule()
print_timeline(timeline_edf)
for miss in edf.get_deadline_misses():
    print("⚠️", miss)