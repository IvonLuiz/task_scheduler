import threading
import time
from collections import deque
from task import Task


class Scheduler:
    def __init__(self, algorithm="RM"):
        """
        Simple scheduler with integer time ticks.
        
        Args:
            algorithm: "RM" for Rate Monotonic or "EDF" for Earliest Deadline First
        """
        self.algorithm = algorithm
        self.tasks = {}
        self.ready_queue = []
        self.running_task = None
        self.current_tick = 0
        self.is_running = False
        self.scheduler_thread = None
        self.task_lock = threading.Lock()
        self.execution_history = []  # What ran at each tick
        
        # For visualization
        self.gantt_chart_data = {}
        self.task_display_order = []
        self.event_log = deque(maxlen=10)  # Store last 10 events
        
    def add_task(self, task):
        """Add a new task to the scheduler"""
        with self.task_lock:
            if task.name not in self.tasks:
                self.tasks[task.name] = task
                if task.name not in self.gantt_chart_data:
                    self.task_display_order.append(task.name)
                    # Pad with spaces for ticks that have already passed
                    self.gantt_chart_data[task.name] = [' '] * self.current_tick
                
                log_msg = f"Task {task.name} added (P={task.period}, E={task.execution_time})"
                self.event_log.append(log_msg)
            else:
                # This case should probably not happen with auto-naming, but good to have
                self.tasks[task.name] = task
    
    def start(self):
        """Start the scheduler"""
        if self.is_running:
            return
            
        self.is_running = True
        self.current_tick = 0
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        print("\nScheduler stopped")
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            with self.task_lock:
                self._release_tasks()
                self._check_deadlines()
                current_task = self._execute_task()
                self._update_and_draw_gantt(current_task)
                
            time.sleep(1)  # 1 second per tick
            self.current_tick += 1
    
    def _release_tasks(self):
        """Check and release tasks that are ready"""
        for task in self.tasks.values():
            if self.current_tick >= task.next_release and task.remaining_time == 0:
                task.release(self.current_tick)
                if task not in self.ready_queue:
                    self.ready_queue.append(task)
                
                log_msg = f"{task} released at tick {self.current_tick}"
                self.event_log.append(log_msg)
    
    def _check_deadlines(self):
        """Check for deadline misses"""
        for task in self.tasks.values():
            # Check only active tasks (released but not finished)
            if task.remaining_time > 0 and task.instance > 0:
                # The absolute deadline for the current instance
                absolute_deadline = task.release_time + task.deadline
                
                if self.current_tick > absolute_deadline:
                    # Check if this miss has already been recorded for this instance
                    if task.instance not in task.deadline_misses:
                        task.deadline_misses.append(task.instance)
                        log_msg = f"❌ {task.name}[{task.instance}] MISSED DEADLINE at tick {absolute_deadline}"
                        self.event_log.append(log_msg)
    
    def _execute_task(self):
        """Execute the highest priority task with preemption"""
        # For Rate Monotonic: Check if we need to preempt current task
        if self.algorithm == "RM" and self.running_task and self.ready_queue:
            highest_priority_task = min(self.ready_queue, key=lambda t: t.period)
            # Preempt if a higher priority task (shorter period) is ready
            if highest_priority_task.period < self.running_task.period:
                # Put current task back in ready queue
                if self.running_task not in self.ready_queue:
                    self.ready_queue.append(self.running_task)
                self.running_task = highest_priority_task
        
        # For EDF: Check if we need to preempt current task  
        elif self.algorithm == "EDF" and self.running_task and self.ready_queue:
            earliest_deadline_task = min(self.ready_queue, key=lambda t: t.release_time + t.deadline)
            current_deadline = self.running_task.release_time + self.running_task.deadline
            earliest_deadline = earliest_deadline_task.release_time + earliest_deadline_task.deadline
            # Preempt if a task with earlier deadline is ready
            if earliest_deadline < current_deadline:
                # Put current task back in ready queue
                if self.running_task not in self.ready_queue:
                    self.ready_queue.append(self.running_task)
                self.running_task = earliest_deadline_task
        
        # Select task if none is running
        if not self.running_task:
            self.running_task = self._select_task()
        
        current_task_name = "idle"
        if self.running_task:
            current_task_name = self.running_task.name
            self.running_task.remaining_time -= 1
            
            # Task completed
            if self.running_task.remaining_time <= 0:
                if self.running_task in self.ready_queue:
                    self.ready_queue.remove(self.running_task)
                self.running_task = None
        
        # Record execution history
        self.execution_history.append(current_task_name)
        return current_task_name
    
    def _select_task(self):
        """Select the highest priority task from ready queue"""
        if not self.ready_queue:
            return None
        
        if self.algorithm == "RM":
            return min(self.ready_queue, key=lambda t: t.period)
        elif self.algorithm == "EDF":
            # For EDF, priority is the absolute deadline
            return min(self.ready_queue, key=lambda t: t.release_time + t.deadline)
        else:
            raise ValueError("Invalid algorithm: use 'RM' or 'EDF'")
    
    def _update_and_draw_gantt(self, current_task_name):
        """Update data and redraw the Gantt chart in the terminal."""
        # Update data for all tasks for the current tick
        for name, task in self.tasks.items():
            char = ' '
            if name == current_task_name:
                char = '█'  # Executing
            elif task in self.ready_queue:
                char = '░'  # Ready but not running
            
            if self.current_tick == task.next_release:
                char = 'R' # Release
            if task.instance > 0 and self.current_tick == task.release_time + task.deadline:
                char = 'D' # Deadline
                
            self.gantt_chart_data[name].append(char)

        # Clear screen and redraw
        print("\033c", end="")
        
        print(f"Scheduler running with {self.algorithm} algorithm | Current Tick: {self.current_tick}")
        print("-" * 80)
        
        # Determine window for display
        width = 70
        start_tick = max(0, self.current_tick - width + 1)
        end_tick = self.current_tick + 1
        
        # Draw chart
        for name in self.task_display_order:
            line = "".join(self.gantt_chart_data[name][start_tick:end_tick])
            print(f"{name:<5} |{line}")
        
        # Draw timeline ruler
        ruler_parts = []
        for i in range(start_tick, end_tick):
            if i > 0 and i % 10 == 0:
                ruler_parts.append('|')
            else:
                ruler_parts.append('.')
        ruler = "".join(ruler_parts)
        print("------" + ruler)
        
        # Draw event log
        print("-" * 80)
        print("📋 Event Log:")
        for event in self.event_log:
            print(f"  {event}")
    
    def get_status(self):
        """Get current scheduler status"""
        return {
            "current_tick": self.current_tick,
            "running_task": str(self.running_task) if self.running_task else "idle",
            "ready_queue": [str(task) for task in self.ready_queue],
            "total_tasks": len(self.tasks)
        }
