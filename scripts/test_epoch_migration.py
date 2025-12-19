#!/usr/bin/env python3
"""
Test script to verify epoch timestamp migration is working correctly.
Tests all components: collectors, consumers, engines, and API.
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import get_config
from src.logging_config import get_logger
from src.utils.time_utils import (
    current_epoch, epoch_to_iso, iso_to_epoch, 
    validate_epoch, safe_convert_to_epoch
)
from pymongo import MongoClient

logger = get_logger(__name__)


class EpochMigrationTester:
    """Test epoch timestamp migration across all components."""
    
    def __init__(self, mongo_client: MongoClient, database_name: str = 'vietnam_stock_ai'):
        """Initialize the tester."""
        self.client = mongo_client
        self.db = mongo_client[database_name]
        self.database_name = database_name
        
        logger.info(f"EpochMigrationTester initialized for database: {database_name}")
    
    def test_time_utils(self) -> Dict[str, Any]:
        """Test time utility functions."""
        logger.info("Testing time utility functions")
        
        results = {
            'passed': 0,
            'failed': 0,
            'tests': []
        }
        
        # Test current_epoch
        try:
            epoch_now = current_epoch()
            assert isinstance(epoch_now, float)
            assert validate_epoch(epoch_now)
            results['tests'].append({'test': 'current_epoch', 'status': 'PASS'})
            results['passed'] += 1
        except Exception as e:
            results['tests'].append({'test': 'current_epoch', 'status': 'FAIL', 'error': str(e)})
            results['failed'] += 1
        
        # Test ISO to epoch conversion
        try:
            iso_str = "2025-12-19T02:35:59.585701"
            epoch_val = iso_to_epoch(iso_str)
            assert isinstance(epoch_val, float)
            assert validate_epoch(epoch_val)
            results['tests'].append({'test': 'iso_to_epoch', 'status': 'PASS'})
            results['passed'] += 1
        except Exception as e:
            results['tests'].append({'test': 'iso_to_epoch', 'status': 'FAIL', 'error': str(e)})
            results['failed'] += 1
        
        # Test epoch to ISO conversion
        try:
            epoch_val = time.time()
            iso_str = epoch_to_iso(epoch_val)
            assert isinstance(iso_str, str)
            assert 'T' in iso_str  # Should be ISO format
            results['tests'].append({'test': 'epoch_to_iso', 'status': 'PASS'})
            results['passed'] += 1
        except Exception as e:
            results['tests'].append({'test': 'epoch_to_iso', 'status': 'FAIL', 'error': str(e)})
            results['failed'] += 1
        
        # Test safe conversion
        try:
            # Test with ISO string
            iso_str = "2025-12-19T02:35:59.585701"
            epoch_val = safe_convert_to_epoch(iso_str)
            assert epoch_val is not None
            assert validate_epoch(epoch_val)
            
            # Test with epoch number
            epoch_input = time.time()
            epoch_output = safe_convert_to_epoch(epoch_input)
            assert epoch_output == epoch_input
            
            # Test with None
            none_output = safe_convert_to_epoch(None)
            assert none_output is None
            
            results['tests'].append({'test': 'safe_convert_to_epoch', 'status': 'PASS'})
            results['passed'] += 1
        except Exception as e:
            results['tests'].append({'test': 'safe_convert_to_epoch', 'status': 'FAIL', 'error': str(e)})
            results['failed'] += 1
        
        return results
    
    def test_data_formats(self) -> Dict[str, Any]:
        """Test data formats in MongoDB collections."""
        logger.info("Testing data formats in MongoDB collections")
        
        results = {
            'collections': {},
            'total_epoch_timestamps': 0,
            'total_iso_timestamps': 0,
            'total_invalid_timestamps': 0
        }
        
        collections_to_check = {
            'price_history': ['timestamp', 'created_at'],
            'news': ['published_at', 'collected_at', 'created_at'],
            'ai_analysis': ['timestamp'],
            'llm_analysis': ['timestamp'],
            'final_scores': ['timestamp']
        }
        
        for collection_name, timestamp_fields in collections_to_check.items():
            collection = self.db[collection_name]
            collection_result = {
                'document_count': 0,
                'fields': {},
                'sample_documents': []
            }
            
            # Get document count
            collection_result['document_count'] = collection.count_documents({})
            
            # Check timestamp formats for each field
            for field in timestamp_fields:
                field_result = {
                    'epoch_count': 0,
                    'iso_count': 0,
                    'invalid_count': 0,
                    'samples': []
                }
                
                # Sample some documents to check formats
                sample_docs = list(collection.find({field: {'$exists': True}}).limit(10))
                
                for doc in sample_docs:
                    if field in doc:
                        value = doc[field]
                        
                        if isinstance(value, (int, float)):
                            if validate_epoch(value):
                                field_result['epoch_count'] += 1
                                field_result['samples'].append({
                                    'type': 'epoch',
                                    'value': value,
                                    'iso_equivalent': epoch_to_iso(value)
                                })
                            else:
                                field_result['invalid_count'] += 1
                                field_result['samples'].append({
                                    'type': 'invalid_epoch',
                                    'value': value
                                })
                        elif isinstance(value, str):
                            if safe_convert_to_epoch(value) is not None:
                                field_result['iso_count'] += 1
                                field_result['samples'].append({
                                    'type': 'iso',
                                    'value': value,
                                    'epoch_equivalent': safe_convert_to_epoch(value)
                                })
                            else:
                                field_result['invalid_count'] += 1
                                field_result['samples'].append({
                                    'type': 'invalid_iso',
                                    'value': value
                                })
                        else:
                            field_result['invalid_count'] += 1
                            field_result['samples'].append({
                                'type': 'unknown',
                                'value': value
                            })
                
                collection_result['fields'][field] = field_result
                results['total_epoch_timestamps'] += field_result['epoch_count']
                results['total_iso_timestamps'] += field_result['iso_count']
                results['total_invalid_timestamps'] += field_result['invalid_count']
            
            results['collections'][collection_name] = collection_result
        
        return results
    
    def test_collector_data_structures(self) -> Dict[str, Any]:
        """Test that collector data structures use epoch timestamps."""
        logger.info("Testing collector data structures")
        
        results = {
            'passed': 0,
            'failed': 0,
            'tests': []
        }
        
        try:
            # Test PriceData structure
            from src.collectors.price_collector import PriceData
            
            price_data = PriceData(
                symbol='TEST',
                timestamp=current_epoch(),
                open=100.0,
                close=101.0,
                high=102.0,
                low=99.0,
                volume=1000
            )
            
            # Check that timestamp is float (epoch)
            assert isinstance(price_data.timestamp, float)
            assert validate_epoch(price_data.timestamp)
            
            results['tests'].append({'test': 'PriceData_structure', 'status': 'PASS'})
            results['passed'] += 1
            
        except Exception as e:
            results['tests'].append({'test': 'PriceData_structure', 'status': 'FAIL', 'error': str(e)})
            results['failed'] += 1
        
        try:
            # Test NewsData structure
            from src.collectors.news_collector import NewsData
            
            news_data = NewsData(
                symbol='TEST',
                title='Test News',
                content='Test content',
                source='test.com',
                published_at=current_epoch(),
                collected_at=current_epoch()
            )
            
            # Check that timestamps are float (epoch)
            assert isinstance(news_data.published_at, float)
            assert isinstance(news_data.collected_at, float)
            assert validate_epoch(news_data.published_at)
            assert validate_epoch(news_data.collected_at)
            
            results['tests'].append({'test': 'NewsData_structure', 'status': 'PASS'})
            results['passed'] += 1
            
        except Exception as e:
            results['tests'].append({'test': 'NewsData_structure', 'status': 'FAIL', 'error': str(e)})
            results['failed'] += 1
        
        return results
    
    def test_engine_data_structures(self) -> Dict[str, Any]:
        """Test that engine data structures use epoch timestamps."""
        logger.info("Testing engine data structures")
        
        results = {
            'passed': 0,
            'failed': 0,
            'tests': []
        }
        
        try:
            # Test AnalysisResult structure
            from src.engines.aiml_engine import AnalysisResult, TrendPrediction
            
            trend = TrendPrediction(direction='up', confidence=0.8, predicted_price=100.0)
            analysis_result = AnalysisResult(
                symbol='TEST',
                timestamp=current_epoch(),
                trend_prediction=trend,
                risk_score=0.3,
                technical_score=0.7,
                indicators={'rsi': 65.0}
            )
            
            # Check that timestamp is float (epoch)
            assert isinstance(analysis_result.timestamp, float)
            assert validate_epoch(analysis_result.timestamp)
            
            results['tests'].append({'test': 'AnalysisResult_structure', 'status': 'PASS'})
            results['passed'] += 1
            
        except Exception as e:
            results['tests'].append({'test': 'AnalysisResult_structure', 'status': 'FAIL', 'error': str(e)})
            results['failed'] += 1
        
        try:
            # Test NewsAnalysisResult structure
            from src.engines.llm_engine import NewsAnalysisResult, SentimentResult
            
            sentiment = SentimentResult(sentiment='positive', score=0.6, confidence=0.8)
            news_analysis = NewsAnalysisResult(
                symbol='TEST',
                timestamp=current_epoch(),
                sentiment=sentiment,
                summary='Test summary',
                influence_score=0.7,
                articles_analyzed=5
            )
            
            # Check that timestamp is float (epoch)
            assert isinstance(news_analysis.timestamp, float)
            assert validate_epoch(news_analysis.timestamp)
            
            results['tests'].append({'test': 'NewsAnalysisResult_structure', 'status': 'PASS'})
            results['passed'] += 1
            
        except Exception as e:
            results['tests'].append({'test': 'NewsAnalysisResult_structure', 'status': 'FAIL', 'error': str(e)})
            results['failed'] += 1
        
        return results
    
    def test_api_responses(self) -> Dict[str, Any]:
        """Test that API responses convert epoch to ISO format."""
        logger.info("Testing API response formatting")
        
        results = {
            'passed': 0,
            'failed': 0,
            'tests': []
        }
        
        try:
            from src.services.api_service import APIService
            
            # Create API service instance
            api_service = APIService(self.client, self.database_name)
            
            # Test timestamp formatting method
            epoch_timestamp = current_epoch()
            formatted_timestamp = api_service._format_timestamp(epoch_timestamp)
            
            assert isinstance(formatted_timestamp, str)
            assert 'T' in formatted_timestamp  # Should be ISO format
            
            # Verify it can be converted back
            converted_back = safe_convert_to_epoch(formatted_timestamp)
            assert abs(converted_back - epoch_timestamp) < 1.0  # Allow 1 second difference
            
            results['tests'].append({'test': 'API_timestamp_formatting', 'status': 'PASS'})
            results['passed'] += 1
            
        except Exception as e:
            results['tests'].append({'test': 'API_timestamp_formatting', 'status': 'FAIL', 'error': str(e)})
            results['failed'] += 1
        
        return results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results."""
        logger.info("Running all epoch migration tests")
        
        all_results = {
            'test_time': datetime.utcnow().isoformat(),
            'database': self.database_name,
            'tests': {}
        }
        
        # Run individual test suites
        all_results['tests']['time_utils'] = self.test_time_utils()
        all_results['tests']['data_formats'] = self.test_data_formats()
        all_results['tests']['collector_structures'] = self.test_collector_data_structures()
        all_results['tests']['engine_structures'] = self.test_engine_data_structures()
        all_results['tests']['api_responses'] = self.test_api_responses()
        
        # Calculate overall statistics
        total_passed = 0
        total_failed = 0
        
        for test_suite, results in all_results['tests'].items():
            if 'passed' in results and 'failed' in results:
                total_passed += results['passed']
                total_failed += results['failed']
        
        all_results['summary'] = {
            'total_passed': total_passed,
            'total_failed': total_failed,
            'success_rate': total_passed / (total_passed + total_failed) * 100 if (total_passed + total_failed) > 0 else 0
        }
        
        return all_results


def main():
    """Main function to run the tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test epoch timestamp migration')
    parser.add_argument('--database', default='vietnam_stock_ai',
                       help='Database name to test')
    parser.add_argument('--output', help='Output file for test results (JSON)')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = get_config()
        
        # Connect to MongoDB
        mongo_client = MongoClient(config.get('mongo_uri', 'mongodb://localhost:27017'))
        
        # Test connection
        mongo_client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {config.get('mongo_uri', 'mongodb://localhost:27017')}")
        
        # Create tester
        tester = EpochMigrationTester(mongo_client, args.database)
        
        # Run all tests
        results = tester.run_all_tests()
        
        # Print results
        print("\n=== EPOCH MIGRATION TEST RESULTS ===")
        print(f"Database: {results['database']}")
        print(f"Test Time: {results['test_time']}")
        print(f"Overall Success Rate: {results['summary']['success_rate']:.1f}%")
        print(f"Tests Passed: {results['summary']['total_passed']}")
        print(f"Tests Failed: {results['summary']['total_failed']}")
        
        # Print detailed results
        for test_suite, test_results in results['tests'].items():
            print(f"\n--- {test_suite.upper()} ---")
            
            if 'passed' in test_results and 'failed' in test_results:
                print(f"Passed: {test_results['passed']}, Failed: {test_results['failed']}")
                
                if 'tests' in test_results:
                    for test in test_results['tests']:
                        status_icon = "✅" if test['status'] == 'PASS' else "❌"
                        print(f"  {status_icon} {test['test']}")
                        if test['status'] == 'FAIL' and 'error' in test:
                            print(f"    Error: {test['error']}")
            
            elif 'collections' in test_results:
                # Data format results
                print(f"Total Epoch Timestamps: {test_results['total_epoch_timestamps']}")
                print(f"Total ISO Timestamps: {test_results['total_iso_timestamps']}")
                print(f"Total Invalid Timestamps: {test_results['total_invalid_timestamps']}")
                
                for collection_name, collection_data in test_results['collections'].items():
                    print(f"\n  {collection_name} ({collection_data['document_count']} documents):")
                    for field_name, field_data in collection_data['fields'].items():
                        print(f"    {field_name}: {field_data['epoch_count']} epoch, {field_data['iso_count']} ISO, {field_data['invalid_count']} invalid")
        
        # Save results to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\nResults saved to: {args.output}")
        
        # Exit with appropriate code
        if results['summary']['total_failed'] == 0:
            print(f"\n✅ All tests passed!")
            sys.exit(0)
        else:
            print(f"\n❌ {results['summary']['total_failed']} tests failed!")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}", exc_info=True)
        print(f"❌ Test execution failed: {str(e)}")
        sys.exit(1)
    finally:
        if 'mongo_client' in locals():
            mongo_client.close()


if __name__ == "__main__":
    main()