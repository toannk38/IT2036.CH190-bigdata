#!/usr/bin/env python3
"""
Price Data Verification Script

This script verifies the initialized price data in the database.
It provides statistics and sample data for verification.

Usage:
    python scripts/verify_price_data.py [--symbol SYMBOL] [--days DAYS]

Examples:
    # Check all symbols
    python scripts/verify_price_data.py

    # Check specific symbol
    python scripts/verify_price_data.py --symbol VNM

    # Check data for last 7 days
    python scripts/verify_price_data.py --days 7
"""

import sys
import os
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pymongo import MongoClient
import pandas as pd

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.config import config
from src.logging_config import get_logger

logger = get_logger(__name__)


class PriceDataVerifier:
    """Verifies and analyzes price data in the database."""
    
    def __init__(self, mongo_uri: str, database_name: str):
        """Initialize the verifier."""
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client[database_name]
        self.price_collection = self.db['price_data']
        self.symbol_collection = self.db['symbols']
        
    def get_data_summary(self) -> Dict:
        """Get overall data summary."""
        try:
            # Total records
            total_records = self.price_collection.count_documents({})
            
            # Unique symbols
            symbols = self.price_collection.distinct('symbol')
            
            # Date range
            oldest = self.price_collection.find().sort('timestamp', 1).limit(1)
            newest = self.price_collection.find().sort('timestamp', -1).limit(1)
            
            oldest_date = None
            newest_date = None
            
            for doc in oldest:
                oldest_date = doc.get('timestamp')
            
            for doc in newest:
                newest_date = doc.get('timestamp')
            
            return {
                'total_records': total_records,
                'unique_symbols': len(symbols),
                'symbols': sorted(symbols),
                'oldest_date': oldest_date,
                'newest_date': newest_date
            }
            
        except Exception as e:
            logger.error(f"Error getting data summary: {e}")
            return {}
    
    def get_symbol_statistics(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get statistics per symbol."""
        try:
            pipeline = []
            
            # Filter by symbol if specified
            if symbol:
                pipeline.append({'$match': {'symbol': symbol}})
            
            # Group by symbol and calculate statistics
            pipeline.extend([
                {
                    '$group': {
                        '_id': '$symbol',
                        'record_count': {'$sum': 1},
                        'min_timestamp': {'$min': '$timestamp'},
                        'max_timestamp': {'$max': '$timestamp'},
                        'avg_volume': {'$avg': '$volume'},
                        'avg_close': {'$avg': '$close'}
                    }
                },
                {
                    '$sort': {'_id': 1}
                }
            ])
            
            results = list(self.price_collection.aggregate(pipeline))
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'symbol': result['_id'],
                    'record_count': result['record_count'],
                    'min_timestamp': result['min_timestamp'],
                    'max_timestamp': result['max_timestamp'],
                    'avg_volume': round(result.get('avg_volume', 0), 2),
                    'avg_close': round(result.get('avg_close', 0), 2)
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error getting symbol statistics: {e}")
            return []
    
    def get_sample_data(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Get sample data for a symbol."""
        try:
            cursor = self.price_collection.find(
                {'symbol': symbol}
            ).sort('timestamp', -1).limit(limit)
            
            return list(cursor)
            
        except Exception as e:
            logger.error(f"Error getting sample data for {symbol}: {e}")
            return []
    
    def check_data_quality(self, symbol: Optional[str] = None) -> Dict:
        """Check data quality issues."""
        try:
            match_filter = {}
            if symbol:
                match_filter['symbol'] = symbol
            
            # Check for missing values
            missing_open = self.price_collection.count_documents({**match_filter, 'open': {'$in': [None, 0]}})
            missing_close = self.price_collection.count_documents({**match_filter, 'close': {'$in': [None, 0]}})
            missing_volume = self.price_collection.count_documents({**match_filter, 'volume': {'$in': [None, 0]}})
            
            # Check for negative values
            negative_prices = self.price_collection.count_documents({
                **match_filter,
                '$or': [
                    {'open': {'$lt': 0}},
                    {'close': {'$lt': 0}},
                    {'high': {'$lt': 0}},
                    {'low': {'$lt': 0}}
                ]
            })
            
            # Check for invalid high/low relationships
            invalid_high_low = self.price_collection.count_documents({
                **match_filter,
                '$expr': {'$gt': ['$low', '$high']}
            })
            
            return {
                'missing_open': missing_open,
                'missing_close': missing_close,
                'missing_volume': missing_volume,
                'negative_prices': negative_prices,
                'invalid_high_low': invalid_high_low
            }
            
        except Exception as e:
            logger.error(f"Error checking data quality: {e}")
            return {}
    
    def get_recent_data_coverage(self, days: int = 7) -> Dict:
        """Check data coverage for recent days."""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Convert to ISO string format
            start_str = start_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            end_str = end_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            
            # Count records per symbol in the date range
            pipeline = [
                {
                    '$match': {
                        'timestamp': {
                            '$gte': start_str,
                            '$lte': end_str
                        }
                    }
                },
                {
                    '$group': {
                        '_id': '$symbol',
                        'record_count': {'$sum': 1},
                        'min_timestamp': {'$min': '$timestamp'},
                        'max_timestamp': {'$max': '$timestamp'}
                    }
                },
                {
                    '$sort': {'record_count': -1}
                }
            ]
            
            results = list(self.price_collection.aggregate(pipeline))
            
            return {
                'date_range': f"{start_date.date()} to {end_date.date()}",
                'symbols_with_data': len(results),
                'coverage_by_symbol': results
            }
            
        except Exception as e:
            logger.error(f"Error checking recent data coverage: {e}")
            return {}
    
    def close(self):
        """Close database connection."""
        if self.mongo_client:
            self.mongo_client.close()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Verify price data in database')
    parser.add_argument(
        '--symbol',
        type=str,
        help='Specific symbol to check'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of recent days to check (default: 7)'
    )
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Show sample data'
    )
    
    args = parser.parse_args()
    
    verifier = None
    
    try:
        print("Price Data Verification Report")
        print("=" * 50)
        
        verifier = PriceDataVerifier(config.MONGODB_URI, config.MONGODB_DATABASE)
        
        # Overall summary
        print("\n1. OVERALL SUMMARY")
        print("-" * 30)
        summary = verifier.get_data_summary()
        if summary:
            print(f"Total records: {summary.get('total_records', 0):,}")
            print(f"Unique symbols: {summary.get('unique_symbols', 0)}")
            print(f"Date range: {summary.get('oldest_date', 'N/A')} to {summary.get('newest_date', 'N/A')}")
            if summary.get('symbols'):
                print(f"Symbols: {', '.join(summary['symbols'])}")
        
        # Symbol statistics
        print(f"\n2. SYMBOL STATISTICS")
        print("-" * 30)
        stats = verifier.get_symbol_statistics(args.symbol)
        if stats:
            print(f"{'Symbol':<8} {'Records':<10} {'Avg Close':<12} {'Avg Volume':<15} {'Date Range'}")
            print("-" * 80)
            for stat in stats:
                date_range = f"{stat['min_timestamp'][:10]} to {stat['max_timestamp'][:10]}"
                print(f"{stat['symbol']:<8} {stat['record_count']:<10,} {stat['avg_close']:<12.2f} {stat['avg_volume']:<15,.0f} {date_range}")
        
        # Data quality check
        print(f"\n3. DATA QUALITY CHECK")
        print("-" * 30)
        quality = verifier.check_data_quality(args.symbol)
        if quality:
            print(f"Missing open prices: {quality.get('missing_open', 0)}")
            print(f"Missing close prices: {quality.get('missing_close', 0)}")
            print(f"Missing volume data: {quality.get('missing_volume', 0)}")
            print(f"Negative prices: {quality.get('negative_prices', 0)}")
            print(f"Invalid high/low: {quality.get('invalid_high_low', 0)}")
        
        # Recent data coverage
        print(f"\n4. RECENT DATA COVERAGE ({args.days} days)")
        print("-" * 30)
        coverage = verifier.get_recent_data_coverage(args.days)
        if coverage:
            print(f"Date range: {coverage.get('date_range', 'N/A')}")
            print(f"Symbols with data: {coverage.get('symbols_with_data', 0)}")
            
            recent_data = coverage.get('coverage_by_symbol', [])
            if recent_data:
                print(f"\nRecent data by symbol:")
                for item in recent_data[:10]:  # Show top 10
                    print(f"  {item['_id']}: {item['record_count']:,} records")
        
        # Sample data
        if args.sample and args.symbol:
            print(f"\n5. SAMPLE DATA FOR {args.symbol}")
            print("-" * 30)
            sample_data = verifier.get_sample_data(args.symbol, 5)
            if sample_data:
                for i, record in enumerate(sample_data, 1):
                    print(f"Record {i}:")
                    print(f"  Timestamp: {record.get('timestamp')}")
                    print(f"  OHLC: {record.get('open'):.2f} / {record.get('high'):.2f} / {record.get('low'):.2f} / {record.get('close'):.2f}")
                    print(f"  Volume: {record.get('volume', 0):,}")
                    print()
        
        print("\nVerification completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Verification failed: {e}", exc_info=True)
        return 1
    finally:
        if verifier:
            verifier.close()


if __name__ == "__main__":
    exit(main())