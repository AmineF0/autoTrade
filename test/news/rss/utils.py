import os
from datetime import datetime
import json

def setup_output_directory(directory: str = "output") -> str:
    """Create output directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def get_timestamp_string() -> str:
    """Get current timestamp string for file naming"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def save_json_output(data: str, filename: str, directory: str = "output") -> str:
    """Save JSON output to file"""
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(json.loads(data), f, indent=2, ensure_ascii=False)
    return filepath