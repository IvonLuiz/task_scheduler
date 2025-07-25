#!/usr/bin/env python3
"""
Simple Task Scheduler Server

Clean implementation with integer time ticks and real-time Gantt visualization.
"""

import socket
import threading
import json
import sys
from task import Task
from scheduler import Scheduler


class SchedulerServer:
    def __init__(self, host='localhost', port=8888, algorithm="RM"):
        self.host = host
        self.port = port
        self.scheduler = Scheduler(algorithm=algorithm)
        self.server_socket = None
        self.is_running = False
        self.client_connections = []
        self.task_counter = 0  # For auto-naming tasks T1, T2, T3...
        
    def load_tasks_from_file(self, filepath):
        """Load initial tasks from a JSON file"""
        try:
            with open(filepath, 'r') as f:
                tasks_data = json.load(f)
            
            for task_info in tasks_data:
                name = task_info['name']
                # JSON might have floats, scheduler uses ints
                period = int(task_info['period'])
                execution_time = int(task_info['execution_time'])
                deadline = int(task_info.get('deadline', period))
                
                task = Task(name, period, execution_time, deadline)
                self.scheduler.add_task(task)
            
            log_msg = f"Loaded {len(tasks_data)} tasks from {filepath}"
            self.scheduler.event_log.append(log_msg)

        except FileNotFoundError:
            print(f"Error: Initial tasks file not found at {filepath}", file=sys.stderr)
            sys.exit(1)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing tasks file {filepath}: {e}", file=sys.stderr)
            sys.exit(1)

    def start_server(self):
        """Start the scheduler server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.is_running = True
            self.scheduler.start()
            
            print(f"Server started on {self.host}:{self.port}")
            print(f"Using {self.scheduler.algorithm} algorithm")
            print("Waiting for client connections...")
            print("Use Ctrl+C to stop the server")
            
            # Accept client connections
            while self.is_running:
                try:
                    client_socket, address = self.server_socket.accept()
                    
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.error:
                    if self.is_running:
                        print("Socket error occurred")
                    break
                    
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop_server()
    
    def handle_client(self, client_socket, address):
        """Handle commands from a client"""
        self.client_connections.append(client_socket)
        
        try:
            # Send welcome message
            welcome = {
                "type": "welcome",
                "message": f"Connected to Simple Task Scheduler",
                "algorithm": self.scheduler.algorithm
            }
            self.send_to_client(client_socket, welcome)
            
            while self.is_running:
                try:
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                        
                    # Parse command
                    command = json.loads(data)
                    response = self.process_command(command)
                    self.send_to_client(client_socket, response)
                    
                except json.JSONDecodeError:
                    error_response = {"type": "error", "message": "Invalid JSON command"}
                    self.send_to_client(client_socket, error_response)
                except socket.error:
                    break
                    
        except Exception as e:
            # This will be logged to the server console, not sent to client
            print(f"\nClient handler error for {address}: {e}")
        finally:
            if client_socket in self.client_connections:
                self.client_connections.remove(client_socket)
            client_socket.close()
            # Log disconnection on the server
            log_msg = f"Client {address} disconnected"
            self.scheduler.event_log.append(log_msg)
    
    def send_to_client(self, client_socket, data):
        """Send data to a client"""
        try:
            message = json.dumps(data) + '\n'
            client_socket.send(message.encode('utf-8'))
        except socket.error:
            pass
    
    def process_command(self, command):
        """Process a command from a client"""
        cmd_type = command.get("type", "")
        
        try:
            if cmd_type == "add_task":
                return self.handle_add_task(command)
            elif cmd_type == "get_status":
                return self.handle_get_status()
            elif cmd_type == "list_tasks":
                return self.handle_list_tasks()
            else:
                return {"type": "error", "message": f"Unknown command: {cmd_type}"}
                
        except Exception as e:
            return {"type": "error", "message": f"Command error: {str(e)}"}
    
    def handle_add_task(self, command):
        """Handle add_task command"""
        try:
            period = int(command["period"])
            execution_time = int(command["execution_time"])
            deadline = int(command.get("deadline", period))
            
            # Auto-generate task name
            self.task_counter += 1
            name = f"T{self.task_counter}"
            
            task = Task(name, period, execution_time, deadline)
            self.scheduler.add_task(task)
            
            return {
                "type": "success",
                "message": f"Task {name} added successfully",
                "task": {"name": name, "period": period, "execution_time": execution_time, "deadline": deadline}
            }
            
        except (KeyError, ValueError) as e:
            return {"type": "error", "message": f"Invalid parameters: {e}"}
    
    def handle_get_status(self):
        """Handle get_status command"""
        status = self.scheduler.get_status()
        return {"type": "status", "data": status}
    
    def handle_list_tasks(self):
        """Handle list_tasks command"""
        with self.scheduler.task_lock:
            tasks = []
            for task in self.scheduler.tasks.values():
                tasks.append({
                    "name": task.name,
                    "period": task.period,
                    "execution_time": task.execution_time,
                    "deadline": task.deadline,
                    "remaining_time": task.remaining_time,
                    "instance": task.instance,
                    "next_release": task.next_release
                })
        return {"type": "task_list", "data": tasks}
    
    def stop_server(self):
        """Stop the scheduler server"""
        print("\nStopping scheduler server...")
        self.is_running = False
        
        if self.scheduler:
            # Generate and display final report
            report = self.scheduler.generate_final_report()
            print(report)
            
            self.scheduler.stop()
        
        # Close all client connections
        for client in self.client_connections[:]:
            try:
                client.close()
            except:
                pass
        self.client_connections.clear()
        
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        print("✅ Server stopped")


def main():
    """Main function to start the scheduler server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple Task Scheduler Server")
    parser.add_argument("--port", "-p", type=int, default=8888, help="Server port (default: 8888)")
    parser.add_argument("--algorithm", "-a", choices=["RM", "EDF"], default="RM", help="Scheduling algorithm (default: RM)")
    parser.add_argument("--tasks", "-t", type=str, help="Path to a JSON file with initial tasks")
    
    args = parser.parse_args()
    
    # Create and start server
    server = SchedulerServer(
        port=args.port,
        algorithm=args.algorithm
    )
    
    # Load initial tasks if file is provided
    if args.tasks:
        server.load_tasks_from_file(args.tasks)
    
    try:
        server.start_server()
        
    except KeyboardInterrupt:
        print("\nServer interrupted by user")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server.stop_server()


if __name__ == "__main__":
    main()
