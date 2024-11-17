import argparse
from datetime import datetime
from typing import Dict, List
from models import Schedule, Overrides
from file_parser import JsonParser

def parse_datetime(dt_str: str) -> datetime:
    """Convert ISO format datetime string to datetime object."""
    return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))

def main():
    # Set up argument parser with help when --help flag used
    parser = argparse.ArgumentParser(description='Render on-call schedule with overrides')
    parser.add_argument('--schedule', required=True, help='Path to schedule JSON file')
    parser.add_argument('--overrides', required=True, help='Path to overrides JSON file')
    parser.add_argument('--from', dest='from_time', required=True, help='Start time in ISO format')
    parser.add_argument('--until', required=True, help='End time in ISO format')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Parse files with type validation
    schedule_parser = JsonParser(args.schedule, Schedule)
    overrides_parser = JsonParser(args.overrides, Overrides)
    
    # Access the validated data
    schedule = schedule_parser.data
    overrides = overrides_parser.data
    
    # Now you have fully typed access to your data
    for user in schedule.users:
        print(user)
    
    for override in overrides.overrides:
        print(f"{override.user}: {override.start_at} -> {override.end_at}")

if __name__ == "__main__":
    main()
