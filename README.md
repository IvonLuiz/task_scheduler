# Real-Time Task Scheduler

A Python-based real-time task scheduler that implements classic scheduling algorithms with dynamic visualization. The system uses a client-server architecture to allow real-time task management across multiple terminals.

## Overview

This task scheduler simulates real-time task execution using discrete integer time ticks (1 tick = 1 second). It supports two classic scheduling algorithms and provides a live Gantt chart visualization in the server terminal.

### Key Features

- **Real-time execution** with integer time ticks
- **Multi-terminal support** via client-server architecture
- **Live Gantt chart visualization** on the server
- **Dynamic task addition** while the scheduler is running
- **Deadline monitoring** with miss detection
- **Initial task loading** from JSON files
- **Two scheduling algorithms**: Rate Monotonic (RM) and Earliest Deadline First (EDF)

## Scheduling Algorithms

### Rate Monotonic (RM)
- **Priority**: Tasks with shorter periods have higher priority
- **Static priority**: Priority is assigned once based on period
- **Optimal for fixed-priority scheduling**: Guarantees schedulability if utilization ≤ 69% for large task sets
- **Best for**: Predictable, periodic tasks with fixed execution patterns

### Earliest Deadline First (EDF)
- **Priority**: Task with the earliest absolute deadline has highest priority
- **Dynamic priority**: Priority changes based on current deadlines
- **Optimal for dynamic scheduling**: Guarantees schedulability if total utilization ≤ 100%
- **Best for**: Mixed workloads with varying deadline constraints

## Architecture

```
┌─────────────────┐    TCP/IP    ┌─────────────────┐
│     Client      │◄────────────►│     Server      │
│   (client.py)   │              │   (server.py)   │
│                 │              │                 │
│ - Add tasks     │              │ - Run scheduler │
│ - View status   │              │ - Live Gantt    │
│ - List tasks    │              │ - Handle clients│
└─────────────────┘              └─────────────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │   Scheduler     │
                                 │ (scheduler.py)  │
                                 │                 │
                                 │ - Execute tasks │
                                 │ - Check deadlines│
                                 │ - Update display │
                                 └─────────────────┘
```

## Usage

### Server

#### Basic Server Startup

Start the server with default settings (RM algorithm, port 8888):
```bash
./server.py
```

Start with specific algorithm:
```bash
./server.py --algorithm EDF
./server.py -a RM
```

Start on different port:
```bash
./server.py --port 9000
./server.py -p 9000
```

Server Command-Line options:
```bash
./server.py --help
```

#### Server with Initial Tasks

Create a JSON file with initial tasks (see `initial_tasks.json` example):
```json
[
    {
        "name": "T1",
        "period": 4,
        "execution_time": 2,
        "deadline": 4
    },
    {
        "name": "T2", 
        "period": 6,
        "execution_time": 3
    }
]
```

Start server with initial tasks:
```bash
./server.py --tasks initial_tasks.json
./server.py -t initial_tasks.json
```

Combined options:
```bash
./server.py -a EDF -p 9000 -t initial_tasks.json
```

### 2. Client Usage

#### Interactive Mode
Start the client in interactive mode:
```bash
./client.py
```

Available commands in interactive mode:
- `add <period> <exec_time> [deadline]` - Add a new task
- `status` - Show current scheduler status
- `list` - List all tasks with details
- `quit` - Exit the client

#### Command-Line Mode
Add a task directly:
```bash
./client.py add 5 2        # Period=5, Execution=2, Deadline=5 (default)
./client.py add 8 3 6      # Period=8, Execution=3, Deadline=6
```

Get status:
```bash
./client.py status
```

List all tasks:
```bash
./client.py list
```

Connect to different server:
```bash
./client.py --host 192.168.1.100 --port 9000 add 4 2
```

Client Command-Line options
```bash
./client.py --help
```

## Visualization Guide

The server displays a real-time Gantt chart that updates every second:

```
🚀 Scheduler running with RM algorithm | Current Tick: 15
--------------------------------------------------------------------------------
T1    |██  ░██ ░░██ ░██ 
T2    |░░███░░███░░░░░░░
T3    |     ░░██░░░░░░░
------+..........|.....
--------------------------------------------------------------------------------
📋 Event Log:
  Task T1 added (P=4, E=2)
  Task T2 added (P=6, E=3)
  T1[1] released at tick 0
  T2[1] released at tick 0
  T1[2] released at tick 4
  T2[2] released at tick 6
  Task T3 added (P=8, E=2)
  T3[1] released at tick 8
  T1[3] released at tick 8
  T2[3] released at tick 12
```

### Chart Symbols
- `█` - Task is executing
- `░` - Task is ready but waiting
- `R` - Task release point
- `D` - Task deadline
- ` ` - Task is idle/not ready
- `.` - Timeline tick marks
- `|` - Timeline every 10 ticks

## Task Properties

### Required Parameters
- **Period**: How often the task repeats (integer ticks)
- **Execution Time**: How long the task takes to complete (integer ticks)

### Optional Parameters
- **Deadline**: When the task must complete (integer ticks, defaults to period)

### Task Naming
- **JSON tasks**: Use the name specified in the JSON file
- **Client tasks**: Auto-named as T1, T2, T3, etc.

### Deadline Calculation
Deadlines are relative to task release time:
- If a task is released at tick 10 with deadline 5, it must complete by tick 15
- Each task instance gets a fresh deadline based on its release time

## Examples

### Example 1: Basic Rate Monotonic Scheduling
```bash
# Terminal 1: Start server
./server.py -a RM

# Terminal 2: Add tasks
./client.py add 4 2    # High priority (short period)
./client.py add 8 3    # Low priority (long period)
```

### Example 2: EDF with Initial Tasks
```bash
# Terminal 1: Start with initial tasks
./server.py -a EDF -t initial_tasks.json

# Terminal 2: Add more tasks dynamically
./client.py add 10 4 8  # Period=10, Exec=4, Deadline=8
```

### Example 3: Deadline Miss Scenario
```bash
# Terminal 1: Start server
./server.py -a RM

# Terminal 2: Add overloaded tasks
./client.py add 4 3    # Task needs 3 ticks every 4 ticks
./client.py add 6 4    # Task needs 4 ticks every 6 ticks
# Total utilization: 3/4 + 4/6 = 1.42 > 1.0 (overloaded)
```
