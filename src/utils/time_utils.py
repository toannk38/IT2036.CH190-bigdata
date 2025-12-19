"""
Time utilities for converting between ISO format and epoch timestamps.
"""

from datetime import datetime
from typing import Union, Optional
import time


def iso_to_epoch(iso_string: str) -> float:
    """
    Convert ISO format string to epoch timestamp.
    
    Args:
        iso_string: ISO format timestamp string (e.g., '2025-12-19T02:35:59.585701')
        
    Returns:
        Epoch timestamp as float
    """
    try:
        # Handle various ISO formats
        if iso_string.endswith('Z'):
            # UTC timezone indicator
            dt = datetime.fromisoformat(iso_string[:-1])
        elif '+' in iso_string or iso_string.count('-') > 2:
            # Has timezone info
            dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        else:
            # No timezone info, assume UTC
            dt = datetime.fromisoformat(iso_string)
        
        return dt.timestamp()
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Invalid ISO format: {iso_string}") from e


def epoch_to_iso(epoch_timestamp: Union[int, float]) -> str:
    """
    Convert epoch timestamp to ISO format string.
    
    Args:
        epoch_timestamp: Epoch timestamp (int or float)
        
    Returns:
        ISO format timestamp string
    """
    try:
        dt = datetime.fromtimestamp(epoch_timestamp)
        return dt.isoformat()
    except (ValueError, OSError) as e:
        raise ValueError(f"Invalid epoch timestamp: {epoch_timestamp}") from e


def current_epoch() -> float:
    """
    Get current time as epoch timestamp.
    
    Returns:
        Current epoch timestamp as float
    """
    return time.time()


def current_iso() -> str:
    """
    Get current time as ISO format string.
    
    Returns:
        Current ISO format timestamp string
    """
    return datetime.utcnow().isoformat()


def validate_epoch(timestamp: Union[int, float]) -> bool:
    """
    Validate if a timestamp is a reasonable epoch timestamp.
    
    Args:
        timestamp: Timestamp to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        # Check if it's a reasonable timestamp (between 2000 and 2100)
        min_epoch = datetime(2000, 1, 1).timestamp()
        max_epoch = datetime(2100, 1, 1).timestamp()
        
        return min_epoch <= float(timestamp) <= max_epoch
    except (ValueError, TypeError):
        return False


def safe_convert_to_epoch(value: Union[str, int, float, None]) -> Optional[float]:
    """
    Safely convert various timestamp formats to epoch.
    
    Args:
        value: Timestamp value (ISO string, epoch number, or None)
        
    Returns:
        Epoch timestamp as float, or None if conversion fails
    """
    if value is None:
        return None
    
    # If already a number, validate and return
    if isinstance(value, (int, float)):
        if validate_epoch(value):
            return float(value)
        else:
            return None
    
    # If string, try to convert from ISO
    if isinstance(value, str):
        try:
            return iso_to_epoch(value)
        except ValueError:
            return None
    
    return None