#!/usr/bin/env python3
"""
Test script for the new /symbols API endpoint.
Tests the active symbols endpoint functionality.
"""

import requests
import json
import sys
from typing import Dict, Any

def test_symbols_endpoint(base_url: str = "http://localhost:8000") -> bool:
    """
    Test the /symbols endpoint.
    
    Args:
        base_url: Base URL of the API service
        
    Returns:
        True if test passes, False otherwise
    """
    print("Testing /symbols endpoint...")
    
    try:
        # Test symbols endpoint
        response = requests.get(f"{base_url}/symbols", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Failed: Expected status 200, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        # Parse response
        data = response.json()
        
        # Validate response structure
        required_fields = ['symbols', 'total', 'active_count']
        for field in required_fields:
            if field not in data:
                print(f"❌ Failed: Missing required field '{field}' in response")
                return False
        
        # Validate symbols array
        symbols = data['symbols']
        if not isinstance(symbols, list):
            print("❌ Failed: 'symbols' should be a list")
            return False
        
        print(f"✅ Found {len(symbols)} active symbols out of {data['total']} total")
        print(f"✅ Active count: {data['active_count']}")
        
        # Validate individual symbol structure
        if symbols:
            first_symbol = symbols[0]
            symbol_required_fields = ['symbol', 'organ_name', 'active']
            
            for field in symbol_required_fields:
                if field not in first_symbol:
                    print(f"❌ Failed: Missing required field '{field}' in symbol data")
                    return False
            
            print(f"✅ Sample symbol: {first_symbol['symbol']} - {first_symbol['organ_name']}")
            
            # Check if symbols are sorted
            symbol_codes = [s['symbol'] for s in symbols]
            if symbol_codes == sorted(symbol_codes):
                print("✅ Symbols are properly sorted alphabetically")
            else:
                print("⚠️  Warning: Symbols may not be sorted alphabetically")
        
        # Pretty print first few symbols for verification
        print("\n📋 First 5 symbols:")
        for i, symbol in enumerate(symbols[:5]):
            print(f"  {i+1}. {symbol['symbol']} - {symbol['organ_name']}")
            if symbol.get('icb_name3'):
                print(f"     Industry: {symbol['icb_name3']}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed: Request error - {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Failed: Invalid JSON response - {e}")
        return False
    except Exception as e:
        print(f"❌ Failed: Unexpected error - {e}")
        return False


def test_health_endpoint(base_url: str = "http://localhost:8000") -> bool:
    """
    Test the /health endpoint to ensure API is running.
    
    Args:
        base_url: Base URL of the API service
        
    Returns:
        True if healthy, False otherwise
    """
    print("Testing API health...")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print("✅ API is healthy")
                return True
            else:
                print(f"⚠️  API status: {data.get('status')}")
                return False
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API: {e}")
        return False


def main():
    """Main test function."""
    print("🧪 Testing Vietnam Stock AI - Symbols API Endpoint")
    print("=" * 50)
    
    # Test health first
    if not test_health_endpoint():
        print("\n❌ API is not available. Make sure the API service is running.")
        print("   Start with: uvicorn src.services.api_service:app --host 0.0.0.0 --port 8000")
        sys.exit(1)
    
    print()
    
    # Test symbols endpoint
    if test_symbols_endpoint():
        print("\n🎉 All tests passed! The /symbols endpoint is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed. Check the API implementation.")
        sys.exit(1)


if __name__ == "__main__":
    main()