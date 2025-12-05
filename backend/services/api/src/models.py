from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

# Request Models
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=8)

class StockSearchRequest(BaseModel):
    query: Optional[str] = None
    sector: Optional[str] = None
    market_cap_min: Optional[float] = None
    market_cap_max: Optional[float] = None
    limit: int = Field(default=20, le=100)
    offset: int = Field(default=0, ge=0)

class PriceHistoryRequest(BaseModel):
    stock_symbol: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    interval: str = Field(default="1d", regex=r'^(1m|5m|15m|30m|1h|1d|1w|1M)$')
    limit: int = Field(default=100, le=1000)

class ScoreRequest(BaseModel):
    stock_symbol: str
    include_explanation: bool = True
    include_components: bool = False

class BatchScoreRequest(BaseModel):
    stock_symbols: List[str] = Field(..., max_items=50)
    include_explanation: bool = False
    include_components: bool = False

class ComparisonRequest(BaseModel):
    stock_symbols: List[str] = Field(..., min_items=2, max_items=10)
    metrics: List[str] = Field(default=["final_score", "recommendation", "risk_score"])

# Response Models
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

class StockInfo(BaseModel):
    symbol: str
    name: str
    sector: str
    industry: str
    market_cap: float
    price: float
    change: float
    change_percent: float
    volume: int
    avg_volume: int
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    last_updated: datetime

class PriceData(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: Optional[float]

class TechnicalIndicators(BaseModel):
    rsi: Optional[float]
    macd: Optional[float]
    macd_signal: Optional[float]
    bb_upper: Optional[float]
    bb_middle: Optional[float]
    bb_lower: Optional[float]
    sma_20: Optional[float]
    sma_50: Optional[float]
    ema_12: Optional[float]
    ema_26: Optional[float]

class ScoreComponents(BaseModel):
    technical: Dict[str, Any]
    sentiment: Dict[str, Any]
    risk: Dict[str, Any]
    weights: Dict[str, Any]

class ScoreResponse(BaseModel):
    stock_symbol: str
    final_score: float
    recommendation: str
    confidence: float
    technical_score: float
    sentiment_score: float
    risk_score: float
    timestamp: datetime
    explanation: Optional[Dict[str, Any]] = None
    components: Optional[ScoreComponents] = None

class NewsItem(BaseModel):
    id: str
    title: str
    content: str
    source: str
    published_at: datetime
    stock_symbols: List[str]
    sentiment: Optional[str]
    sentiment_score: Optional[float]
    impact_score: Optional[float]

class AlertResponse(BaseModel):
    id: str
    alert_type: str
    priority: str
    stock_symbol: str
    title: str
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    acknowledged: bool

class AnalysisHistory(BaseModel):
    stock_symbol: str
    analysis_type: str
    timestamp: datetime
    result: Dict[str, Any]
    confidence: float
    model_version: str

class MarketOverview(BaseModel):
    total_stocks: int
    active_alerts: int
    top_gainers: List[StockInfo]
    top_losers: List[StockInfo]
    most_active: List[StockInfo]
    market_sentiment: str
    last_updated: datetime

class ComparisonResult(BaseModel):
    stocks: List[str]
    metrics: Dict[str, List[float]]
    rankings: Dict[str, List[str]]
    summary: Dict[str, Any]

class APIUsageStats(BaseModel):
    user_id: str
    requests_today: int
    requests_this_hour: int
    daily_limit: int
    hourly_limit: int
    remaining_daily: int
    remaining_hourly: int

class HealthStatus(BaseModel):
    status: str
    timestamp: datetime
    version: str
    uptime: float
    services: Dict[str, str]
    performance: Dict[str, float]

# Pagination Models
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

class StockListResponse(PaginatedResponse):
    items: List[StockInfo]

class NewsListResponse(PaginatedResponse):
    items: List[NewsItem]

class AlertListResponse(PaginatedResponse):
    items: List[AlertResponse]

class HistoryListResponse(PaginatedResponse):
    items: List[AnalysisHistory]

# Error Models
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime

class ValidationError(BaseModel):
    field: str
    message: str
    value: Any

class ValidationErrorResponse(BaseModel):
    error: str = "validation_error"
    message: str
    errors: List[ValidationError]
    timestamp: datetime

# WebSocket Models
class WSMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime

class WSSubscription(BaseModel):
    action: str  # subscribe, unsubscribe
    channels: List[str]  # stock_updates, alerts, news
    stocks: Optional[List[str]] = None

# Filter and Sort Models
class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class StockSortBy(str, Enum):
    SYMBOL = "symbol"
    NAME = "name"
    PRICE = "price"
    CHANGE = "change"
    VOLUME = "volume"
    MARKET_CAP = "market_cap"
    SCORE = "score"

class NewsSortBy(str, Enum):
    PUBLISHED_AT = "published_at"
    RELEVANCE = "relevance"
    SENTIMENT_SCORE = "sentiment_score"

class AlertSortBy(str, Enum):
    TIMESTAMP = "timestamp"
    PRIORITY = "priority"
    STOCK_SYMBOL = "stock_symbol"