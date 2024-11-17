from datetime import datetime
import json

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        return super().default(obj)

def parse_datetime(dt_str: str) -> datetime:
    """Convert ISO format datetime string to datetime object."""
    return datetime.fromisoformat(dt_str.replace('Z', '+00:00')) 