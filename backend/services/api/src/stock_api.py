from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import aiohttp
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis

from .models import *
from .auth import User, require_any, require_basic
from ..config.settings import settings

router = APIRouter(prefix="/stocks", tags=["stocks"])

class StockService:
    """Stock information and market data service"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(settings.mongodb_url)
        self.db = self.mongo_client[settings.database_name]
        self.redis_client = redis.from_url(settings.redis_url)
        self.cache_ttl = 300  # 5 minutes
    
    async def get_stock_list(self, search: StockSearchRequest) -> StockListResponse:
        """Get paginated list of stocks with filtering"""
        # Build query
        query = {}
        if search.query:
            query["$or"] = [
                {"symbol": {"$regex": search.query, "$options": "i"}},
                {"name": {"$regex": search.query, "$options": "i"}}
            ]
        if search.sector:
            query["sector"] = search.sector
        if search.market_cap_min or search.market_cap_max:
            market_cap_filter = {}
            if search.market_cap_min:
                market_cap_filter["$gte"] = search.market_cap_min
            if search.market_cap_max:
                market_cap_filter["$lte"] = search.market_cap_max
            query["market_cap"] = market_cap_filter
        
        # Get total count
        total = await self.db.stocks.count_documents(query)
        
        # Get paginated results
        cursor = self.db.stocks.find(query).skip(search.offset).limit(search.limit)
        stocks_data = await cursor.to_list(length=search.limit)
        
        # Convert to StockInfo models
        stocks = []
        for stock_data in stocks_data:
            stocks.append(StockInfo(
                symbol=stock_data["symbol"],
                name=stock_data["name"],
                sector=stock_data.get("sector", "Unknown"),
                industry=stock_data.get("industry", "Unknown"),
                market_cap=stock_data.get("market_cap", 0),
                price=stock_data.get("current_price", 0),
                change=stock_data.get("price_change", 0),
                change_percent=stock_data.get("price_change_percent", 0),
                volume=stock_data.get("volume", 0),
                avg_volume=stock_data.get("avg_volume", 0),
                pe_ratio=stock_data.get("pe_ratio"),
                dividend_yield=stock_data.get("dividend_yield"),
                last_updated=stock_data.get("last_updated", datetime.now())
            ))
        
        pages = (total + search.limit - 1) // search.limit
        page = (search.offset // search.limit) + 1
        
        return StockListResponse(
            items=stocks,
            total=total,
            page=page,
            size=search.limit,
            pages=pages
        )
    
    async def get_stock_detail(self, symbol: str) -> StockInfo:
        """Get detailed information for a specific stock"""
        # Try cache first
        cache_key = f"stock_detail:{symbol}"
        cached = await self.redis_client.get(cache_key)
        
        if cached:
            import json
            stock_data = json.loads(cached)
        else:
            # Get from database
            stock_data = await self.db.stocks.find_one({"symbol": symbol})
            if not stock_data:
                raise HTTPException(status_code=404, detail="Stock not found")
            
            # Cache result
            import json
            await self.redis_client.setex(
                cache_key, 
                self.cache_ttl, 
                json.dumps(stock_data, default=str)
            )
        
        return StockInfo(
            symbol=stock_data["symbol"],
            name=stock_data["name"],
            sector=stock_data.get("sector", "Unknown"),
            industry=stock_data.get("industry", "Unknown"),
            market_cap=stock_data.get("market_cap", 0),
            price=stock_data.get("current_price", 0),
            change=stock_data.get("price_change", 0),
            change_percent=stock_data.get("price_change_percent", 0),
            volume=stock_data.get("volume", 0),
            avg_volume=stock_data.get("avg_volume", 0),
            pe_ratio=stock_data.get("pe_ratio"),
            dividend_yield=stock_data.get("dividend_yield"),
            last_updated=datetime.fromisoformat(stock_data.get("last_updated", datetime.now().isoformat()))
        )
    
    async def get_price_history(self, request: PriceHistoryRequest) -> List[PriceData]:
        """Get historical price data"""
        # Build date filter
        date_filter = {"symbol": request.stock_symbol}
        if request.start_date:
            date_filter["timestamp"] = {"$gte": request.start_date}
        if request.end_date:
            if "timestamp" in date_filter:
                date_filter["timestamp"]["$lte"] = request.end_date
            else:
                date_filter["timestamp"] = {"$lte": request.end_date}
        
        # Get price data
        cursor = self.db.price_history.find(date_filter).sort("timestamp", -1).limit(request.limit)
        price_data = await cursor.to_list(length=request.limit)
        
        if not price_data:
            raise HTTPException(status_code=404, detail="No price data found")
        
        return [
            PriceData(
                timestamp=data["timestamp"],
                open=data["open"],
                high=data["high"],
                low=data["low"],
                close=data["close"],
                volume=data["volume"],
                adj_close=data.get("adj_close")
            )
            for data in price_data
        ]
    
    async def get_technical_indicators(self, symbol: str) -> TechnicalIndicators:
        """Get latest technical indicators"""
        # Get from AI analysis service
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{settings.ai_analysis_url}/features/{symbol}") as response:
                    if response.status == 200:
                        data = await response.json()
                        features = data.get("features", {})
                        
                        return TechnicalIndicators(
                            rsi=features.get("rsi"),
                            macd=features.get("macd"),
                            macd_signal=features.get("macd_signal"),
                            bb_upper=features.get("bb_upper"),
                            bb_middle=features.get("bb_middle"),
                            bb_lower=features.get("bb_lower"),
                            sma_20=features.get("sma_20"),
                            sma_50=features.get("sma_50"),
                            ema_12=features.get("ema_12"),
                            ema_26=features.get("ema_26")
                        )
                    else:
                        raise HTTPException(status_code=404, detail="Technical indicators not available")
            except aiohttp.ClientError:
                raise HTTPException(status_code=503, detail="Technical analysis service unavailable")
    
    async def get_market_overview(self) -> MarketOverview:
        """Get market overview with top movers"""
        # Get top gainers
        gainers_cursor = self.db.stocks.find({"price_change_percent": {"$gt": 0}}).sort("price_change_percent", -1).limit(5)
        gainers_data = await gainers_cursor.to_list(length=5)
        
        # Get top losers
        losers_cursor = self.db.stocks.find({"price_change_percent": {"$lt": 0}}).sort("price_change_percent", 1).limit(5)
        losers_data = await losers_cursor.to_list(length=5)
        
        # Get most active
        active_cursor = self.db.stocks.find().sort("volume", -1).limit(5)
        active_data = await active_cursor.to_list(length=5)
        
        # Convert to StockInfo
        def to_stock_info(data):
            return StockInfo(
                symbol=data["symbol"],
                name=data["name"],
                sector=data.get("sector", "Unknown"),
                industry=data.get("industry", "Unknown"),
                market_cap=data.get("market_cap", 0),
                price=data.get("current_price", 0),
                change=data.get("price_change", 0),
                change_percent=data.get("price_change_percent", 0),
                volume=data.get("volume", 0),
                avg_volume=data.get("avg_volume", 0),
                pe_ratio=data.get("pe_ratio"),
                dividend_yield=data.get("dividend_yield"),
                last_updated=data.get("last_updated", datetime.now())
            )
        
        # Get total stock count
        total_stocks = await self.db.stocks.count_documents({})
        
        # Get active alerts count
        active_alerts = await self.db.alerts.count_documents({"acknowledged": False})
        
        # Calculate market sentiment (simplified)
        positive_count = await self.db.stocks.count_documents({"price_change_percent": {"$gt": 0}})
        total_with_change = await self.db.stocks.count_documents({"price_change_percent": {"$exists": True}})
        
        if total_with_change > 0:
            positive_ratio = positive_count / total_with_change
            if positive_ratio > 0.6:
                market_sentiment = "Bullish"
            elif positive_ratio < 0.4:
                market_sentiment = "Bearish"
            else:
                market_sentiment = "Neutral"
        else:
            market_sentiment = "Unknown"
        
        return MarketOverview(
            total_stocks=total_stocks,
            active_alerts=active_alerts,
            top_gainers=[to_stock_info(data) for data in gainers_data],
            top_losers=[to_stock_info(data) for data in losers_data],
            most_active=[to_stock_info(data) for data in active_data],
            market_sentiment=market_sentiment,
            last_updated=datetime.now()
        )

# Initialize service
stock_service = StockService()

@router.get("/", response_model=StockListResponse)
async def get_stocks(
    query: Optional[str] = Query(None, description="Search by symbol or name"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    market_cap_min: Optional[float] = Query(None, description="Minimum market cap"),
    market_cap_max: Optional[float] = Query(None, description="Maximum market cap"),
    limit: int = Query(20, le=100, description="Number of results per page"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    user: User = Depends(require_any)
):
    """Get list of stocks with filtering and pagination"""
    search_request = StockSearchRequest(
        query=query,
        sector=sector,
        market_cap_min=market_cap_min,
        market_cap_max=market_cap_max,
        limit=limit,
        offset=offset
    )
    return await stock_service.get_stock_list(search_request)

@router.get("/{symbol}", response_model=StockInfo)
async def get_stock_detail(
    symbol: str,
    user: User = Depends(require_any)
):
    """Get detailed information for a specific stock"""
    return await stock_service.get_stock_detail(symbol.upper())

@router.get("/{symbol}/history", response_model=List[PriceData])
async def get_price_history(
    symbol: str,
    start_date: Optional[datetime] = Query(None, description="Start date for history"),
    end_date: Optional[datetime] = Query(None, description="End date for history"),
    interval: str = Query("1d", regex=r'^(1m|5m|15m|30m|1h|1d|1w|1M)$'),
    limit: int = Query(100, le=1000, description="Maximum number of data points"),
    user: User = Depends(require_basic)
):
    """Get historical price data for a stock"""
    request = PriceHistoryRequest(
        stock_symbol=symbol.upper(),
        start_date=start_date,
        end_date=end_date,
        interval=interval,
        limit=limit
    )
    return await stock_service.get_price_history(request)

@router.get("/{symbol}/indicators", response_model=TechnicalIndicators)
async def get_technical_indicators(
    symbol: str,
    user: User = Depends(require_basic)
):
    """Get technical indicators for a stock"""
    return await stock_service.get_technical_indicators(symbol.upper())

@router.get("/market/overview", response_model=MarketOverview)
async def get_market_overview(
    user: User = Depends(require_any)
):
    """Get market overview with top movers and statistics"""
    return await stock_service.get_market_overview()