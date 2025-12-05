from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import aiohttp
import asyncio
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import redis.asyncio as redis

from .models import *
from .auth import User, require_basic, require_premium
from ..config.settings import settings

router = APIRouter(prefix="/analysis", tags=["analysis"])

class AnalysisService:
    """Analysis results and scoring service"""
    
    def __init__(self):
        self.mongo_client = AsyncIOMotorClient(settings.mongodb_url)
        self.db = self.mongo_client[settings.database_name]
        self.redis_client = redis.from_url(settings.redis_url)
        self.cache_ttl = 180  # 3 minutes for analysis results
    
    async def get_stock_score(self, symbol: str, include_explanation: bool = True, 
                            include_components: bool = False) -> ScoreResponse:
        """Get comprehensive score for a stock"""
        # Try cache first
        cache_key = f"score:{symbol}:{include_explanation}:{include_components}"
        cached = await self.redis_client.get(cache_key)
        
        if cached:
            import json
            return ScoreResponse(**json.loads(cached))
        
        # Get from aggregation service
        async with aiohttp.ClientSession() as session:
            try:
                payload = {
                    "stock_symbol": symbol,
                    "stock_data": {}
                }
                
                async with session.post(f"{settings.aggregation_url}/score/calculate", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        score_data = data["score"]
                        
                        # Build response
                        score_response = ScoreResponse(
                            stock_symbol=score_data["stock_symbol"],
                            final_score=score_data["final_score"],
                            recommendation=score_data["recommendation"],
                            confidence=score_data["confidence"],
                            technical_score=score_data["technical_score"],
                            sentiment_score=score_data["sentiment_score"],
                            risk_score=score_data["risk_score"],
                            timestamp=datetime.fromisoformat(score_data["timestamp"]),
                            explanation=data.get("explanation") if include_explanation else None,
                            components=ScoreComponents(**score_data["components"]) if include_components else None
                        )
                        
                        # Cache result
                        await self.redis_client.setex(
                            cache_key,
                            self.cache_ttl,
                            score_response.json()
                        )
                        
                        return score_response
                    else:
                        raise HTTPException(status_code=response.status, detail="Score calculation failed")
                        
            except aiohttp.ClientError:
                raise HTTPException(status_code=503, detail="Analysis service unavailable")
    
    async def get_batch_scores(self, symbols: List[str], include_explanation: bool = False) -> Dict[str, ScoreResponse]:
        """Get scores for multiple stocks"""
        # Get from aggregation service
        async with aiohttp.ClientSession() as session:
            try:
                payload = {"stock_symbols": symbols}
                
                async with session.post(f"{settings.aggregation_url}/score/batch", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = {}
                        
                        for symbol, result_data in data["results"].items():
                            if "error" not in result_data:
                                score_data = result_data["score"]
                                results[symbol] = ScoreResponse(
                                    stock_symbol=score_data["stock_symbol"],
                                    final_score=score_data["final_score"],
                                    recommendation=score_data["recommendation"],
                                    confidence=score_data["confidence"],
                                    technical_score=score_data["technical_score"],
                                    sentiment_score=score_data["sentiment_score"],
                                    risk_score=score_data["risk_score"],
                                    timestamp=datetime.fromisoformat(score_data["timestamp"]),
                                    explanation=result_data.get("explanation") if include_explanation else None
                                )
                        
                        return results
                    else:
                        raise HTTPException(status_code=response.status, detail="Batch score calculation failed")
                        
            except aiohttp.ClientError:
                raise HTTPException(status_code=503, detail="Analysis service unavailable")
    
    async def compare_stocks(self, symbols: List[str], metrics: List[str]) -> ComparisonResult:
        """Compare multiple stocks across specified metrics"""
        # Get scores for all stocks
        scores = await self.get_batch_scores(symbols)
        
        # Extract metrics
        comparison_data = {}
        for metric in metrics:
            comparison_data[metric] = []
            for symbol in symbols:
                if symbol in scores:
                    score = scores[symbol]
                    if metric == "final_score":
                        comparison_data[metric].append(score.final_score)
                    elif metric == "technical_score":
                        comparison_data[metric].append(score.technical_score)
                    elif metric == "sentiment_score":
                        comparison_data[metric].append(score.sentiment_score)
                    elif metric == "risk_score":
                        comparison_data[metric].append(score.risk_score)
                    elif metric == "confidence":
                        comparison_data[metric].append(score.confidence)
                    else:
                        comparison_data[metric].append(0)
                else:
                    comparison_data[metric].append(0)
        
        # Create rankings
        rankings = {}
        for metric in metrics:
            # Sort symbols by metric value (descending for most metrics, ascending for risk)
            reverse_sort = metric != "risk_score"
            sorted_pairs = sorted(zip(symbols, comparison_data[metric]), 
                                key=lambda x: x[1], reverse=reverse_sort)
            rankings[metric] = [pair[0] for pair in sorted_pairs]
        
        # Generate summary
        summary = {
            "best_overall": rankings.get("final_score", symbols)[0] if "final_score" in rankings else None,
            "lowest_risk": rankings.get("risk_score", symbols)[0] if "risk_score" in rankings else None,
            "highest_confidence": rankings.get("confidence", symbols)[0] if "confidence" in rankings else None,
            "comparison_timestamp": datetime.now()
        }
        
        return ComparisonResult(
            stocks=symbols,
            metrics=comparison_data,
            rankings=rankings,
            summary=summary
        )
    
    async def get_analysis_history(self, symbol: str, analysis_type: str = None, 
                                 days: int = 30, limit: int = 100) -> List[AnalysisHistory]:
        """Get historical analysis results"""
        # Build query
        query = {"stock_symbol": symbol}
        if analysis_type:
            query["analysis_type"] = analysis_type
        
        # Date filter
        start_date = datetime.now() - timedelta(days=days)
        query["timestamp"] = {"$gte": start_date}
        
        # Get from database
        cursor = self.db.analysis_history.find(query).sort("timestamp", -1).limit(limit)
        history_data = await cursor.to_list(length=limit)
        
        return [
            AnalysisHistory(
                stock_symbol=data["stock_symbol"],
                analysis_type=data["analysis_type"],
                timestamp=data["timestamp"],
                result=data["result"],
                confidence=data.get("confidence", 0),
                model_version=data.get("model_version", "unknown")
            )
            for data in history_data
        ]
    
    async def get_ai_prediction(self, symbol: str) -> Dict[str, Any]:
        """Get AI prediction from AI Analysis Service"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{settings.ai_analysis_url}/predict/{symbol}") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise HTTPException(status_code=response.status, detail="AI prediction failed")
            except aiohttp.ClientError:
                raise HTTPException(status_code=503, detail="AI Analysis service unavailable")
    
    async def get_sentiment_analysis(self, symbol: str) -> Dict[str, Any]:
        """Get sentiment analysis from LLM Analysis Service"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{settings.llm_analysis_url}/analyze/recent/{symbol}") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise HTTPException(status_code=response.status, detail="Sentiment analysis failed")
            except aiohttp.ClientError:
                raise HTTPException(status_code=503, detail="LLM Analysis service unavailable")
    
    async def trigger_analysis_update(self, symbol: str, background_tasks: BackgroundTasks):
        """Trigger analysis update for a stock"""
        background_tasks.add_task(self._update_analysis, symbol)
        return {"message": f"Analysis update triggered for {symbol}"}
    
    async def _update_analysis(self, symbol: str):
        """Background task to update analysis"""
        try:
            # Trigger score recalculation
            async with aiohttp.ClientSession() as session:
                payload = {"stock_symbol": symbol}
                await session.post(f"{settings.aggregation_url}/score/calculate", json=payload)
                
            # Clear cache
            cache_pattern = f"score:{symbol}:*"
            # Note: In production, you'd use Redis SCAN to find and delete matching keys
            
        except Exception as e:
            print(f"Error updating analysis for {symbol}: {e}")

# Initialize service
analysis_service = AnalysisService()

@router.get("/score/{symbol}", response_model=ScoreResponse)
async def get_stock_score(
    symbol: str,
    include_explanation: bool = True,
    include_components: bool = False,
    user: User = Depends(require_basic)
):
    """Get comprehensive analysis score for a stock"""
    return await analysis_service.get_stock_score(
        symbol.upper(), include_explanation, include_components
    )

@router.post("/score/batch", response_model=Dict[str, ScoreResponse])
async def get_batch_scores(
    request: BatchScoreRequest,
    user: User = Depends(require_premium)
):
    """Get scores for multiple stocks (Premium feature)"""
    symbols = [s.upper() for s in request.stock_symbols]
    return await analysis_service.get_batch_scores(symbols, request.include_explanation)

@router.post("/compare", response_model=ComparisonResult)
async def compare_stocks(
    request: ComparisonRequest,
    user: User = Depends(require_premium)
):
    """Compare multiple stocks across specified metrics"""
    symbols = [s.upper() for s in request.stock_symbols]
    return await analysis_service.compare_stocks(symbols, request.metrics)

@router.get("/history/{symbol}", response_model=List[AnalysisHistory])
async def get_analysis_history(
    symbol: str,
    analysis_type: Optional[str] = None,
    days: int = 30,
    limit: int = 100,
    user: User = Depends(require_basic)
):
    """Get historical analysis results for a stock"""
    return await analysis_service.get_analysis_history(
        symbol.upper(), analysis_type, days, limit
    )

@router.get("/ai/{symbol}")
async def get_ai_prediction(
    symbol: str,
    user: User = Depends(require_basic)
):
    """Get AI prediction for a stock"""
    return await analysis_service.get_ai_prediction(symbol.upper())

@router.get("/sentiment/{symbol}")
async def get_sentiment_analysis(
    symbol: str,
    user: User = Depends(require_basic)
):
    """Get sentiment analysis for a stock"""
    return await analysis_service.get_sentiment_analysis(symbol.upper())

@router.post("/update/{symbol}")
async def trigger_analysis_update(
    symbol: str,
    background_tasks: BackgroundTasks,
    user: User = Depends(require_premium)
):
    """Trigger analysis update for a stock (Premium feature)"""
    return await analysis_service.trigger_analysis_update(symbol.upper(), background_tasks)