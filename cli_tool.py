#!/usr/bin/env python3
"""
Command Line Interface (CLI) tool example.
This demonstrates how to create CLI applications with Python.
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime
from src.utils.helpers import load_json_file, save_json_file, format_file_size


def create_task(args):
    """Create a new task."""
    task = {
        'id': datetime.now().timestamp(),
        'title': args.title,
        'description': args.description or '',
        'priority': args.priority,
        'status': 'pending',
        'created_at': datetime.now().isoformat(),
        'due_date': args.due_date.isoformat() if args.due_date else None
    }
    
    # Load existing tasks
    tasks_file = Path('tasks.json')
    tasks = load_json_file(str(tasks_file)) if tasks_file.exists() else []
    
    # Add new task
    tasks.append(task)
    
    # Save tasks
    if save_json_file(tasks, str(tasks_file)):
        print(f"✅ Task created: {task['title']}")
    else:
        print("❌ Error saving task")


def list_tasks(args):
    """List all tasks."""
    tasks_file = Path('tasks.json')
    if not tasks_file.exists():
        print("No tasks found. Create your first task!")
        return
    
    tasks = load_json_file(str(tasks_file))
    
    if not tasks:
        print("No tasks found.")
        return
    
    # Filter by status if specified
    if args.status:
        tasks = [t for t in tasks if t['status'] == args.status]
    
    # Sort by priority
    priority_order = {'high': 3, 'medium': 2, 'low': 1}
    tasks.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
    
    print(f"\n📋 Tasks ({len(tasks)} found):")
    print("-" * 60)
    
    for task in tasks:
        status_emoji = {
            'pending': '⏳',
            'in_progress': '🔄',
            'completed': '✅',
            'cancelled': '❌'
        }.get(task['status'], '❓')
        
        priority_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }.get(task['priority'], '⚪')
        
        print(f"{status_emoji} {priority_emoji} {task['title']}")
        if task['description']:
            print(f"   Description: {task['description']}")
        print(f"   Status: {task['status']} | Priority: {task['priority']}")
        print(f"   Created: {task['created_at'][:10]}")
        if task['due_date']:
            print(f"   Due: {task['due_date'][:10]}")
        print()


def update_task(args):
    """Update task status."""
    tasks_file = Path('tasks.json')
    if not tasks_file.exists():
        print("No tasks file found.")
        return
    
    tasks = load_json_file(str(tasks_file))
    task_id = float(args.task_id)
    
    # Find task by ID
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        print(f"Task with ID {args.task_id} not found.")
        return
    
    # Update status
    old_status = task['status']
    task['status'] = args.status
    task['updated_at'] = datetime.now().isoformat()
    
    # Save updated tasks
    if save_json_file(tasks, str(tasks_file)):
        print(f"✅ Task '{task['title']}' status updated: {old_status} → {args.status}")
    else:
        print("❌ Error updating task")


def delete_task(args):
    """Delete a task."""
    tasks_file = Path('tasks.json')
    if not tasks_file.exists():
        print("No tasks file found.")
        return
    
    tasks = load_json_file(str(tasks_file))
    task_id = float(args.task_id)
    
    # Find task by ID
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        print(f"Task with ID {args.task_id} not found.")
        return
    
    # Confirm deletion
    confirm = input(f"Are you sure you want to delete '{task['title']}'? (y/N): ")
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        return
    
    # Remove task
    tasks = [t for t in tasks if t['id'] != task_id]
    
    # Save updated tasks
    if save_json_file(tasks, str(tasks_file)):
        print(f"✅ Task '{task['title']}' deleted successfully")
    else:
        print("❌ Error deleting task")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Task Manager CLI - A simple command-line task management tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli_tool.py create -t "Buy groceries" -d "Milk, bread, eggs" -p high
  python cli_tool.py list
  python cli_tool.py list --status pending
  python cli_tool.py update 1234567890.123 --status completed
  python cli_tool.py delete 1234567890.123
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new task')
    create_parser.add_argument('-t', '--title', required=True, help='Task title')
    create_parser.add_argument('-d', '--description', help='Task description')
    create_parser.add_argument('-p', '--priority', choices=['low', 'medium', 'high'], 
                              default='medium', help='Task priority')
    create_parser.add_argument('--due-date', type=datetime.fromisoformat, help='Due date (YYYY-MM-DD)')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all tasks')
    list_parser.add_argument('--status', choices=['pending', 'in_progress', 'completed', 'cancelled'],
                            help='Filter by status')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update task status')
    update_parser.add_argument('task_id', help='Task ID to update')
    update_parser.add_argument('--status', required=True, 
                              choices=['pending', 'in_progress', 'completed', 'cancelled'],
                              help='New status')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('task_id', help='Task ID to delete')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    if args.command == 'create':
        create_task(args)
    elif args.command == 'list':
        list_tasks(args)
    elif args.command == 'update':
        update_task(args)
    elif args.command == 'delete':
        delete_task(args)


if __name__ == '__main__':
    main()
