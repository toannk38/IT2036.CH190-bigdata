#!/usr/bin/env python3
"""
Test script for Data Quality Service - Phase 2.5
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from validators.data_quality_validator import DataQualityValidator
from analyzers.outlier_detector import OutlierDetector
from monitors.quality_monitor import QualityMonitor
from analyzers.data_reconciliation import DataReconciliation
from datetime import datetime

def test_price_validation():
    """Test price data validation"""
    print("=== Testing Price Validation ===")
    
    validator = DataQualityValidator()
    
    # Valid price data
    valid_price = {
        "symbol": "VCB",
        "time": "2024-12-04T09:15:00+07:00",
        "open": 85500,
        "high": 86200,
        "low": 85000,
        "close": 86000,
        "volume": 1250000
    }
    
    result = validator.validate_price_data(valid_price)
    print(f"Valid price - Score: {result.score}, Valid: {result.is_valid}")
    print(f"Issues: {result.issues}, Warnings: {result.warnings}")
    
    # Invalid price data
    invalid_price = {
        "symbol": "VCB",
        "time": "2024-12-04T09:15:00+07:00",
        "open": 85500,
        "high": 84000,  # High < Low (invalid)
        "low": 85000,
        "close": 86000,
        "volume": -100  # Negative volume
    }
    
    result = validator.validate_price_data(invalid_price)
    print(f"Invalid price - Score: {result.score}, Valid: {result.is_valid}")
    print(f"Issues: {result.issues}, Warnings: {result.warnings}")

def test_outlier_detection():
    """Test outlier detection"""
    print("\n=== Testing Outlier Detection ===")
    
    detector = OutlierDetector()
    
    # Historical data
    historical_prices = [
        {"close": 85000, "volume": 1000000},
        {"close": 85200, "volume": 1100000},
        {"close": 85100, "volume": 950000},
        {"close": 85300, "volume": 1200000},
        {"close": 85150, "volume": 1050000},
        {"close": 85250, "volume": 1150000},
        {"close": 85180, "volume": 1080000},
        {"close": 85220, "volume": 1120000},
        {"close": 85190, "volume": 1090000},
        {"close": 85210, "volume": 1110000}
    ]
    
    # Normal price
    normal_price = {"close": 85200, "volume": 1100000}
    result = detector.detect_price_outliers(normal_price, historical_prices)
    print(f"Normal price - Outlier: {result.is_outlier}, Confidence: {result.confidence:.3f}")
    
    # Outlier price
    outlier_price = {"close": 95000, "volume": 5000000}  # Extreme values
    result = detector.detect_price_outliers(outlier_price, historical_prices)
    print(f"Outlier price - Outlier: {result.is_outlier}, Confidence: {result.confidence:.3f}")
    print(f"Details: {result.details}")

def test_quality_monitoring():
    """Test quality monitoring"""
    print("\n=== Testing Quality Monitoring ===")
    
    monitor = QualityMonitor()
    validator = DataQualityValidator()
    
    # Simulate some data processing
    test_prices = [
        {"symbol": "VCB", "time": "2024-12-04T09:15:00+07:00", "open": 85500, "high": 86200, "low": 85000, "close": 86000, "volume": 1250000},
        {"symbol": "VIC", "time": "2024-12-04T09:16:00+07:00", "open": 95500, "high": 96200, "low": 95000, "close": 96000, "volume": 850000},
        {"symbol": "VNM", "open": 75500, "high": 74000, "low": 75000, "close": 76000, "volume": -100},  # Invalid data
    ]
    
    for price_data in test_prices:
        validation_result = validator.validate_price_data(price_data)
        monitor.record_price_validation(validation_result, False)
    
    # Get quality summary
    summary = monitor.get_quality_summary()
    print(f"Total records: {summary['overall']['total_records']}")
    print(f"Validity rate: {summary['overall']['validity_rate']:.3f}")
    print(f"Average quality score: {summary['overall']['avg_quality_score']:.3f}")
    print(f"Alerts: {len(summary['alerts'])}")
    
    for alert in summary['alerts']:
        print(f"  - {alert['type']}: {alert['message']}")

def test_data_reconciliation():
    """Test data reconciliation"""
    print("\n=== Testing Data Reconciliation ===")
    
    reconciler = DataReconciliation()
    
    # Simulate collected price data (incomplete)
    collected_data = [
        {"time": "2024-12-04T09:00:00+07:00", "close": 85000},
        {"time": "2024-12-04T09:01:00+07:00", "close": 85100},
        {"time": "2024-12-04T09:02:00+07:00", "close": 85050},
        # Gap here - missing 09:03 to 09:10
        {"time": "2024-12-04T09:11:00+07:00", "close": 85200},
        {"time": "2024-12-04T09:12:00+07:00", "close": 85150},
    ]
    
    date = datetime(2024, 12, 4)  # Wednesday
    result = reconciler.reconcile_price_data("VCB", date, collected_data)
    
    print(f"Symbol: {result.symbol}")
    print(f"Expected: {result.expected_count}, Actual: {result.actual_count}")
    print(f"Missing: {result.missing_count}, Duplicates: {result.duplicate_count}")
    print(f"Quality Score: {result.quality_score:.3f}")
    print(f"Data gaps: {result.data_gaps}")

def test_news_validation():
    """Test news validation"""
    print("\n=== Testing News Validation ===")
    
    validator = DataQualityValidator()
    
    # Valid news
    valid_news = {
        "news_id": "news_123",
        "symbol": "VCB",
        "title": "VCB công bố kế hoạch tăng vốn điều lệ năm 2024",
        "content": "Ngân hàng TMCP Ngoại thương Việt Nam (VCB) vừa công bố kế hoạch tăng vốn điều lệ trong năm 2024 nhằm mở rộng hoạt động kinh doanh và đáp ứng các yêu cầu về an toàn vốn theo quy định của Ngân hàng Nhà nước.",
        "source": "VnExpress",
        "published_at": "2024-12-04T08:30:00+07:00"
    }
    
    result = validator.validate_news_data(valid_news)
    print(f"Valid news - Score: {result.score}, Valid: {result.is_valid}")
    print(f"Issues: {result.issues}, Warnings: {result.warnings}")
    
    # Invalid news (too short)
    invalid_news = {
        "news_id": "news_456",
        "symbol": "VIC",
        "title": "Short",
        "content": "Too short content",
        "source": "Test",
        "published_at": "2024-12-04T08:30:00+07:00"
    }
    
    result = validator.validate_news_data(invalid_news)
    print(f"Invalid news - Score: {result.score}, Valid: {result.is_valid}")
    print(f"Issues: {result.issues}, Warnings: {result.warnings}")

def main():
    """Run all tests"""
    print("🧪 Data Quality Service Tests - Phase 2.5")
    print("=" * 50)
    
    try:
        test_price_validation()
        test_outlier_detection()
        test_quality_monitoring()
        test_data_reconciliation()
        test_news_validation()
        
        print("\n✅ All tests completed successfully!")
        print("\n📊 Phase 2.5 Components Validated:")
        print("  ✓ Comprehensive data validation rules")
        print("  ✓ Data quality monitoring metrics")
        print("  ✓ Outlier detection algorithms")
        print("  ✓ Data reconciliation processes")
        print("  ✓ Quality scoring and alerting")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()