"""Data loading utilities."""
import json
import pandas as pd
from pathlib import Path


def get_data_path():
    """Get path to data directory."""
    return Path(__file__).parent.parent.parent.parent / "data"


def load_json_file(filename):
    """Load JSON file."""
    file_path = get_data_path() / filename
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_csv_file(filename):
    """Load CSV file."""
    file_path = get_data_path() / filename
    return pd.read_csv(file_path)


def parse_timestamp(timestamp_str):
    """Parse timestamp string to datetime."""
    return pd.to_datetime(timestamp_str)
