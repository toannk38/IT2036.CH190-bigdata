"""
Unit tests for API Service.
Tests specific functionality and edge cases for API endpoints.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException

from src.services.api_service import APIService, StockSummary, AlertResponse, HistoricalData


class TestAPIService:
    """Unit tests for APIService class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.mock_client = MagicMock()
        self.mock_db = MagicMock()
        
        # Create mock collections
        self.mock_symbols = MagicMock()
        self.mock_price = MagicMock()
        self.mock_ai = MagicMock()
        self.mock_llm = MagicMock()
        self.mock_final = MagicMock()
        
        # Setup database to return correct collections
        collections = {
            'symbols': self.mock_symbols,
            'price_history': self.mock_price,
            'ai_analysis': self.mock_ai,
            'llm_analysis': self.mock_llm,
            'final_scores': self.mock_final
        }
        self.mock_db.__getitem__ = MagicMock(side_effect=lambda name: collections.get(name, MagicMock()))
        self.mock_client.__getitem__ = MagicMock(return_value=self.mock_db)
        
        self.api_service = APIService(self.mock_client)
    
    def test_get_stock_summary_valid_symbol(self):
        """Test get_stock_summary with valid symbol returns complete data."""
        # Setup test data
        symbol = 'VNM'
        self.mock_symbols.find_one.return_value = {'symbol': symbol, 'active': True}
        self.mock_price.find_one.return_value = {
            'symbol': symbol,
            'timestamp': '2024-01-15T09:30:00Z',
            'open': 85000,
            'close': 86500,
            'high': 87000,
            'low': 84500,
            'volume': 1250000
        }
        self.mock_ai.find_one.return_value = {
            'symbol': symbol,
            'timestamp': '2024-01-15T10:00:00Z',
            'technical_score': 0.72,
            'risk_score': 0.35,
            'trend_prediction': {
                'direction': 'up',
                'confidence': 0.75,
                'predicted_price': 88000
            },
            'indicators': {'rsi': 65, 'macd': 1250}
        }
        self.mock_llm.find_one.return_value = {
            'symbol': symbol,
            'timestamp': '2024-01-15T10:00:00Z',
            'sentiment': {
                'overall': 'positive',
                'score': 0.68,
                'confidence': 0.82
            },
            'summary': 'Positive outlook',
            'influence_score': 0.75,
            'articles_analyzed': 5
        }
        self.mock_final.find_one.return_value = {
            'symbol': symbol,
            'timestamp': '2024-01-15T10:05:00Z',
            'final_score': 72.5,
            'recommendation': 'BUY',
            'components': {
                'technical_score': 0.72,
                'risk_score': 0.35,
                'sentiment_score': 0.68
            },
            'alerts': [
                {
                    'type': 'BUY',
                    'priority': 'high',
                    'message': 'Strong buy signal detected'
                }
            ]
        }
        
        # Call method
        result = self.api_service.get_stock_summary(symbol)
        
        # Assertions
        assert result is not None
        assert isinstance(result, StockSummary)
        assert result.symbol == symbol
        assert result.current_price is not None
        assert result.current_price.close == 86500
        assert result.ai_ml_analysis is not None
        assert result.llm_analysis is not None
        assert result.final_score == 72.5
        assert result.recommendation == 'BUY'
        assert len(result.alerts) == 1
        assert result.alerts[0].type == 'BUY'
    
    def test_get_stock_summary_invalid_symbol(self):
        """Test get_stock_summary with non-existent symbol raises HTTPException."""
        # Setup: symbol doesn't exist
        self.mock_symbols.find_one.return_value = None
        
        # Call method and expect exception
        with pytest.raises(HTTPException) as exc_info:
            self.api_service.get_stock_summary('INVALID')
        
        # Assertions
        assert exc_info.value.status_code == 404
        assert 'not found' in exc_info.value.detail.lower()
    
    def test_get_stock_summary_missing_data(self):
        """Test get_stock_summary handles missing analysis data gracefully."""
        # Setup: symbol exists but no analysis data
        symbol = 'VNM'
        self.mock_symbols.find_one.return_value = {'symbol': symbol, 'active': True}
        self.mock_price.find_one.return_value = None
        self.mock_ai.find_one.return_value = None
        self.mock_llm.find_one.return_value = None
        self.mock_final.find_one.return_value = None
        
        # Call method
        result = self.api_service.get_stock_summary(symbol)
        
        # Assertions - should return summary with None values
        assert result is not None
        assert result.symbol == symbol
        assert result.current_price is None
        assert result.ai_ml_analysis is None
        assert result.llm_analysis is None
        assert result.final_score is None
        assert result.recommendation is None
    
    def test_get_alerts_with_pagination(self):
        """Test get_alerts returns paginated results."""
        # Setup test data
        test_alerts = []
        for i in range(10):
            test_alerts.append({
                'symbol': f'SYM{i}',
                'timestamp': (datetime.utcnow() - timedelta(hours=i)).isoformat(),
                'final_score': 50.0 + i,
                'recommendation': 'WATCH',
                'alerts': {
                    'type': 'WATCH',
                    'priority': 'medium',
                    'message': f'Watch signal for SYM{i}'
                }
            })
        
        def mock_aggregate(pipeline):
            result = []
            for alert_doc in test_alerts:
                result.append({
                    'symbol': alert_doc['symbol'],
                    'timestamp': alert_doc['timestamp'],
                    'final_score': alert_doc['final_score'],
                    'recommendation': alert_doc['recommendation'],
                    'alert': alert_doc['alerts']
                })
            return result
        
        self.mock_final.aggregate = mock_aggregate
        
        # Call method with pagination
        result = self.api_service.get_alerts(limit=5, offset=0)
        
        # Assertions
        assert result is not None
        assert isinstance(result, AlertResponse)
        assert result.total == 10
        assert len(result.alerts) == 5
        assert result.page == 1
        assert result.page_size == 5
    
    def test_get_alerts_empty_results(self):
        """Test get_alerts handles empty results."""
        # Setup: no alerts
        self.mock_final.aggregate = MagicMock(return_value=[])
        
        # Call method
        result = self.api_service.get_alerts()
        
        # Assertions
        assert result is not None
        assert result.total == 0
        assert len(result.alerts) == 0
    
    def test_get_historical_analysis_valid_range(self):
        """Test get_historical_analysis with valid date range."""
        # Setup test data
        symbol = 'VNM'
        start_date = '2024-01-01'
        end_date = '2024-01-31'
        
        self.mock_symbols.find_one.return_value = {'symbol': symbol, 'active': True}
        
        test_data = []
        for i in range(5):
            test_data.append({
                'symbol': symbol,
                'timestamp': f'2024-01-{i+1:02d}T10:00:00Z',
                'final_score': 50.0 + i * 5,
                'recommendation': 'WATCH',
                'components': {
                    'technical_score': 0.5,
                    'risk_score': 0.3,
                    'sentiment_score': 0.6
                }
            })
        
        self.mock_final.find = MagicMock(return_value=test_data)
        
        # Call method
        result = self.api_service.get_historical_analysis(symbol, start_date, end_date)
        
        # Assertions
        assert result is not None
        assert isinstance(result, HistoricalData)
        assert result.symbol == symbol
        assert result.start_date == start_date
        assert result.end_date == end_date
        assert result.total_points == 5
        assert len(result.data) == 5
        
        # Check first data point
        assert result.data[0].final_score == 50.0
        assert result.data[0].recommendation == 'WATCH'
    
    def test_get_historical_analysis_invalid_symbol(self):
        """Test get_historical_analysis with non-existent symbol."""
        # Setup: symbol doesn't exist
        self.mock_symbols.find_one.return_value = None
        
        # Call method and expect exception
        with pytest.raises(HTTPException) as exc_info:
            self.api_service.get_historical_analysis('INVALID', '2024-01-01', '2024-01-31')
        
        # Assertions
        assert exc_info.value.status_code == 404
        assert 'not found' in exc_info.value.detail.lower()
    
    def test_get_historical_analysis_invalid_date_format(self):
        """Test get_historical_analysis with invalid date format."""
        # Setup: symbol exists
        self.mock_symbols.find_one.return_value = {'symbol': 'VNM', 'active': True}
        
        # Call method with invalid date and expect exception
        with pytest.raises(HTTPException) as exc_info:
            self.api_service.get_historical_analysis('VNM', 'invalid-date', '2024-01-31')
        
        # Assertions
        assert exc_info.value.status_code == 400
        assert 'invalid date format' in exc_info.value.detail.lower()
    
    def test_get_historical_analysis_start_after_end(self):
        """Test get_historical_analysis with start_date after end_date."""
        # Setup: symbol exists
        self.mock_symbols.find_one.return_value = {'symbol': 'VNM', 'active': True}
        
        # Call method with invalid date range and expect exception
        with pytest.raises(HTTPException) as exc_info:
            self.api_service.get_historical_analysis('VNM', '2024-12-31', '2024-01-01')
        
        # Assertions
        assert exc_info.value.status_code == 400
        assert 'before or equal' in exc_info.value.detail.lower()
    
    def test_get_historical_analysis_empty_results(self):
        """Test get_historical_analysis with no data in range."""
        # Setup
        symbol = 'VNM'
        self.mock_symbols.find_one.return_value = {'symbol': symbol, 'active': True}
        self.mock_final.find = MagicMock(return_value=[])
        
        # Call method
        result = self.api_service.get_historical_analysis(symbol, '2024-01-01', '2024-01-31')
        
        # Assertions
        assert result is not None
        assert result.total_points == 0
        assert len(result.data) == 0


class TestAPIEndpoints:
    """Integration tests for FastAPI endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from fastapi.testclient import TestClient
        from src.services.api_service import app
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert 'message' in data
        assert 'version' in data
        assert 'endpoints' in data
    
    @patch('src.services.api_service.api_service')
    def test_get_stock_summary_endpoint(self, mock_service, client):
        """Test /stock/{symbol}/summary endpoint."""
        # Setup mock
        mock_summary = MagicMock()
        mock_summary.symbol = 'VNM'
        mock_summary.final_score = 72.5
        mock_summary.recommendation = 'BUY'
        mock_summary.current_price = None
        mock_summary.ai_ml_analysis = None
        mock_summary.llm_analysis = None
        mock_summary.component_scores = None
        mock_summary.alerts = []
        mock_summary.last_updated = None
        
        mock_service.get_stock_summary.return_value = mock_summary
        
        # Call endpoint
        response = client.get("/stock/VNM/summary")
        
        # Assertions
        assert response.status_code == 200
        mock_service.get_stock_summary.assert_called_once_with('VNM')
    
    @patch('src.services.api_service.api_service')
    def test_get_stock_summary_endpoint_not_found(self, mock_service, client):
        """Test /stock/{symbol}/summary endpoint with non-existent symbol."""
        # Setup mock to raise HTTPException
        mock_service.get_stock_summary.side_effect = HTTPException(
            status_code=404,
            detail="Symbol 'INVALID' not found"
        )
        
        # Call endpoint
        response = client.get("/stock/INVALID/summary")
        
        # Assertions
        assert response.status_code == 404
        data = response.json()
        assert 'error' in data
        assert 'message' in data
    
    @patch('src.services.api_service.api_service')
    def test_get_alerts_endpoint(self, mock_service, client):
        """Test /alerts endpoint."""
        # Setup mock
        mock_response = AlertResponse(
            alerts=[],
            total=0,
            page=1,
            page_size=50
        )
        mock_service.get_alerts.return_value = mock_response
        
        # Call endpoint
        response = client.get("/alerts")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert 'alerts' in data
        assert 'total' in data
        assert 'page' in data
        assert 'page_size' in data
    
    @patch('src.services.api_service.api_service')
    def test_get_alerts_endpoint_with_pagination(self, mock_service, client):
        """Test /alerts endpoint with pagination parameters."""
        # Setup mock
        mock_response = AlertResponse(
            alerts=[],
            total=100,
            page=2,
            page_size=25
        )
        mock_service.get_alerts.return_value = mock_response
        
        # Call endpoint with pagination
        response = client.get("/alerts?limit=25&offset=25")
        
        # Assertions
        assert response.status_code == 200
        mock_service.get_alerts.assert_called_once_with(limit=25, offset=25)
    
    @patch('src.services.api_service.api_service')
    def test_get_historical_analysis_endpoint(self, mock_service, client):
        """Test /stock/{symbol}/history endpoint."""
        # Setup mock
        mock_response = HistoricalData(
            symbol='VNM',
            start_date='2024-01-01',
            end_date='2024-01-31',
            data=[],
            total_points=0
        )
        mock_service.get_historical_analysis.return_value = mock_response
        
        # Call endpoint
        response = client.get("/stock/VNM/history?start_date=2024-01-01&end_date=2024-01-31")
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data['symbol'] == 'VNM'
        assert data['start_date'] == '2024-01-01'
        assert data['end_date'] == '2024-01-31'
    
    def test_get_historical_analysis_endpoint_missing_params(self, client):
        """Test /stock/{symbol}/history endpoint with missing parameters."""
        # Call endpoint without required parameters
        response = client.get("/stock/VNM/history")
        
        # Assertions - FastAPI should return 422 for missing required params
        assert response.status_code == 422
