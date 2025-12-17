#!/usr/bin/env python3
"""
Test script for new vnstock API to verify the fixes work correctly.
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_price_data():
    """Test fetching price data using new vnstock API."""
    print("Testing price data collection...")
    
    try:
        from vnstock import Quote
        
        # Test with VCI symbol
        symbol = 'VCI'
        quote = Quote(symbol=symbol, source='VCI')
        
        # Get recent data
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        
        print(f"Fetching price data for {symbol} from {start_date} to {end_date}")
        df = quote.history(start=start_date, end=end_date, interval='1D')
        
        if df is not None and not df.empty:
            print(f"✅ Success! Got {len(df)} rows of price data")
            print(f"Columns: {list(df.columns)}")
            print("Latest data:")
            print(df.tail(1))
            return True
        else:
            print("❌ No data returned")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_news_data():
    """Test fetching news data using new vnstock API."""
    print("\nTesting news data collection...")
    
    try:
        from vnstock import Company
        
        # Test with VCB symbol
        symbol = 'VCB'
        company = Company(symbol=symbol, source='VCI')
        
        print(f"Fetching news data for {symbol}")
        df = company.news()
        
        if df is not None and not df.empty:
            print(f"✅ Success! Got {len(df)} news articles")
            print(f"Columns: {list(df.columns)}")
            print("Sample article:")
            if len(df) > 0:
                first_article = df.iloc[0]
                print(f"Title: {first_article.get('news_title', 'N/A')}")
                print(f"Date: {first_article.get('public_date', 'N/A')}")
            return True
        else:
            print("❌ No news data returned")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing new vnstock API...")
    
    price_ok = test_price_data()
    news_ok = test_news_data()
    
    if price_ok and news_ok:
        print("\n🎉 All tests passed! The vnstock API fixes should work.")
    else:
        print("\n⚠️  Some tests failed. Check vnstock installation or API changes.")
        sys.exit(1)