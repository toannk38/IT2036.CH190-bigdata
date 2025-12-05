from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime
import websockets

from .score_calculator import ScoreCalculator, FinalScore
from .weight_optimizer import WeightOptimizer
from .alert_engine import AlertEngine, Alert, AlertRule, AlertType, AlertPriority
from .realtime_processor import RealtimeProcessor
from ..config.settings import settings

# Pydantic models
class StockRequest(BaseModel):
    stock_symbol: str
    stock_data: Optional[Dict[str, Any]] = None

class BatchScoreRequest(BaseModel):
    stock_symbols: List[str]

class WeightUpdateRequest(BaseModel):
    weights: Dict[str, Any]

class AlertRuleRequest(BaseModel):
    name: str
    alert_type: str
    conditions: Dict[str, Any]
    priority: str
    cooldown_minutes: int = 60

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    stats: Dict[str, Any]

# Initialize FastAPI app
app = FastAPI(
    title="Aggregation & Scoring Service",
    description="Final score calculation and alert generation for stock analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
score_calculator = ScoreCalculator(
    ai_analysis_url=settings.ai_analysis_url,
    llm_analysis_url=settings.llm_analysis_url
)
weight_optimizer = WeightOptimizer(score_calculator)
alert_engine = AlertEngine()
realtime_processor = RealtimeProcessor(
    mongodb_url=settings.mongodb_url,
    redis_url=settings.redis_url
)

# Global state
previous_scores = {}

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await realtime_processor.initialize()
    await realtime_processor.start_processing()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await realtime_processor.stop_processing()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    realtime_stats = await realtime_processor.get_realtime_stats()
    alert_stats = alert_engine.get_alert_statistics()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.service_version,
        stats={
            'realtime': realtime_stats,
            'alerts': alert_stats,
            'optimization_history': len(weight_optimizer.optimization_history)
        }
    )

@app.post("/score/calculate")
async def calculate_score(request: StockRequest):
    """Calculate comprehensive score for a stock"""
    try:
        # Calculate new score
        current_score = await score_calculator.calculate_comprehensive_score(
            request.stock_symbol, 
            request.stock_data
        )
        
        # Get previous score for comparison
        previous_score = previous_scores.get(request.stock_symbol)
        
        # Process alerts
        await alert_engine.process_score_update(
            current_score, 
            previous_score, 
            request.stock_symbol
        )
        
        # Update previous scores
        previous_scores[request.stock_symbol] = current_score
        
        # Queue real-time update
        await realtime_processor.queue_score_update(request.stock_symbol)
        
        # Generate explanation
        explanation = score_calculator.get_score_explanation(current_score)
        
        return {
            "score": current_score.__dict__,
            "explanation": explanation,
            "alerts": [alert.__dict__ for alert in alert_engine.get_active_alerts(request.stock_symbol)]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/score/batch")
async def calculate_batch_scores(request: BatchScoreRequest):
    """Calculate scores for multiple stocks"""
    try:
        tasks = []
        for symbol in request.stock_symbols:
            task = score_calculator.calculate_comprehensive_score(symbol)
            tasks.append((symbol, task))
        
        results = {}
        for symbol, task in tasks:
            try:
                score = await task
                results[symbol] = {
                    "score": score.__dict__,
                    "explanation": score_calculator.get_score_explanation(score)
                }
                
                # Update previous scores and process alerts
                previous_score = previous_scores.get(symbol)
                await alert_engine.process_score_update(score, previous_score, symbol)
                previous_scores[symbol] = score
                
            except Exception as e:
                results[symbol] = {"error": str(e)}
        
        return {
            "results": results,
            "summary": {
                "total_requested": len(request.stock_symbols),
                "successful": len([r for r in results.values() if "error" not in r]),
                "failed": len([r for r in results.values() if "error" in r])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/score/{stock_symbol}")
async def get_latest_score(stock_symbol: str):
    """Get latest calculated score for a stock"""
    if stock_symbol in previous_scores:
        score = previous_scores[stock_symbol]
        return {
            "score": score.__dict__,
            "explanation": score_calculator.get_score_explanation(score),
            "alerts": [alert.__dict__ for alert in alert_engine.get_active_alerts(stock_symbol)]
        }
    else:
        raise HTTPException(status_code=404, detail="No score found for this stock")

@app.post("/weights/optimize")
async def optimize_weights(stock_symbols: List[str] = None):
    """Optimize scoring weights using historical data"""
    try:
        if not stock_symbols:
            stock_symbols = list(previous_scores.keys())[:20]  # Use recent stocks
        
        if len(stock_symbols) < 5:
            raise ValueError("Need at least 5 stocks for optimization")
        
        result = await weight_optimizer.optimize_weights(stock_symbols)
        
        return {
            "optimization_result": {
                "optimal_weights": result.optimal_weights,
                "performance_metrics": result.performance_metrics,
                "improvement": result.improvement,
                "timestamp": result.timestamp
            },
            "applied": result.improvement > 0.05  # Applied if >5% improvement
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/weights/update")
async def update_weights(request: WeightUpdateRequest):
    """Manually update scoring weights"""
    try:
        score_calculator.update_weights(request.weights)
        return {
            "message": "Weights updated successfully",
            "new_weights": score_calculator.weights
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/weights/current")
async def get_current_weights():
    """Get current scoring weights"""
    return {
        "weights": score_calculator.weights,
        "optimization_summary": weight_optimizer.get_optimization_summary()
    }

@app.get("/alerts/active")
async def get_active_alerts(stock_symbol: Optional[str] = None):
    """Get active alerts"""
    alerts = alert_engine.get_active_alerts(stock_symbol)
    return {
        "alerts": [alert.__dict__ for alert in alerts],
        "count": len(alerts)
    }

@app.post("/alerts/acknowledge/{alert_id}")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""
    alert_engine.acknowledge_alert(alert_id)
    return {"message": "Alert acknowledged"}

@app.post("/alerts/rules")
async def add_alert_rule(request: AlertRuleRequest):
    """Add custom alert rule"""
    try:
        rule = AlertRule(
            id=f"custom_{int(datetime.now().timestamp())}",
            name=request.name,
            alert_type=AlertType(request.alert_type),
            conditions=request.conditions,
            priority=AlertPriority(request.priority),
            cooldown_minutes=request.cooldown_minutes
        )
        
        alert_engine.add_alert_rule(rule)
        
        return {
            "message": "Alert rule added successfully",
            "rule_id": rule.id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/alerts/rules/{rule_id}")
async def remove_alert_rule(rule_id: str):
    """Remove alert rule"""
    alert_engine.remove_alert_rule(rule_id)
    return {"message": "Alert rule removed"}

@app.get("/alerts/statistics")
async def get_alert_statistics():
    """Get alert statistics"""
    return alert_engine.get_alert_statistics()

@app.post("/realtime/price-update")
async def price_update(stock_symbol: str, price_data: Dict[str, Any]):
    """Receive price update for real-time processing"""
    await realtime_processor.queue_price_update(stock_symbol, price_data)
    return {"message": "Price update queued"}

@app.post("/realtime/news-update")
async def news_update(stock_symbol: str, news_data: Dict[str, Any]):
    """Receive news update for real-time processing"""
    await realtime_processor.queue_news_update(stock_symbol, news_data)
    return {"message": "News update queued"}

@app.get("/realtime/stats")
async def get_realtime_stats():
    """Get real-time processing statistics"""
    return await realtime_processor.get_realtime_stats()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    await realtime_processor.handle_websocket_connection(websocket, "/ws")

# Background task for automatic weight optimization
async def auto_optimize_weights():
    """Background task for automatic weight optimization"""
    while True:
        try:
            if len(previous_scores) >= 10:  # Need minimum stocks
                stock_symbols = list(previous_scores.keys())
                result = await weight_optimizer.auto_optimize(stock_symbols)
                if result:
                    print(f"Weights auto-optimized with {result.improvement:.2%} improvement")
        except Exception as e:
            print(f"Auto-optimization error: {e}")
        
        await asyncio.sleep(3600)  # Run every hour

# Start background tasks
@app.on_event("startup")
async def start_background_tasks():
    asyncio.create_task(auto_optimize_weights())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )