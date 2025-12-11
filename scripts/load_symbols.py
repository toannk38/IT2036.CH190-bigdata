#!/usr/bin/env python3
"""
Script to load stock symbols from JSON file into MongoDB.
Requirements: 2.3
Usage: python scripts/load_symbols.py <json_file_path>

This script:
1. Reads stock symbols from a JSON file
2. Validates the data format
3. Upserts symbols into MongoDB (updates existing, inserts new)
4. Maintains timestamps for tracking changes
"""

import sys
import json
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv
import os
from typing import Dict, List

# Load environment variables
load_dotenv()

# ANSI color codes for terminal output
GREEN = '\033[0;32m'
BLUE = '\033[0;34m'
YELLOW = '\033[1;33m'
RED = '\033[0;31m'
NC = '\033[0m'  # No Color


def validate_symbol_data(symbol_data: Dict) -> bool:
    """
    Validate that symbol data contains required fields.
    
    Args:
        symbol_data: Dictionary containing symbol information
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['symbol', 'organ_name']
    
    for field in required_fields:
        if field not in symbol_data or not symbol_data[field]:
            print(f"{YELLOW}Warning: Missing required field '{field}' in symbol data{NC}")
            return False
    
    return True


def load_symbols_from_json(json_file_path: str) -> int:
    """
    Load symbols from JSON file and upsert to MongoDB.
    
    Args:
        json_file_path: Path to JSON file containing symbol data
        
    Returns:
        Number of symbols successfully loaded
    """
    print(f"{BLUE}=== Stock Symbols Loader ==={NC}")
    print(f"JSON file: {json_file_path}")
    
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    db_name = os.getenv('MONGODB_DATABASE', 'vietnam_stock_ai')
    
    print(f"MongoDB URI: {mongo_uri}")
    print(f"Database: {db_name}")
    print()
    
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Test connection
        client.admin.command('ping')
        print(f"{GREEN}✓ Connected to MongoDB{NC}")
    except ConnectionFailure as e:
        print(f"{RED}Error: Could not connect to MongoDB: {e}{NC}")
        return 0
    
    db = client[db_name]
    symbols_collection = db['symbols']
    
    # Read JSON file
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            symbols_data = json.load(f)
        print(f"{GREEN}✓ Loaded JSON file ({len(symbols_data)} symbols){NC}")
    except FileNotFoundError:
        print(f"{RED}Error: File not found: {json_file_path}{NC}")
        client.close()
        return 0
    except json.JSONDecodeError as e:
        print(f"{RED}Error: Invalid JSON format: {e}{NC}")
        client.close()
        return 0
    
    # Validate data format
    if not isinstance(symbols_data, list):
        print(f"{RED}Error: JSON file must contain an array of symbols{NC}")
        client.close()
        return 0
    
    # Process and upsert symbols
    print()
    print(f"{BLUE}Processing symbols...{NC}")
    
    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    now = datetime.utcnow()
    
    for i, symbol_data in enumerate(symbols_data, 1):
        # Validate symbol data
        if not validate_symbol_data(symbol_data):
            print(f"Skipping invalid symbol at index {i}")
            skipped_count += 1
            continue
        
        # Add timestamps
        symbol_data['updated_at'] = now
        
        # Set active flag if not present
        if 'active' not in symbol_data:
            symbol_data['active'] = True
        
        try:
            # Check if symbol exists
            existing = symbols_collection.find_one({'symbol': symbol_data['symbol']})
            
            if existing:
                # Preserve original created_at
                symbol_data['created_at'] = existing.get('created_at', now)
            else:
                # New symbol
                symbol_data['created_at'] = now
            
            # Upsert symbol
            result = symbols_collection.update_one(
                {'symbol': symbol_data['symbol']},
                {'$set': symbol_data},
                upsert=True
            )
            
            if result.upserted_id:
                inserted_count += 1
                print(f"  {GREEN}✓{NC} Inserted: {symbol_data['symbol']} - {symbol_data['organ_name']}")
            elif result.modified_count > 0:
                updated_count += 1
                print(f"  {BLUE}↻{NC} Updated: {symbol_data['symbol']} - {symbol_data['organ_name']}")
            else:
                print(f"  {YELLOW}={NC} No change: {symbol_data['symbol']}")
                
        except OperationFailure as e:
            print(f"{RED}Error processing symbol {symbol_data.get('symbol', 'unknown')}: {e}{NC}")
            skipped_count += 1
    
    # Summary
    print()
    print(f"{BLUE}=== Summary ==={NC}")
    print(f"Total symbols in file: {len(symbols_data)}")
    print(f"{GREEN}Inserted: {inserted_count}{NC}")
    print(f"{BLUE}Updated: {updated_count}{NC}")
    print(f"{YELLOW}Skipped: {skipped_count}{NC}")
    print()
    
    # Verify database state
    total_in_db = symbols_collection.count_documents({})
    active_in_db = symbols_collection.count_documents({'active': True})
    print(f"Total symbols in database: {total_in_db}")
    print(f"Active symbols in database: {active_in_db}")
    
    client.close()
    print()
    print(f"{GREEN}✓ Symbol loading completed successfully!{NC}")
    
    return inserted_count + updated_count


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"{YELLOW}Usage: python scripts/load_symbols.py <json_file_path>{NC}")
        print()
        print("Example:")
        print("  python scripts/load_symbols.py data/vn30.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    count = load_symbols_from_json(json_file)
    
    sys.exit(0 if count > 0 else 1)
