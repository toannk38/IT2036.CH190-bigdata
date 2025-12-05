import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime
import time



from vnstock import VnstockClient, StockPrice, StockNews, StockListing
from vnstock.exceptions import VnstockError, RateLimitError, DataNotFoundError

@pytest.fixture
def client():
    return VnstockClient(source='VCI', rate_limit=0.1)

@pytest.fixture
def mock_listing_df():
    return pd.DataFrame({
        'symbol': ['VCB', 'VIC'],
        'organ_name': ['Vietcombank', 'Vingroup']
    })

@pytest.fixture
def mock_industries_df():
    return pd.DataFrame({
        'symbol': ['VCB', 'VIC'],
        'organ_name': ['Vietcombank', 'Vingroup'],
        'icb_name3': ['Banking', 'Real Estate'],
        'icb_name2': ['Finance', 'Real Estate'],
        'icb_name4': ['Banks', 'Real Estate Dev']
    })

@pytest.fixture
def mock_price_df():
    return pd.DataFrame({
        'time': ['2024-01-01', '2024-01-02'],
        'open': [100.0, 101.0],
        'high': [105.0, 106.0],
        'low': [99.0, 100.0],
        'close': [103.0, 104.0],
        'volume': [1000000, 1100000]
    })

@pytest.fixture
def mock_news_df():
    return pd.DataFrame({
        'title': ['News 1', 'News 2'],
        'publishDate': ['2024-01-01', '2024-01-02'],
        'source': ['VnExpress', 'CafeF'],
        'url': ['http://example.com/1', 'http://example.com/2']
    })

class TestVnstockClient:
    def test_init(self, client):
        assert client.source == 'VCI'
        assert client.rate_limit == 0.1
    
    def test_get_all_symbols(self, client, mock_listing_df, mock_industries_df):
        with patch('vnstock.vnstock_client.vnstock_lib') as mock_vnstock:
            mock_listing = Mock()
            mock_listing.all_symbols.return_value = mock_listing_df
            mock_listing.symbols_by_industries.return_value = mock_industries_df
            mock_vnstock.Listing.return_value = mock_listing
            
            result = client.get_all_symbols()
            
            assert len(result) == 2
            assert isinstance(result[0], StockListing)
            assert result[0].symbol == 'VCB'
            assert result[0].organ_name == 'Vietcombank'
            assert result[0].icb_name3 == 'Banking'
    
    def test_get_price_history(self, client, mock_price_df):
        with patch('vnstock.vnstock_client.vnstock_lib') as mock_vnstock:
            mock_quote = Mock()
            mock_quote.history.return_value = mock_price_df
            mock_vnstock.Quote.return_value = mock_quote
            
            result = client.get_price_history('VCB', '2024-01-01', '2024-01-02')
            
            assert len(result) == 2
            assert isinstance(result[0], StockPrice)
            assert result[0].symbol == 'VCB'
            assert result[0].open == 100.0
            assert result[0].volume == 1000000
    
    def test_get_price_history_empty(self, client):
        with patch('vnstock.vnstock_client.vnstock_lib') as mock_vnstock:
            mock_quote = Mock()
            mock_quote.history.return_value = pd.DataFrame()
            mock_vnstock.Quote.return_value = mock_quote
            
            with pytest.raises(DataNotFoundError):
                client.get_price_history('INVALID', '2024-01-01', '2024-01-02')
    
    def test_get_news(self, client, mock_news_df):
        with patch('vnstock.vnstock_client.vnstock_lib') as mock_vnstock:
            mock_company = Mock()
            mock_company.news.return_value = mock_news_df
            mock_vnstock.Company.return_value = mock_company
            
            result = client.get_news('VCB')
            
            assert len(result) == 2
            assert isinstance(result[0], StockNews)
            assert result[0].symbol == 'VCB'
            assert result[0].title == 'News 1'
            assert result[0].source == 'VnExpress'
    
    def test_get_news_empty(self, client):
        with patch('vnstock.vnstock_client.vnstock_lib') as mock_vnstock:
            mock_company = Mock()
            mock_company.news.return_value = pd.DataFrame()
            mock_vnstock.Company.return_value = mock_company
            
            result = client.get_news('VCB')
            assert result == []
    
    def test_rate_limit(self, client):
        start = time.time()
        client._rate_limit_check()
        client._rate_limit_check()
        elapsed = time.time() - start
        assert elapsed >= 0.1

class TestCache:
    def test_cache_works(self, client, mock_listing_df, mock_industries_df):
        with patch('vnstock.vnstock_client.vnstock_lib') as mock_vnstock:
            mock_listing = Mock()
            mock_listing.all_symbols.return_value = mock_listing_df
            mock_listing.symbols_by_industries.return_value = mock_industries_df
            mock_vnstock.Listing.return_value = mock_listing
            
            result1 = client.get_all_symbols()
            result2 = client.get_all_symbols()
            
            assert mock_listing.all_symbols.call_count == 1
            assert result1 == result2
