#!/usr/bin/env python3
"""
Price Data Initialization Script

This script initializes the database with historical price data for the recent year
using 1-minute intervals for all active symbols in the VN30 index.

Usage:
    python scripts/init_price_data.py [--symbols SYMBOL1,SYMBOL2] [--days DAYS] [--interval INTERVAL]

Examples:
    # Initialize all VN30 symbols for the past year with 1-minute data
    python scripts/init_price_data.py

    # Initialize specific symbols for the past 30 days
    python scripts/init_price_data.py --symbols VNM,VIC,HPG --days 30

    # Initialize with 5-minute intervals
    python scripts/init_price_data.py --interval 5m
"""

import sys
import os
import argparse
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import PyMongoError

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import config
from src.logging_config import get_logger
from src.services.symbol_manager import SymbolManager

logger = get_logger(__name__)


class PriceDataInitializer:
    """
    Initializes historical price data for stock symbols.
    
    This class handles bulk initialization of price data by:
    - Fetching historical data from vnstock
    - Processing data in batches
    - Storing directly to MongoDB
    - Handling errors and retries
    """
    
    def __init__(self, mongo_uri: str, database_name: str):
        """
        Initialize the price data initializer.
        
        Args:
            mongo_uri: MongoDB connection URI
            database_name: Name of the database
        """
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client[database_name]
        self.price_collection = self.db['price_data']
        self.symbol_manager = SymbolManager(self.mongo_client, database_name)
        
        # Create indexes for efficient querying
        self._create_indexes()
        
        logger.info(f"PriceDataInitializer initialized with database: {database_name}")
    
    def _create_indexes(self):
        """Create indexes for the price_data collection."""
        try:
            # Compound index on symbol and timestamp for efficient queries
            self.price_collection.create_index([("symbol", 1), ("timestamp", 1)], unique=True)
            # Index on timestamp for time-based queries
            self.price_collection.create_index("timestamp")
            # Index on symbol for symbol-based queries
            self.price_collection.create_index("symbol")
            logger.debug("Indexes created for price_data collection")
        except PyMongoError as e:
            logger.warning(f"Failed to create indexes: {e}")
    
    def load_symbols_from_json(self, json_file_path: str = "data/vn30.json") -> int:
        """
        Load symbols from JSON file to database.
        
        Args:
            json_file_path: Path to the JSON file containing symbols
            
        Returns:
            Number of symbols loaded
        """
        try:
            return self.symbol_manager.load_symbols_from_json(json_file_path)
        except Exception as e:
            logger.error(f"Failed to load symbols from {json_file_path}: {e}")
            raise
    
    def get_symbols_to_initialize(self, symbol_list: Optional[List[str]] = None) -> List[str]:
        """
        Get list of symbols to initialize data for.
        
        Args:
            symbol_list: Optional list of specific symbols. If None, uses all active symbols.
            
        Returns:
            List of symbol codes
        """
        if symbol_list:
            # Validate that symbols exist in database
            all_symbols = self.symbol_manager.get_active_symbols()
            valid_symbols = [s for s in symbol_list if s in all_symbols]
            
            if len(valid_symbols) != len(symbol_list):
                invalid = set(symbol_list) - set(valid_symbols)
                logger.warning(f"Invalid symbols will be skipped: {invalid}")
            
            return valid_symbols
        else:
            return self.symbol_manager.get_active_symbols()
    
    def fetch_historical_data(
        self, 
        symbol: str, 
        start_date: datetime, 
        end_date: datetime,
        interval: str = "1m"
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical price data for a symbol.
        
        Args:
            symbol: Stock symbol code
            start_date: Start date for data collection
            end_date: End date for data collection
            interval: Data interval (1m, 5m, 15m, 30m, 1h, 1d)
            
        Returns:
            DataFrame with price data or None if failed
        """
        try:
            from vnstock import Quote
            
            logger.debug(f"Fetching {interval} data for {symbol} from {start_date.date()} to {end_date.date()}")
            
            # Create Quote instance
            quote = Quote(symbol=symbol, source='VCI')
            
            # Format dates for vnstock
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            # Fetch historical data
            df = quote.history(start=start_str, end=end_str, interval=interval)
            
            if df is None or df.empty:
                logger.warning(f"No data returned for {symbol} in period {start_str} to {end_str}")
                return None
            
            # Add symbol column
            df['symbol'] = symbol
            
            # Ensure timestamp is datetime
            if 'time' in df.columns:
                df['timestamp'] = pd.to_datetime(df['time'])
            else:
                df['timestamp'] = df.index
            
            # Select and rename columns to match our schema
            required_columns = ['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume']
            
            # Check if all required columns exist
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"Missing columns for {symbol}: {missing_columns}")
                return None
            
            # Select only required columns
            df = df[required_columns].copy()
            
            # Convert timestamp to ISO format string for MongoDB
            df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            # Ensure numeric columns are proper types
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Remove rows with NaN values
            df = df.dropna()
            
            logger.info(f"Fetched {len(df)} records for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}", exc_info=True)
            return None
    
    def store_price_data(self, df: pd.DataFrame, symbol: str) -> int:
        """
        Store price data to MongoDB.
        
        Args:
            df: DataFrame containing price data
            symbol: Stock symbol code
            
        Returns:
            Number of records inserted
        """
        if df is None or df.empty:
            return 0
        
        try:
            # Convert DataFrame to list of dictionaries
            records = df.to_dict('records')
            
            # Insert records with upsert to handle duplicates
            inserted_count = 0
            for record in records:
                try:
                    result = self.price_collection.update_one(
                        {
                            'symbol': record['symbol'],
                            'timestamp': record['timestamp']
                        },
                        {'$set': record},
                        upsert=True
                    )
                    
                    if result.upserted_id or result.modified_count > 0:
                        inserted_count += 1
                        
                except PyMongoError as e:
                    logger.error(f"Failed to insert record for {symbol}: {e}")
                    continue
            
            logger.info(f"Stored {inserted_count} records for {symbol}")
            return inserted_count
            
        except Exception as e:
            logger.error(f"Error storing data for {symbol}: {e}", exc_info=True)
            return 0
    
    def initialize_symbol_data(
        self,
        symbol: str,
        days: int = 365,
        interval: str = "1m",
        batch_days: int = 100
    ) -> Dict[str, int]:
        """
        Initialize historical data for a single symbol.
        
        Args:
            symbol: Stock symbol code
            days: Number of days to go back
            interval: Data interval
            batch_days: Number of days to process in each batch
            
        Returns:
            Dictionary with statistics
        """
        logger.info(f"Initializing {days} days of {interval} data for {symbol}")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        total_inserted = 0
        total_batches = 0
        failed_batches = 0
        
        # Process data in batches to avoid memory issues and API limits
        current_start = start_date
        
        while current_start < end_date:
            current_end = min(current_start + timedelta(days=batch_days), end_date)
            
            logger.debug(f"Processing batch for {symbol}: {current_start.date()} to {current_end.date()}")
            
            # Fetch data for this batch
            df = self.fetch_historical_data(symbol, current_start, current_end, interval)
            
            if df is not None and not df.empty:
                # Store data
                inserted = self.store_price_data(df, symbol)
                total_inserted += inserted
            else:
                failed_batches += 1
                logger.warning(f"Failed to fetch data for {symbol} batch {current_start.date()}")
            
            total_batches += 1
            current_start = current_end
            
            # Small delay to avoid overwhelming the API
            import time
            time.sleep(0.5)
        
        result = {
            'symbol': symbol,
            'total_inserted': total_inserted,
            'total_batches': total_batches,
            'failed_batches': failed_batches,
            'success_rate': (total_batches - failed_batches) / total_batches if total_batches > 0 else 0
        }
        
        logger.info(f"Completed {symbol}: {total_inserted} records inserted, {failed_batches}/{total_batches} batches failed")
        return result
    
    def initialize_all_symbols(
        self,
        symbols: List[str],
        days: int = 365,
        interval: str = "1m"
    ) -> Dict[str, any]:
        """
        Initialize historical data for all specified symbols.
        
        Args:
            symbols: List of symbol codes
            days: Number of days to go back
            interval: Data interval
            
        Returns:
            Summary statistics
        """
        logger.info(f"Starting initialization for {len(symbols)} symbols")
        
        results = []
        total_records = 0
        successful_symbols = 0
        
        for i, symbol in enumerate(symbols, 1):
            logger.info(f"Processing symbol {i}/{len(symbols)}: {symbol}")
            
            try:
                result = self.initialize_symbol_data(symbol, days, interval)
                results.append(result)
                
                total_records += result['total_inserted']
                if result['total_inserted'] > 0:
                    successful_symbols += 1
                    
            except Exception as e:
                logger.error(f"Failed to initialize {symbol}: {e}", exc_info=True)
                results.append({
                    'symbol': symbol,
                    'total_inserted': 0,
                    'total_batches': 0,
                    'failed_batches': 0,
                    'success_rate': 0,
                    'error': str(e)
                })
        
        summary = {
            'total_symbols': len(symbols),
            'successful_symbols': successful_symbols,
            'total_records': total_records,
            'results': results,
            'completion_time': datetime.now().isoformat()
        }
        
        logger.info(f"Initialization completed: {successful_symbols}/{len(symbols)} symbols successful, {total_records} total records")
        return summary
    
    def close(self):
        """Close database connection."""
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("Database connection closed")


def main():
    """Main function to run the price data initialization."""
    parser = argparse.ArgumentParser(description='Initialize historical price data')
    parser.add_argument(
        '--symbols',
        type=str,
        help='Comma-separated list of symbols (e.g., VNM,VIC,HPG). If not provided, uses all active symbols.'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=365,
        help='Number of days to go back (default: 365)'
    )
    parser.add_argument(
        '--interval',
        type=str,
        default='1m',
        choices=['1m', '5m', '15m', '30m', '1h', '1d'],
        help='Data interval (default: 1m)'
    )
    parser.add_argument(
        '--load-symbols',
        action='store_true',
        help='Load symbols from VN30 JSON file before initialization'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file to save initialization results (JSON format)'
    )
    
    args = parser.parse_args()
    
    # Initialize the price data initializer
    initializer = None
    
    try:
        logger.info("Starting price data initialization")
        logger.info(f"Configuration: MongoDB URI={config.MONGODB_URI}, Database={config.MONGODB_DATABASE}")
        
        initializer = PriceDataInitializer(config.MONGODB_URI, config.MONGODB_DATABASE)
        
        # Load symbols if requested
        if args.load_symbols:
            logger.info("Loading symbols from VN30 JSON file")
            count = initializer.load_symbols_from_json()
            logger.info(f"Loaded {count} symbols")
        
        # Get symbols to process
        symbol_list = None
        if args.symbols:
            symbol_list = [s.strip().upper() for s in args.symbols.split(',')]
            logger.info(f"Processing specific symbols: {symbol_list}")
        
        symbols = initializer.get_symbols_to_initialize(symbol_list)
        
        if not symbols:
            logger.error("No symbols found to process")
            return 1
        
        logger.info(f"Will process {len(symbols)} symbols: {symbols}")
        
        # Confirm before proceeding with large operations
        if args.days > 30 or len(symbols) > 5:
            response = input(f"This will initialize {args.days} days of {args.interval} data for {len(symbols)} symbols. Continue? (y/N): ")
            if response.lower() != 'y':
                logger.info("Operation cancelled by user")
                return 0
        
        # Initialize data
        summary = initializer.initialize_all_symbols(symbols, args.days, args.interval)
        
        # Print summary
        print("\n" + "="*60)
        print("INITIALIZATION SUMMARY")
        print("="*60)
        print(f"Total symbols processed: {summary['total_symbols']}")
        print(f"Successful symbols: {summary['successful_symbols']}")
        print(f"Total records inserted: {summary['total_records']}")
        print(f"Completion time: {summary['completion_time']}")
        
        # Print per-symbol results
        print("\nPer-symbol results:")
        for result in summary['results']:
            status = "✓" if result['total_inserted'] > 0 else "✗"
            print(f"  {status} {result['symbol']}: {result['total_inserted']} records")
            if 'error' in result:
                print(f"    Error: {result['error']}")
        
        # Save results to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(summary, f, indent=2)
            logger.info(f"Results saved to {args.output}")
        
        return 0 if summary['successful_symbols'] > 0 else 1
        
    except KeyboardInterrupt:
        logger.info("Operation interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Initialization failed: {e}", exc_info=True)
        return 1
    finally:
        if initializer:
            initializer.close()


if __name__ == "__main__":
    exit(main())