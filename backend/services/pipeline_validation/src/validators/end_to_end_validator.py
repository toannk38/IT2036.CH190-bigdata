import logging
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from kafka import KafkaProducer, KafkaConsumer
from pymongo import MongoClient

logger = logging.getLogger(__name__)

@dataclass
class PipelineTestResult:
    test_name: str
    success: bool
    duration_seconds: float
    records_sent: int
    records_received: int
    data_quality_score: float
    errors: List[str]
    warnings: List[str]

class EndToEndValidator:
    def __init__(self, kafka_servers: str, mongodb_uri: str):
        self.kafka_servers = kafka_servers
        self.mongodb_uri = mongodb_uri
        self.test_symbol = "TEST_SYMBOL"
        
    def validate_full_pipeline(self) -> Dict[str, Any]:
        """Validate complete data pipeline from Kafka to MongoDB"""
        results = []
        
        # Test 1: Price data flow
        price_result = self._test_price_data_flow()
        results.append(price_result)
        
        # Test 2: News data flow
        news_result = self._test_news_data_flow()
        results.append(news_result)
        
        # Test 3: Data quality validation
        quality_result = self._test_data_quality()
        results.append(quality_result)
        
        # Test 4: Performance benchmarking
        perf_result = self._test_performance()
        results.append(perf_result)
        
        # Calculate overall success
        all_success = all(r.success for r in results)
        avg_quality = sum(r.data_quality_score for r in results) / len(results)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_success': all_success,
            'average_quality_score': avg_quality,
            'total_tests': len(results),
            'passed_tests': sum(1 for r in results if r.success),
            'test_results': [self._result_to_dict(r) for r in results],
            'summary': self._generate_summary(results)
        }
    
    def _test_price_data_flow(self) -> PipelineTestResult:
        """Test price data flow through pipeline"""
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            # Generate test price data
            test_data = self._generate_test_price_data(10)
            
            # Send to Kafka
            sent_count = self._send_to_kafka('stock_prices_raw', test_data)
            
            # Wait for processing
            time.sleep(5)
            
            # Verify in MongoDB
            received_count = self._verify_in_mongodb('stock_prices', test_data)
            
            # Calculate quality score
            quality_score = received_count / sent_count if sent_count > 0 else 0.0
            
            success = received_count == sent_count and quality_score >= 0.95
            
            if received_count < sent_count:
                warnings.append(f"Data loss: sent {sent_count}, received {received_count}")
            
        except Exception as e:
            errors.append(f"Price data flow test failed: {e}")
            sent_count = received_count = 0
            quality_score = 0.0
            success = False
        
        duration = time.time() - start_time
        
        return PipelineTestResult(
            test_name="price_data_flow",
            success=success,
            duration_seconds=duration,
            records_sent=sent_count,
            records_received=received_count,
            data_quality_score=quality_score,
            errors=errors,
            warnings=warnings
        )
    
    def _test_news_data_flow(self) -> PipelineTestResult:
        """Test news data flow through pipeline"""
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            # Generate test news data
            test_data = self._generate_test_news_data(5)
            
            # Send to Kafka
            sent_count = self._send_to_kafka('stock_news_raw', test_data)
            
            # Wait for processing
            time.sleep(5)
            
            # Verify in MongoDB
            received_count = self._verify_in_mongodb('news', test_data)
            
            # Calculate quality score
            quality_score = received_count / sent_count if sent_count > 0 else 0.0
            
            success = received_count == sent_count and quality_score >= 0.95
            
            if received_count < sent_count:
                warnings.append(f"Data loss: sent {sent_count}, received {received_count}")
            
        except Exception as e:
            errors.append(f"News data flow test failed: {e}")
            sent_count = received_count = 0
            quality_score = 0.0
            success = False
        
        duration = time.time() - start_time
        
        return PipelineTestResult(
            test_name="news_data_flow",
            success=success,
            duration_seconds=duration,
            records_sent=sent_count,
            records_received=received_count,
            data_quality_score=quality_score,
            errors=errors,
            warnings=warnings
        )
    
    def _test_data_quality(self) -> PipelineTestResult:
        """Test data quality validation"""
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            # Test with invalid data
            invalid_data = [
                {
                    "symbol": self.test_symbol,
                    "time": "invalid_time",
                    "open": -100,  # Invalid price
                    "high": 50,
                    "low": 60,     # Low > High (invalid)
                    "close": 55,
                    "volume": -1000  # Invalid volume
                }
            ]
            
            # Send invalid data
            sent_count = self._send_to_kafka('stock_prices_raw', invalid_data)
            
            # Wait for processing
            time.sleep(3)
            
            # Check if invalid data was rejected
            received_count = self._verify_in_mongodb('stock_prices', invalid_data)
            
            # Quality validation should reject invalid data
            success = received_count == 0  # Invalid data should be rejected
            quality_score = 1.0 if success else 0.0
            
            if received_count > 0:
                errors.append("Invalid data was not rejected by quality validation")
            
        except Exception as e:
            errors.append(f"Data quality test failed: {e}")
            sent_count = received_count = 0
            quality_score = 0.0
            success = False
        
        duration = time.time() - start_time
        
        return PipelineTestResult(
            test_name="data_quality_validation",
            success=success,
            duration_seconds=duration,
            records_sent=sent_count,
            records_received=received_count,
            data_quality_score=quality_score,
            errors=errors,
            warnings=warnings
        )
    
    def _test_performance(self) -> PipelineTestResult:
        """Test pipeline performance"""
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            # Generate larger dataset for performance test
            test_data = self._generate_test_price_data(100)
            
            # Measure send time
            send_start = time.time()
            sent_count = self._send_to_kafka('stock_prices_raw', test_data)
            send_duration = time.time() - send_start
            
            # Wait for processing
            time.sleep(10)
            
            # Measure total processing time
            received_count = self._verify_in_mongodb('stock_prices', test_data)
            
            # Performance criteria: < 10 seconds for 100 records
            total_duration = time.time() - start_time
            success = total_duration < 10.0 and received_count == sent_count
            
            # Calculate throughput
            throughput = sent_count / total_duration if total_duration > 0 else 0
            quality_score = min(1.0, throughput / 10.0)  # Target: 10 records/second
            
            if total_duration >= 10.0:
                warnings.append(f"Performance below target: {total_duration:.2f}s for {sent_count} records")
            
            logger.info(f"Performance test: {throughput:.2f} records/second")
            
        except Exception as e:
            errors.append(f"Performance test failed: {e}")
            sent_count = received_count = 0
            quality_score = 0.0
            success = False
        
        duration = time.time() - start_time
        
        return PipelineTestResult(
            test_name="performance_benchmark",
            success=success,
            duration_seconds=duration,
            records_sent=sent_count,
            records_received=received_count,
            data_quality_score=quality_score,
            errors=errors,
            warnings=warnings
        )
    
    def _generate_test_price_data(self, count: int) -> List[Dict[str, Any]]:
        """Generate test price data"""
        data = []
        base_time = datetime.now()
        
        for i in range(count):
            data.append({
                "symbol": f"{self.test_symbol}_{i}",
                "time": (base_time + timedelta(minutes=i)).isoformat(),
                "open": 85000 + i * 100,
                "high": 86000 + i * 100,
                "low": 84000 + i * 100,
                "close": 85500 + i * 100,
                "volume": 1000000 + i * 1000,
                "collected_at": datetime.now().isoformat()
            })
        
        return data
    
    def _generate_test_news_data(self, count: int) -> List[Dict[str, Any]]:
        """Generate test news data"""
        data = []
        base_time = datetime.now()
        
        for i in range(count):
            data.append({
                "news_id": f"test_news_{i}_{int(time.time())}",
                "symbol": f"{self.test_symbol}_{i}",
                "title": f"Test news title {i} for validation",
                "content": f"This is test news content number {i} for pipeline validation. " * 5,
                "source": "Pipeline Test",
                "source_url": f"https://test.com/news/{i}",
                "published_at": (base_time + timedelta(minutes=i)).isoformat(),
                "collected_at": datetime.now().isoformat(),
                "category": "test",
                "tags": ["test", "validation"]
            })
        
        return data
    
    def _send_to_kafka(self, topic: str, data: List[Dict[str, Any]]) -> int:
        """Send test data to Kafka"""
        producer = KafkaProducer(
            bootstrap_servers=self.kafka_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        
        sent_count = 0
        for record in data:
            try:
                future = producer.send(topic, key=record.get('symbol'), value=record)
                future.get(timeout=10)
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send record to {topic}: {e}")
        
        producer.flush()
        producer.close()
        
        return sent_count
    
    def _verify_in_mongodb(self, collection: str, test_data: List[Dict[str, Any]]) -> int:
        """Verify data exists in MongoDB"""
        client = MongoClient(self.mongodb_uri)
        db = client['stock_ai']
        coll = db[collection]
        
        received_count = 0
        for record in test_data:
            if collection == 'stock_prices':
                query = {'symbol': record['symbol'], 'time': record['time']}
            else:  # news
                query = {'news_id': record['news_id']}
            
            if coll.find_one(query):
                received_count += 1
        
        client.close()
        return received_count
    
    def _result_to_dict(self, result: PipelineTestResult) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            'test_name': result.test_name,
            'success': result.success,
            'duration_seconds': result.duration_seconds,
            'records_sent': result.records_sent,
            'records_received': result.records_received,
            'data_quality_score': result.data_quality_score,
            'errors': result.errors,
            'warnings': result.warnings
        }
    
    def _generate_summary(self, results: List[PipelineTestResult]) -> Dict[str, Any]:
        """Generate test summary"""
        total_duration = sum(r.duration_seconds for r in results)
        total_sent = sum(r.records_sent for r in results)
        total_received = sum(r.records_received for r in results)
        
        return {
            'total_duration_seconds': total_duration,
            'total_records_sent': total_sent,
            'total_records_received': total_received,
            'data_loss_rate': (total_sent - total_received) / total_sent if total_sent > 0 else 0,
            'average_throughput': total_sent / total_duration if total_duration > 0 else 0,
            'pipeline_health': 'healthy' if all(r.success for r in results) else 'degraded'
        }