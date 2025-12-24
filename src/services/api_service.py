"""
API Service for Vietnam Stock AI Backend.
Provides REST API endpoints for accessing stock analysis data.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from src.config import config
from src.logging_config import get_logger
from src.utils.time_utils import epoch_to_iso, safe_convert_to_epoch

logger = get_logger(__name__)


# Response Models
class PriceData(BaseModel):
    """Price data model."""
    timestamp: str  # Will be converted from epoch to ISO for API response
    open: float
    close: float
    high: float
    low: float
    volume: int


class SymbolInfo(BaseModel):
    """Symbol information model."""
    symbol: str
    organ_name: str
    icb_name2: Optional[str] = None
    icb_name3: Optional[str] = None
    icb_name4: Optional[str] = None
    com_type_code: Optional[str] = None
    icb_code1: Optional[str] = None
    icb_code2: Optional[str] = None
    icb_code3: Optional[str] = None
    icb_code4: Optional[str] = None
    active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SymbolsResponse(BaseModel):
    """Active symbols list response."""
    symbols: List[SymbolInfo]
    total: int
    active_count: int


class TrendPrediction(BaseModel):
    """Trend prediction model."""
    direction: str
    confidence: float
    predicted_price: Optional[float] = None


class SentimentData(BaseModel):
    """Sentiment analysis data model."""
    overall: str
    score: float
    confidence: float


class ComponentScores(BaseModel):
    """Component scores model."""
    technical_score: float
    risk_score: float
    sentiment_score: float


class Alert(BaseModel):
    """Alert model."""
    type: str
    priority: str
    message: str


class StockSummary(BaseModel):
    """Comprehensive stock summary response."""
    symbol: str
    current_price: Optional[PriceData] = None
    ai_ml_analysis: Optional[Dict[str, Any]] = None
    llm_analysis: Optional[Dict[str, Any]] = None
    final_score: Optional[float] = None
    recommendation: Optional[str] = None
    component_scores: Optional[ComponentScores] = None
    alerts: List[Alert] = []
    last_updated: Optional[str] = None


class AlertResponse(BaseModel):
    """Alert list response."""
    alerts: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int


class HistoricalDataPoint(BaseModel):
    """Historical analysis data point."""
    timestamp: str
    final_score: float
    recommendation: str
    components: ComponentScores


class HistoricalData(BaseModel):
    """Historical analysis response."""
    symbol: str
    start_date: str
    end_date: str
    data: List[HistoricalDataPoint]
    total_points: int


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    status_code: int


# API Service Class
class APIService:
    """
    API Service for providing REST endpoints.
    
    Responsibilities:
    - Provide stock summary endpoint with comprehensive data
    - Provide alerts endpoint with sorting and pagination
    - Provide historical analysis endpoint with date filtering
    - Handle input validation and error responses
    """
    
    def __init__(self, mongo_client: MongoClient, database_name: str = 'vietnam_stock_ai'):
        """
        Initialize APIService.
        
        Args:
            mongo_client: MongoDB client instance
            database_name: Name of the database to use
        """
        self.db = mongo_client[database_name]
        self.price_collection = self.db['price_history']
        self.ai_analysis_collection = self.db['ai_analysis']
        self.llm_analysis_collection = self.db['llm_analysis']
        self.final_scores_collection = self.db['final_scores']
        self.symbols_collection = self.db['symbols']
        
        logger.info("APIService initialized")
    
    def get_stock_summary(self, symbol: str) -> StockSummary:
        """
        Get comprehensive stock summary.
        
        Args:
            symbol: Stock symbol code
            
        Returns:
            StockSummary with all available data
            
        Raises:
            HTTPException: If symbol not found or data retrieval fails
        """
        try:
            logger.info(f"Fetching stock summary for {symbol}")
            
            # Verify symbol exists
            symbol_doc = self.symbols_collection.find_one({'symbol': symbol})
            if not symbol_doc:
                raise HTTPException(
                    status_code=404,
                    detail=f"Symbol '{symbol}' not found"
                )
            
            # Get latest price data
            current_price = self._get_latest_price(symbol)
            
            # Get latest AI/ML analysis
            ai_analysis = self.ai_analysis_collection.find_one(
                {'symbol': symbol},
                sort=[('timestamp', -1)]
            )
            
            # Get latest LLM analysis
            llm_analysis = self.llm_analysis_collection.find_one(
                {'symbol': symbol},
                sort=[('timestamp', -1)]
            )
            
            # Get latest final score
            final_score_doc = self.final_scores_collection.find_one(
                {'symbol': symbol},
                sort=[('timestamp', -1)]
            )
            
            # Build response
            summary = StockSummary(
                symbol=symbol,
                current_price=self._format_price_data(current_price) if current_price else None,
                ai_ml_analysis=self._format_ai_analysis(ai_analysis) if ai_analysis else None,
                llm_analysis=self._format_llm_analysis(llm_analysis) if llm_analysis else None,
                final_score=final_score_doc.get('final_score') if final_score_doc else None,
                recommendation=final_score_doc.get('recommendation') if final_score_doc else None,
                component_scores=self._format_component_scores(final_score_doc) if final_score_doc else None,
                alerts=self._format_alerts(final_score_doc.get('alerts', [])) if final_score_doc else [],
                last_updated=self._format_timestamp(final_score_doc.get('timestamp')) if final_score_doc else None
            )
            
            logger.info(f"Stock summary retrieved for {symbol}")
            return summary
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error retrieving stock summary",
                context={'symbol': symbol, 'error': str(e)},
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
    
    def get_alerts(self, limit: int = 50, offset: int = 0) -> AlertResponse:
        """
        Get active alerts sorted by priority and timestamp.
        
        Sorting order:
        1. Priority: high > medium > low
        2. Timestamp: most recent first
        
        Args:
            limit: Maximum number of alerts to return (default: 50)
            offset: Number of alerts to skip for pagination (default: 0)
            
        Returns:
            AlertResponse with sorted alerts and pagination info
            
        Raises:
            HTTPException: If data retrieval fails
        """
        try:
            logger.info(f"Fetching alerts (limit={limit}, offset={offset})")
            
            # Define priority order for sorting
            priority_order = {'high': 1, 'medium': 2, 'low': 3}
            
            # Get all recent final scores with alerts
            pipeline = [
                # Match documents with alerts
                {'$match': {'alerts': {'$exists': True, '$ne': []}}},
                # Unwind alerts array
                {'$unwind': '$alerts'},
                # Add priority order field for sorting
                {'$addFields': {
                    'priority_order': {
                        '$switch': {
                            'branches': [
                                {'case': {'$eq': ['$alerts.priority', 'high']}, 'then': 1},
                                {'case': {'$eq': ['$alerts.priority', 'medium']}, 'then': 2},
                                {'case': {'$eq': ['$alerts.priority', 'low']}, 'then': 3}
                            ],
                            'default': 4
                        }
                    }
                }},
                # Sort by priority then timestamp
                {'$sort': {'priority_order': 1, 'timestamp': -1}},
                # Project final structure
                {'$project': {
                    'symbol': 1,
                    'timestamp': 1,
                    'final_score': 1,
                    'recommendation': 1,
                    'alert': '$alerts',
                    '_id': 0
                }}
            ]
            
            # Get total count
            total_alerts = list(self.final_scores_collection.aggregate(pipeline))
            total = len(total_alerts)
            
            # Apply pagination
            paginated_alerts = total_alerts[offset:offset + limit]
            
            # Format response
            formatted_alerts = []
            for item in paginated_alerts:
                alert_data = {
                    'symbol': item['symbol'],
                    'timestamp': self._format_timestamp(item['timestamp']),
                    'final_score': item['final_score'],
                    'recommendation': item['recommendation'],
                    'type': item['alert']['type'],
                    'priority': item['alert']['priority'],
                    'message': item['alert']['message']
                }
                formatted_alerts.append(alert_data)
            
            response = AlertResponse(
                alerts=formatted_alerts,
                total=total,
                page=offset // limit + 1 if limit > 0 else 1,
                page_size=limit
            )
            
            logger.info(f"Retrieved {len(formatted_alerts)} alerts (total: {total})")
            return response
            
        except Exception as e:
            logger.error(
                f"Error retrieving alerts",
                context={'error': str(e)},
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
    
    def get_historical_analysis(
        self,
        symbol: str,
        start_date: str,
        end_date: str
    ) -> HistoricalData:
        """
        Get historical analysis data for specified date range.
        
        Args:
            symbol: Stock symbol code
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            
        Returns:
            HistoricalData with time-series analysis data
            
        Raises:
            HTTPException: If symbol not found, invalid dates, or data retrieval fails
        """
        try:
            logger.info(
                f"Fetching historical analysis for {symbol}",
                context={'start_date': start_date, 'end_date': end_date}
            )
            
            # Verify symbol exists
            symbol_doc = self.symbols_collection.find_one({'symbol': symbol})
            if not symbol_doc:
                raise HTTPException(
                    status_code=404,
                    detail=f"Symbol '{symbol}' not found"
                )
            
            # Parse and validate dates
            try:
                start_dt = datetime.fromisoformat(start_date)
                end_dt = datetime.fromisoformat(end_date)
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid date format. Use ISO format (YYYY-MM-DD): {str(e)}"
                )
            
            if start_dt > end_dt:
                raise HTTPException(
                    status_code=400,
                    detail="start_date must be before or equal to end_date"
                )
            
            # Convert to epoch timestamps for query
            start_epoch = start_dt.timestamp()
            end_epoch = end_dt.timestamp()
            
            # Query historical final scores within date range - handle both epoch and ISO formats
            cursor = self.final_scores_collection.find(
                {
                    'symbol': symbol,
                    '$or': [
                        {
                            'timestamp': {
                                '$gte': start_epoch,
                                '$lte': end_epoch
                            }
                        },  # Epoch format
                        {
                            'timestamp': {
                                '$gte': start_dt.isoformat(),
                                '$lte': end_dt.isoformat()
                            }
                        }   # ISO format (legacy)
                    ]
                },
                sort=[('timestamp', 1)]
            )
            
            # Format data points
            data_points = []
            for doc in cursor:
                point = HistoricalDataPoint(
                    timestamp=self._format_timestamp(doc['timestamp']),
                    final_score=doc['final_score'],
                    recommendation=doc['recommendation'],
                    components=ComponentScores(
                        technical_score=doc['components']['technical_score'],
                        risk_score=doc['components']['risk_score'],
                        sentiment_score=doc['components']['sentiment_score']
                    )
                )
                data_points.append(point)
            
            response = HistoricalData(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                data=data_points,
                total_points=len(data_points)
            )
            
            logger.info(
                f"Retrieved {len(data_points)} historical data points for {symbol}"
            )
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error retrieving historical analysis",
                context={'symbol': symbol, 'error': str(e)},
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
    
    def get_active_symbols(self) -> SymbolsResponse:
        """
        Get list of all active symbols with their information.
        
        Returns:
            SymbolsResponse with list of active symbols and metadata
            
        Raises:
            HTTPException: If data retrieval fails
        """
        try:
            logger.info("Fetching active symbols list")
            
            # Get all symbols from database
            cursor = self.symbols_collection.find({})
            all_symbols = list(cursor)
            
            # Filter and format active symbols
            active_symbols = []
            total_count = len(all_symbols)
            active_count = 0
            
            for symbol_doc in all_symbols:
                # Check if symbol is active (default to True if not specified)
                is_active = symbol_doc.get('active', True)
                
                if is_active:
                    active_count += 1
                    
                    # Format symbol info
                    symbol_info = SymbolInfo(
                        symbol=symbol_doc['symbol'],
                        organ_name=symbol_doc.get('organ_name', ''),
                        icb_name2=symbol_doc.get('icb_name2'),
                        icb_name3=symbol_doc.get('icb_name3'),
                        icb_name4=symbol_doc.get('icb_name4'),
                        com_type_code=symbol_doc.get('com_type_code'),
                        icb_code1=symbol_doc.get('icb_code1'),
                        icb_code2=symbol_doc.get('icb_code2'),
                        icb_code3=symbol_doc.get('icb_code3'),
                        icb_code4=symbol_doc.get('icb_code4'),
                        active=is_active,
                        created_at=self._format_timestamp(symbol_doc.get('created_at')),
                        updated_at=self._format_timestamp(symbol_doc.get('updated_at'))
                    )
                    active_symbols.append(symbol_info)
            
            # Sort symbols by symbol code for consistent ordering
            active_symbols.sort(key=lambda x: x.symbol)
            
            response = SymbolsResponse(
                symbols=active_symbols,
                total=total_count,
                active_count=active_count
            )
            
            logger.info(f"Retrieved {active_count} active symbols out of {total_count} total")
            return response
            
        except Exception as e:
            logger.error(
                f"Error retrieving active symbols",
                context={'error': str(e)},
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
    
    def _get_latest_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get latest price data for symbol."""
        try:
            return self.price_collection.find_one(
                {'symbol': symbol},
                sort=[('timestamp', -1)]
            )
        except Exception as e:
            logger.error(f"Error getting latest price: {str(e)}")
            return None
    
    def _format_price_data(self, price_doc: Dict[str, Any]) -> PriceData:
        """Format price document to PriceData model."""
        # Convert epoch timestamp to ISO format for API response
        timestamp = price_doc['timestamp']
        if isinstance(timestamp, (int, float)):
            timestamp_str = epoch_to_iso(timestamp)
        else:
            timestamp_str = str(timestamp)  # Already ISO format
            
        return PriceData(
            timestamp=timestamp_str,
            open=price_doc['open'],
            close=price_doc['close'],
            high=price_doc['high'],
            low=price_doc['low'],
            volume=price_doc['volume']
        )
    
    def _format_ai_analysis(self, ai_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Format AI/ML analysis document."""
        # Convert epoch timestamp to ISO format for API response
        timestamp = ai_doc['timestamp']
        if isinstance(timestamp, (int, float)):
            timestamp_str = epoch_to_iso(timestamp)
        else:
            timestamp_str = str(timestamp)  # Already ISO format
            
        return {
            'timestamp': timestamp_str,
            'trend_prediction': ai_doc['trend_prediction'],
            'risk_score': ai_doc['risk_score'],
            'technical_score': ai_doc['technical_score'],
            'indicators': ai_doc.get('indicators', {})
        }
    
    def _format_llm_analysis(self, llm_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Format LLM analysis document."""
        # Convert epoch timestamp to ISO format for API response
        timestamp = llm_doc['timestamp']
        if isinstance(timestamp, (int, float)):
            timestamp_str = epoch_to_iso(timestamp)
        else:
            timestamp_str = str(timestamp)  # Already ISO format
            
        return {
            'timestamp': timestamp_str,
            'sentiment': llm_doc['sentiment'],
            'summary': llm_doc.get('summary', ''),
            'influence_score': llm_doc.get('influence_score', 0.0),
            'articles_analyzed': llm_doc.get('articles_analyzed', 0)
        }
    
    def _format_component_scores(self, final_score_doc: Dict[str, Any]) -> ComponentScores:
        """Format component scores."""
        components = final_score_doc.get('components', {})
        return ComponentScores(
            technical_score=components.get('technical_score', 0.0),
            risk_score=components.get('risk_score', 0.0),
            sentiment_score=components.get('sentiment_score', 0.0)
        )
    
    def _format_alerts(self, alerts: List[Dict[str, Any]]) -> List[Alert]:
        """Format alerts list."""
        return [
            Alert(
                type=alert['type'],
                priority=alert['priority'],
                message=alert['message']
            )
            for alert in alerts
        ]
    
    def _format_timestamp(self, timestamp: Any) -> Optional[str]:
        """Format timestamp to ISO string for API response."""
        if timestamp is None:
            return None
        
        if isinstance(timestamp, (int, float)):
            return epoch_to_iso(timestamp)
        else:
            return str(timestamp)  # Already ISO format


# Create FastAPI application
app = FastAPI(
    title="Vietnam Stock AI Backend API",
    description="REST API for accessing stock analysis data",
    version="1.0.0"
)

# Initialize MongoDB client and API service
mongo_client = MongoClient(config.MONGODB_URI)
api_service = APIService(mongo_client, config.MONGODB_DATABASE)

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify API and database connectivity.
    
    Returns:
        Dict with status information including API status and database connectivity
    """
    try:
        # Test database connectivity
        mongo_client.admin.command('ping')
        db_status = "healthy"
        db_message = "Database connection successful"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"
        db_message = f"Database connection failed: {str(e)}"
    
    # Overall status
    overall_status = "healthy" if db_status == "healthy" else "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),  # Keep ISO for API response
        "version": "1.0.0",
        "services": {
            "api": "healthy",
            "database": {
                "status": db_status,
                "message": db_message
            }
        }
    }

# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Vietnam Stock AI Backend API",
        "version": "1.0.0",
        "endpoints": {
            "stock_summary": "/stock/{symbol}/summary",
            "alerts": "/alerts",
            "historical_analysis": "/stock/{symbol}/history",
            "active_symbols": "/symbols"
        }
    }


@app.get("/stock/{symbol}/summary", response_model=StockSummary)
async def get_stock_summary(symbol: str):
    """
    Get comprehensive stock summary.
    
    Returns current price, AI/ML analysis, LLM analysis, final score,
    recommendation, and alerts for the specified stock symbol.
    """
    return api_service.get_stock_summary(symbol.upper())


@app.get("/alerts", response_model=AlertResponse)
async def get_alerts(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of alerts to return"),
    offset: int = Query(0, ge=0, description="Number of alerts to skip for pagination")
):
    """
    Get active alerts sorted by priority and timestamp.
    
    Alerts are sorted first by priority (high > medium > low),
    then by timestamp (most recent first).
    """
    return api_service.get_alerts(limit=limit, offset=offset)


@app.get("/stock/{symbol}/history", response_model=HistoricalData)
async def get_historical_analysis(
    symbol: str,
    start_date: str = Query(..., description="Start date in ISO format (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date in ISO format (YYYY-MM-DD)")
):
    """
    Get historical analysis data for specified date range.
    
    Returns time-series data of final scores, recommendations, and component scores
    for the specified stock symbol within the given date range.
    """
    return api_service.get_historical_analysis(
        symbol.upper(),
        start_date,
        end_date
    )


@app.get("/symbols", response_model=SymbolsResponse)
async def get_active_symbols():
    """
    Get list of all active symbols with their information.
    
    Returns comprehensive information about all active stock symbols including:
    - Symbol code
    - Company name (organ_name)
    - Industry classification (ICB codes and names)
    - Company type code
    - Active status
    - Creation and update timestamps
    """
    return api_service.get_active_symbols()


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions with proper error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    logger.error(
        "Unhandled exception in API",
        context={'error': str(exc)},
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "status_code": 500
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
