#!/usr/bin/env python3
"""
Script to load stock symbols from JSON file into MongoDB.
Usage: python scripts/load_symbols.py <json_file_path>
"""

import sys
import json
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def load_symbols_from_json(json_file_path: str):
    """Load symbols from JSON file and upsert to MongoDB."""
    
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    db_name = os.getenv('MONGODB_DATABASE', 'vietnam_stock_ai')
    
    client = MongoClient(mongo_uri)
    db = client[db_name]
    symbols_collection = db['symbols']
    
    # Read JSON file
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            symbols_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {json_file_path}")
        return 0
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format: {e}")
        return 0
    
    # Process and upsert symbols
    count = 0
    now = datetime.utcnow()
    
    for symbol_data in symbols_data:
        # Add timestamps
        symbol_data['updated_at'] = now
        if 'created_at' not in symbol_data:
            symbol_data['created_at'] = now
        
        # Set active flag if not present
        if 'active' not in symbol_data:
            symbol_data['active'] = True
        
        # Upsert symbol
        result = symbols_collection.update_one(
            {'symbol': symbol_data['symbol']},
            {'$set': symbol_data},
            upsert=True
        )
        
        if result.upserted_id or result.modified_count > 0:
            count += 1
    
    print(f"Successfully loaded {count} symbols into MongoDB")
    client.close()
    return count

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/load_symbols.py <json_file_path>")
        sys.exit(1)
    
    json_file = sys.argv[1]
    load_symbols_from_json(json_file)
