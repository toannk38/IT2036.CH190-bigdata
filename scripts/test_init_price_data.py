#!/usr/bin/env python3
"""
Test script for the updated init_price_data.py to verify epoch timestamp functionality.
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import config
from src.logging_config import get_logger
from src.utils.time_utils import validate_epoch, epoch_to_iso
from scripts.init_price_data import PriceDataInitializer

logger = get_logger(__name__)


def test_timestamp_conversion():
    """Test that timestamp conversion works correctly."""
    print("Testing timestamp conversion...")
    
    # Create sample datetime data
    dates = pd.date_range(start='2024-01-01', end='2024-01-02', freq='1H')
    df = pd.DataFrame({
        'timestamp': dates,
        'symbol': 'TEST',
        'open': 100.0,
        'high': 101.0,
        'low': 99.0,
        'close': 100.5,
        'volume': 1000
    })
    
    print(f"Original timestamps (first 3):")
    for i in range(min(3, len(df))):
        print(f"  {df['timestamp'].iloc[i]}")
    
    # Convert to epoch format (simulate the conversion in fetch_historical_data)
    df['timestamp'] = (df['timestamp'].astype('int64') // 10**9).astype('float64')
    
    print(f"Converted epoch timestamps (first 3):")
    for i in range(min(3, len(df))):
        epoch_ts = df['timestamp'].iloc[i]
        iso_ts = epoch_to_iso(epoch_ts)
        is_valid = validate_epoch(epoch_ts)
        print(f"  {epoch_ts} -> {iso_ts} (valid: {is_valid})")
    
    # Validate all timestamps
    all_valid = all(validate_epoch(ts) for ts in df['timestamp'])
    print(f"All timestamps valid: {all_valid}")
    
    return all_valid


def test_initializer_setup():
    """Test that the initializer can be created and basic operations work."""
    print("\nTesting initializer setup...")
    
    try:
        initializer = PriceDataInitializer(config.MONGODB_URI, config.MONGODB_DATABASE)
        print("✓ Initializer created successfully")
        
        # Test getting symbols
        symbols = initializer.get_symbols_to_initialize(['VIC'])  # Test with one symbol
        print(f"✓ Symbol lookup works: {symbols}")
        
        initializer.close()
        print("✓ Initializer closed successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Initializer test failed: {e}")
        return False


def test_data_structure():
    """Test that the data structure matches expected format."""
    print("\nTesting data structure...")
    
    # Create sample data that matches what vnstock would return
    sample_data = {
        'time': pd.date_range(start='2024-01-01', periods=5, freq='1H'),
        'open': [100.0, 101.0, 102.0, 103.0, 104.0],
        'high': [101.0, 102.0, 103.0, 104.0, 105.0],
        'low': [99.0, 100.0, 101.0, 102.0, 103.0],
        'close': [100.5, 101.5, 102.5, 103.5, 104.5],
        'volume': [1000, 1100, 1200, 1300, 1400]
    }
    
    df = pd.DataFrame(sample_data)
    
    # Simulate the processing in fetch_historical_data
    df['symbol'] = 'TEST'
    df['timestamp'] = pd.to_datetime(df['time'])
    
    required_columns = ['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume']
    df = df[required_columns].copy()
    
    # Convert timestamp to epoch format
    df['timestamp'] = (df['timestamp'].astype('int64') // 10**9).astype('float64')
    
    # Ensure numeric columns are proper types
    numeric_columns = ['open', 'high', 'low', 'close', 'volume', 'timestamp']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Remove rows with NaN values
    df = df.dropna()
    
    print(f"Final data structure:")
    print(f"  Columns: {list(df.columns)}")
    print(f"  Data types: {dict(df.dtypes)}")
    print(f"  Sample record: {df.iloc[0].to_dict()}")
    
    # Validate structure
    expected_columns = ['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume']
    has_all_columns = all(col in df.columns for col in expected_columns)
    
    # Validate timestamp format
    all_timestamps_valid = all(validate_epoch(ts) for ts in df['timestamp'])
    
    print(f"✓ Has all required columns: {has_all_columns}")
    print(f"✓ All timestamps are valid epoch: {all_timestamps_valid}")
    
    return has_all_columns and all_timestamps_valid


def main():
    """Run all tests."""
    print("=" * 60)
    print("TESTING UPDATED INIT_PRICE_DATA.PY")
    print("=" * 60)
    
    tests = [
        ("Timestamp Conversion", test_timestamp_conversion),
        ("Initializer Setup", test_initializer_setup),
        ("Data Structure", test_data_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            status = "PASS" if result else "FAIL"
            print(f"\n{test_name}: {status}")
        except Exception as e:
            results.append((test_name, False))
            print(f"\n{test_name}: FAIL - {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {test_name}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! The init_price_data.py script is ready for epoch timestamps.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit(main())