#!/usr/bin/env python
"""
Test script for LLM Engine with OpenAI API.

This script tests the LLM Engine with real OpenAI API calls.
Make sure to set OPENAI_API_KEY in your .env file before running.

Usage:
    python scripts/test_llm_openai.py
"""

import sys
import os
from datetime import datetime
from unittest.mock import Mock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.engines.llm_engine import LLMEngine, LLMClient
from src.config import config
from pymongo import MongoClient


def test_llm_client_sentiment():
    """Test LLM client sentiment analysis."""
    print("\n" + "="*80)
    print("Testing LLM Client Sentiment Analysis")
    print("="*80)
    
    # Check if API key is set
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == 'your_openai_api_key_here':
        print("\n❌ ERROR: OPENAI_API_KEY not set in .env file")
        print("Please set your OpenAI API key in the .env file and try again.")
        return False
    
    print(f"\n✓ OpenAI API Key found (length: {len(config.OPENAI_API_KEY)})")
    print(f"✓ Using model: {config.OPENAI_MODEL}")
    
    # Create LLM client with OpenAI
    print("\n📡 Initializing LLM Client with OpenAI API...")
    client = LLMClient(api_key=config.OPENAI_API_KEY, model=config.OPENAI_MODEL, use_openai=True)
    
    # Test cases
    test_cases = [
        {
            "name": "Positive Vietnamese News",
            "text": "Vinamilk (VNM) công bố kết quả kinh doanh quý 4 tăng trưởng mạnh với lợi nhuận tăng 25% so với cùng kỳ năm trước. Công ty dự kiến sẽ tiếp tục mở rộng thị trường xuất khẩu.",
            "expected_sentiment": "positive"
        },
        {
            "name": "Negative Vietnamese News",
            "text": "Vietcombank (VCB) báo cáo lợi nhuận giảm 15% trong quý 3 do ảnh hưởng của nợ xấu tăng cao. Ngân hàng đang đối mặt với nhiều khó khăn trong việc thu hồi nợ.",
            "expected_sentiment": "negative"
        },
        {
            "name": "Neutral Vietnamese News",
            "text": "Vingroup (VIC) tổ chức đại hội cổ đông thường niên vào ngày 15 tháng 4. Các cổ đông sẽ bỏ phiếu về các vấn đề quan trọng của công ty.",
            "expected_sentiment": "neutral"
        },
        {
            "name": "Positive English News",
            "text": "The company reported strong quarterly earnings with revenue growth of 30% and increased market share. Analysts are optimistic about future prospects.",
            "expected_sentiment": "positive"
        },
        {
            "name": "Negative English News",
            "text": "The stock price declined sharply following news of significant losses and declining sales. Investors are concerned about the company's financial health.",
            "expected_sentiment": "negative"
        }
    ]
    
    print("\n🧪 Running sentiment analysis tests...\n")
    
    success_count = 0
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Text: {test_case['text'][:100]}...")
        print(f"Expected: {test_case['expected_sentiment']}")
        
        try:
            result = client.analyze_sentiment(test_case['text'])
            
            print(f"Result:")
            print(f"  - Sentiment: {result['sentiment']}")
            print(f"  - Score: {result['score']:.2f}")
            print(f"  - Confidence: {result['confidence']:.2f}")
            
            # Check if sentiment matches expected
            if result['sentiment'] == test_case['expected_sentiment']:
                print(f"  ✓ PASS")
                success_count += 1
            else:
                print(f"  ⚠ MISMATCH (expected {test_case['expected_sentiment']}, got {result['sentiment']})")
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
    
    print(f"\n{'='*80}")
    print(f"Results: {success_count}/{len(test_cases)} tests passed")
    print(f"{'='*80}")
    
    return success_count == len(test_cases)


def test_llm_client_summary():
    """Test LLM client summary generation."""
    print("\n" + "="*80)
    print("Testing LLM Client Summary Generation")
    print("="*80)
    
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == 'your_openai_api_key_here':
        print("\n❌ ERROR: OPENAI_API_KEY not set in .env file")
        return False
    
    print(f"\n✓ Using model: {config.OPENAI_MODEL}")
    
    # Create LLM client with OpenAI
    print("\n📡 Initializing LLM Client with OpenAI API...")
    client = LLMClient(api_key=config.OPENAI_API_KEY, model=config.OPENAI_MODEL, use_openai=True)
    
    # Test articles
    articles = [
        "Vinamilk công bố kết quả kinh doanh quý 4 tăng trưởng mạnh với lợi nhuận tăng 25%.",
        "Vietcombank mở rộng mạng lưới chi nhánh tại các tỉnh miền Trung.",
        "Vingroup ra mắt dự án bất động sản mới tại Hà Nội với quy mô 50 hecta.",
        "FPT Software ký hợp đồng lớn với đối tác Nhật Bản trị giá 100 triệu USD.",
        "Hòa Phát tăng công suất sản xuất thép để đáp ứng nhu cầu thị trường."
    ]
    
    print(f"\n🧪 Generating summary for {len(articles)} articles...\n")
    
    try:
        summary = client.generate_summary(articles)
        
        print(f"Summary:")
        print(f"{summary}")
        print(f"\n✓ Summary generated successfully")
        print(f"  Length: {len(summary)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_llm_engine_full():
    """Test full LLM Engine with mock MongoDB."""
    print("\n" + "="*80)
    print("Testing Full LLM Engine")
    print("="*80)
    
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == 'your_openai_api_key_here':
        print("\n❌ ERROR: OPENAI_API_KEY not set in .env file")
        return False
    
    print(f"\n✓ Using model: {config.OPENAI_MODEL}")
    
    # Create mock MongoDB client
    print("\n🔧 Creating mock MongoDB client...")
    mock_client = Mock(spec=MongoClient)
    mock_db = Mock()
    mock_news_collection = Mock()
    mock_analysis_collection = Mock()
    
    mock_db.__getitem__ = Mock(side_effect=lambda x: {
        'news': mock_news_collection,
        'llm_analysis': mock_analysis_collection
    }.get(x))
    
    mock_client.__getitem__ = Mock(return_value=mock_db)
    
    # Create sample news articles
    sample_articles = [
        {
            'symbol': 'VNM',
            'title': 'Vinamilk tăng trưởng mạnh',
            'content': 'Vinamilk công bố kết quả kinh doanh quý 4 tăng trưởng mạnh với lợi nhuận tăng 25% so với cùng kỳ năm trước.',
            'source': 'cafef.vn',
            'published_at': datetime.utcnow().isoformat(),
            'collected_at': datetime.utcnow().isoformat()
        },
        {
            'symbol': 'VNM',
            'title': 'VNM mở rộng thị trường',
            'content': 'Vinamilk dự kiến sẽ tiếp tục mở rộng thị trường xuất khẩu sang các nước Đông Nam Á.',
            'source': 'vnexpress.net',
            'published_at': datetime.utcnow().isoformat(),
            'collected_at': datetime.utcnow().isoformat()
        },
        {
            'symbol': 'VNM',
            'title': 'Cổ phiếu VNM tăng giá',
            'content': 'Cổ phiếu Vinamilk tăng 5% trong phiên giao dịch hôm nay sau thông tin tích cực về kết quả kinh doanh.',
            'source': 'vietstock.vn',
            'published_at': datetime.utcnow().isoformat(),
            'collected_at': datetime.utcnow().isoformat()
        }
    ]
    
    # Mock MongoDB query
    mock_news_collection.find.return_value = sample_articles
    mock_analysis_collection.insert_one.return_value = Mock(inserted_id='mock_id')
    
    # Create LLM Engine with OpenAI
    print("\n📡 Initializing LLM Engine with OpenAI API...")
    engine = LLMEngine(
        mock_client,
        database_name='test_db',
        api_key=config.OPENAI_API_KEY,
        model=config.OPENAI_MODEL,
        use_openai=True
    )
    
    # Analyze news
    print(f"\n🧪 Analyzing news for VNM with {len(sample_articles)} articles...\n")
    
    try:
        result = engine.analyze_news('VNM', lookback_days=7)
        
        if result is None:
            print("❌ ERROR: Analysis returned None")
            return False
        
        print(f"Analysis Result:")
        print(f"  Symbol: {result.symbol}")
        print(f"  Timestamp: {result.timestamp}")
        print(f"  Sentiment: {result.sentiment.sentiment}")
        print(f"  Score: {result.sentiment.score:.2f}")
        print(f"  Confidence: {result.sentiment.confidence:.2f}")
        print(f"  Influence Score: {result.influence_score:.2f}")
        print(f"  Articles Analyzed: {result.articles_analyzed}")
        print(f"\n  Summary:")
        print(f"  {result.summary}")
        
        print(f"\n✓ Analysis completed successfully")
        
        # Verify the result was stored
        if mock_analysis_collection.insert_one.called:
            print(f"✓ Result stored in MongoDB")
        else:
            print(f"⚠ Result was not stored in MongoDB")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fallback_mode():
    """Test LLM Engine in fallback mode (without OpenAI)."""
    print("\n" + "="*80)
    print("Testing LLM Engine in Fallback Mode (Keyword-based)")
    print("="*80)
    
    print("\n🔧 Creating LLM Client without OpenAI API...")
    client = LLMClient(api_key=None, use_openai=False)
    
    test_text = "The company reported strong growth and increased profits with positive outlook."
    
    print(f"\n🧪 Testing sentiment analysis (fallback mode)...")
    print(f"Text: {test_text}")
    
    try:
        result = client.analyze_sentiment(test_text)
        
        print(f"\nResult:")
        print(f"  - Sentiment: {result['sentiment']}")
        print(f"  - Score: {result['score']:.2f}")
        print(f"  - Confidence: {result['confidence']:.2f}")
        
        print(f"\n✓ Fallback mode working correctly")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("LLM Engine OpenAI Integration Test Suite")
    print("="*80)
    
    # Check environment
    print("\n📋 Environment Check:")
    print(f"  OPENAI_API_KEY: {'✓ Set' if config.OPENAI_API_KEY and config.OPENAI_API_KEY != 'your_openai_api_key_here' else '❌ Not set'}")
    print(f"  OPENAI_MODEL: {config.OPENAI_MODEL}")
    
    results = []
    
    # Test 1: Fallback mode (always works)
    results.append(("Fallback Mode", test_fallback_mode()))
    
    # Test 2-4: OpenAI tests (only if API key is set)
    if config.OPENAI_API_KEY and config.OPENAI_API_KEY != 'your_openai_api_key_here':
        results.append(("Sentiment Analysis", test_llm_client_sentiment()))
        results.append(("Summary Generation", test_llm_client_summary()))
        results.append(("Full Engine Test", test_llm_engine_full()))
    else:
        print("\n⚠ Skipping OpenAI tests (API key not set)")
        print("To test with OpenAI, set OPENAI_API_KEY in your .env file")
    
    # Print summary
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")
    print("="*80)
    
    return total_passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
