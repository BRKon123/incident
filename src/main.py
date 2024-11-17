import argparse
import json
from models import Schedule, Overrides
from parser_factory import ParserFactory
from scheduler import BasicScheduleCreator
from utils.datetime_utils import DateTimeEncoder, parse_datetime
import sys

def main():
    # Set up argument parser with help when --help flag used
    parser = argparse.ArgumentParser(description='Render on-call schedule with overrides')
    parser.add_argument('--schedule', required=True, help='Path to schedule JSON/CSV file')
    parser.add_argument('--overrides', required=True, help='Path to overrides JSON/CSV file')
    parser.add_argument('--from', dest='from_time', required=True, help='Start time in ISO format')
    parser.add_argument('--until', required=True, help='End time in ISO format')
    parser.add_argument(
        '--output',
        default='output.json',
        help='Path to output JSON file (default: output.json)'
    )
    
    args = parser.parse_args()
    
    try:
        # Parse input files
        schedule_parser = ParserFactory.create_parser(
            args.schedule, 
            Schedule,
        )
        
        overrides_parser = ParserFactory.create_parser(
            args.overrides, 
            Overrides,
        )
        
        # Parse datetime strings
        from_time = parse_datetime(args.from_time)
        until_time = parse_datetime(args.until)
        
        # Create schedule
        scheduler = BasicScheduleCreator()
        schedule_entries = scheduler.create_schedule(
            schedule_parser.data,
            overrides_parser.data,
            from_time,
            until_time
        )
        
        # Convert to list of dicts for JSON serialization
        entries_dict = [entry.model_dump() for entry in schedule_entries]
        
        # Write JSON to output file
        with open(args.output, 'w') as f:
            json.dump(entries_dict, f, cls=DateTimeEncoder, indent=2)
        
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
