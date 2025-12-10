"""
Symbol Manager Service for managing stock symbols in MongoDB.
Handles loading, querying, and updating stock symbol metadata.
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from src.logging_config import get_logger

logger = get_logger(__name__)


class SymbolManager:
    """
    Manages stock symbols in MongoDB.
    
    Responsibilities:
    - Load symbols from JSON files
    - Query active symbols for data collection
    - Update symbol metadata
    """
    
    def __init__(self, mongo_client: MongoClient, database_name: str = "vietnam_stock_ai"):
        """
        Initialize SymbolManager with MongoDB connection.
        
        Args:
            mongo_client: MongoDB client instance
            database_name: Name of the database to use
        """
        self.client = mongo_client
        self.db = self.client[database_name]
        self.collection = self.db['symbols']
        
        # Create indexes for efficient querying
        self._create_indexes()
        
        logger.info(f"SymbolManager initialized with database: {database_name}")
    
    def _create_indexes(self):
        """Create indexes for the symbols collection."""
        try:
            # Index on symbol for fast lookups
            self.collection.create_index("symbol", unique=True)
            # Index on active flag for filtering
            self.collection.create_index("active")
            logger.debug("Indexes created for symbols collection")
        except PyMongoError as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    def load_symbols_from_json(self, json_file_path: str) -> int:
        """
        Load symbols from JSON file and upsert to MongoDB.
        
        Args:
            json_file_path: Path to JSON file containing symbol data
            
        Returns:
            Number of symbols loaded/updated
            
        Raises:
            FileNotFoundError: If JSON file doesn't exist
            json.JSONDecodeError: If JSON file is invalid
            PyMongoError: If database operation fails
        """
        logger.info(f"Loading symbols from {json_file_path}")
        
        # Read and parse JSON file
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                symbols_data = json.load(f)
        except FileNotFoundError:
            logger.error(f"JSON file not found: {json_file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in {json_file_path}: {e}")
            raise
        
        if not isinstance(symbols_data, list):
            raise ValueError("JSON file must contain a list of symbol objects")
        
        # Process and upsert symbols
        count = 0
        now = datetime.utcnow()
        
        for symbol_data in symbols_data:
            if not isinstance(symbol_data, dict):
                logger.warning(f"Skipping invalid symbol data: {symbol_data}")
                continue
            
            if 'symbol' not in symbol_data:
                logger.warning(f"Skipping symbol data without 'symbol' field: {symbol_data}")
                continue
            
            # Add timestamps
            symbol_data['updated_at'] = now
            
            # Set active flag if not present
            if 'active' not in symbol_data:
                symbol_data['active'] = True
            
            try:
                # Upsert symbol (update if exists, insert if not)
                result = self.collection.update_one(
                    {'symbol': symbol_data['symbol']},
                    {
                        '$set': symbol_data,
                        '$setOnInsert': {'created_at': now}
                    },
                    upsert=True
                )
                
                # Count if inserted, updated, or matched (even if no changes)
                if result.upserted_id or result.modified_count > 0 or result.matched_count > 0:
                    count += 1
                    logger.debug(f"Upserted symbol: {symbol_data['symbol']}")
                    
            except PyMongoError as e:
                logger.error(f"Failed to upsert symbol {symbol_data.get('symbol')}: {e}")
                raise
        
        logger.info(f"Successfully loaded {count} symbols from {json_file_path}")
        return count
    
    def get_active_symbols(self) -> List[str]:
        """
        Get list of active symbol codes for data collection.
        
        Returns:
            List of symbol codes (e.g., ['VNM', 'VIC', 'HPG'])
        """
        logger.debug("Querying active symbols")
        
        try:
            # Query symbols where active=True
            cursor = self.collection.find(
                {'active': True},
                {'symbol': 1, '_id': 0}
            )
            
            symbols = [doc['symbol'] for doc in cursor]
            logger.info(f"Retrieved {len(symbols)} active symbols")
            return symbols
            
        except PyMongoError as e:
            logger.error(f"Failed to query active symbols: {e}")
            raise
    
    def update_symbol(self, symbol: str, metadata: Dict) -> bool:
        """
        Update symbol metadata.
        
        Args:
            symbol: Symbol code to update
            metadata: Dictionary of fields to update
            
        Returns:
            True if successful, False if symbol not found
            
        Raises:
            PyMongoError: If database operation fails
        """
        logger.debug(f"Updating symbol: {symbol}")
        
        if not metadata:
            logger.warning(f"No metadata provided for symbol {symbol}")
            return False
        
        # Add updated timestamp
        metadata['updated_at'] = datetime.utcnow()
        
        try:
            result = self.collection.update_one(
                {'symbol': symbol},
                {'$set': metadata}
            )
            
            if result.matched_count > 0:
                logger.info(f"Successfully updated symbol: {symbol}")
                return True
            else:
                logger.warning(f"Symbol not found: {symbol}")
                return False
                
        except PyMongoError as e:
            logger.error(f"Failed to update symbol {symbol}: {e}")
            raise
    
    def get_symbol(self, symbol: str) -> Optional[Dict]:
        """
        Get symbol data by symbol code.
        
        Args:
            symbol: Symbol code to retrieve
            
        Returns:
            Symbol document or None if not found
        """
        try:
            return self.collection.find_one({'symbol': symbol})
        except PyMongoError as e:
            logger.error(f"Failed to get symbol {symbol}: {e}")
            raise
    
    def get_all_symbols(self, active_only: bool = False) -> List[Dict]:
        """
        Get all symbols from the database.
        
        Args:
            active_only: If True, only return active symbols
            
        Returns:
            List of symbol documents
        """
        try:
            query = {'active': True} if active_only else {}
            cursor = self.collection.find(query)
            return list(cursor)
        except PyMongoError as e:
            logger.error(f"Failed to get all symbols: {e}")
            raise
