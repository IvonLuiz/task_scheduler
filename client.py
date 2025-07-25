#!/usr/bin/env python3
import socket
import json
import sys


class Client:
    def __init__(self, host='localhost', port=8888):
        self.host = host
        self.port = port
        self.socket = None
        self.is_connected = False
        
    def connect(self):
        """Connect to the scheduler server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.is_connected = True
            
            # Read welcome message
            data = self.socket.recv(1024).decode('utf-8')
            if data:
                message = json.loads(data.strip())
                if message.get("type") == "welcome":
                    print(f"{message['message']}")
                    print(f"Algorithm: {message['algorithm']}")
            
            return True
            
        except ConnectionRefusedError:
            print(f"❌ Cannot connect to server at {self.host}:{self.port}")
            print("💡 Make sure the scheduler server is running")
            return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        self.is_connected = False
        if self.socket:
            self.socket.close()
    
    def send_command(self, command):
        """Send a command to the server and get response"""
        if not self.is_connected:
            print("❌ Not connected to server")
            return None
            
        try:
            message = json.dumps(command) + '\n'
            self.socket.send(message.encode('utf-8'))
            
            # Wait for response
            data = self.socket.recv(1024).decode('utf-8')
            if data:
                response = json.loads(data.strip())
                return response
            return None
            
        except Exception as e:
            print(f"❌ Error sending command: {e}")
            self.is_connected = False
            return None
    
    def add_task(self, period, execution_time, deadline=None):
        """Add a task to the scheduler"""
        command = {
            "type": "add_task",
            "period": period,
            "execution_time": execution_time
        }
        if deadline is not None:
            command["deadline"] = deadline
        
        response = self.send_command(command)
        if response:
            if response.get("type") == "success":
                task = response.get("task", {})
                print(f"✅ {response['message']}")
                print(f"   Period: {task.get('period')} ticks")
                print(f"   Execution: {task.get('execution_time')} ticks")
                print(f"   Deadline: {task.get('deadline')} ticks")
            else:
                print(f"❌ {response.get('message', 'Unknown error')}")
    
    def get_status(self):
        """Request current status"""
        response = self.send_command({"type": "get_status"})
        if response and response.get("type") == "status":
            data = response["data"]
            print(f"\n📊 Status (tick {data['current_tick']}):")
            print(f"   Running: {data['running_task']}")
            print(f"   Queue length: {len(data['ready_queue'])}")
            print(f"   Total tasks: {data['total_tasks']}")
    
    def list_tasks(self):
        """Request list of tasks"""
        response = self.send_command({"type": "list_tasks"})
        if response and response.get("type") == "task_list":
            tasks = response["data"]
            if not tasks:
                print("\n📋 No tasks in the system")
                return
                
            print(f"\n📋 Tasks ({len(tasks)} total):")
            print("   Name  Period  Exec  Deadline  Remaining  Instance  Next")
            print("   " + "-" * 55)
            for task in tasks:
                print(f"   {task['name']:<4}  {task['period']:<6}  {task['execution_time']:<4}  "
                      f"{task['deadline']:<8}  {task['remaining_time']:<9}  {task['instance']:<8}  {task['next_release']}")


def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Task Scheduler Client")
    parser.add_argument("--host", "-H", default="localhost", help="Server host (default: localhost)")
    parser.add_argument("--port", "-p", type=int, default=8888, help="Server port (default: 8888)")
    parser.add_argument("command", nargs="*", help="Command: add <period> <exec_time> [deadline] | status | list")
    
    args = parser.parse_args()
    
    client = Client(args.host, args.port)
    
    if not client.connect():
        sys.exit(1)
    
    try:
        if args.command:
            # Non-interactive mode
            cmd = args.command[0].lower()
            
            if cmd == "add" and len(args.command) >= 3:
                period = int(args.command[1])
                exec_time = int(args.command[2])
                deadline = int(args.command[3]) if len(args.command) > 3 else None
                client.add_task(period, exec_time, deadline)
                
            elif cmd == "status":
                client.get_status()
                
            elif cmd == "list":
                client.list_tasks()
                
            else:
                print("❌ Usage: add <period> <exec_time> [deadline] | status | list")
                print("   Example: add 4 2     # Task with period=4, execution=2")
                print("   Example: add 6 3 5   # Task with period=6, execution=3, deadline=5")
        
        else:
            # Interactive mode
            print("\nTask Scheduler Client")
            print("Commands:")
            print("  add <period> <exec_time> [deadline]  - Add a new task")
            print("  status                               - Show current status")
            print("  list                                 - List all tasks")
            print("  quit                                 - Exit")
            print("\nExample: add 4 2")
            
            while True:
                try:
                    command = input("\nclient> ").strip().split()
                    
                    if not command:
                        continue
                    
                    cmd = command[0].lower()
                    
                    if cmd == "quit" or cmd == "exit":
                        break
                    elif cmd == "add" and len(command) >= 3:
                        period = int(command[1])
                        exec_time = int(command[2])
                        deadline = int(command[3]) if len(command) > 3 else None
                        client.add_task(period, exec_time, deadline)
                    elif cmd == "status":
                        client.get_status()
                    elif cmd == "list":
                        client.list_tasks()
                    else:
                        print("❌ Invalid command. Use: add <period> <exec_time> [deadline] | status | list | quit")
                        
                except ValueError:
                    print("❌ Invalid numbers. Use integers only.")
                except KeyboardInterrupt:
                    print("\n(Use 'quit' to exit)")
                    
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
