from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

from .llm_client import LLMClient
from .prompt_templates import PromptManager
from .text_processor import TextProcessor
from .news_analyzer import NewsAnalyzer, BatchAnalysisResult
from .quality_control import QualityController
from ..config.settings import settings

# Pydantic models
class NewsItem(BaseModel):
    content: str
    stock_symbol: str
    company_name: str
    sector: Optional[str] = ""
    current_price: Optional[float] = 0
    market_cap: Optional[str] = ""
    market_context: Optional[str] = ""

class AnalysisRequest(BaseModel):
    news_item: NewsItem
    analysis_types: Optional[List[str]] = ["sentiment", "summary"]

class BatchAnalysisRequest(BaseModel):
    news_items: List[NewsItem]
    analysis_types: Optional[List[str]] = ["sentiment"]

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    usage_stats: Dict[str, Any]

# Initialize FastAPI app
app = FastAPI(
    title="LLM News Analysis Service",
    description="AI-powered Vietnamese stock news analysis using LLM",
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
llm_client = LLMClient(settings.get_llm_config())
prompt_manager = PromptManager()
text_processor = TextProcessor()
news_analyzer = NewsAnalyzer(llm_client, prompt_manager, text_processor)
quality_controller = QualityController()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    usage_stats = llm_client.get_usage_stats()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.service_version,
        usage_stats=usage_stats
    )

@app.post("/analyze/sentiment")
async def analyze_sentiment(request: AnalysisRequest):
    """Analyze news sentiment"""
    try:
        result = await news_analyzer.analyze_sentiment(
            request.news_item.content,
            request.news_item.stock_symbol,
            request.news_item.company_name,
            request.news_item.sector
        )
        
        # Validate result
        validation = quality_controller.validate_analysis_result(result)
        
        return {
            "analysis_result": result.__dict__,
            "quality_validation": {
                "is_valid": validation.is_valid,
                "quality_score": validation.quality_metrics.overall_score,
                "issues": validation.quality_metrics.issues
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze/summary")
async def analyze_summary(request: AnalysisRequest):
    """Generate news summary"""
    try:
        result = await news_analyzer.summarize_news(
            request.news_item.content,
            request.news_item.stock_symbol,
            request.news_item.company_name
        )
        
        validation = quality_controller.validate_analysis_result(result)
        
        return {
            "analysis_result": result.__dict__,
            "quality_validation": {
                "is_valid": validation.is_valid,
                "quality_score": validation.quality_metrics.overall_score,
                "issues": validation.quality_metrics.issues
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze/insights")
async def analyze_insights(request: AnalysisRequest):
    """Extract investment insights"""
    try:
        if request.news_item.current_price <= 0:
            raise ValueError("Current price is required for insights analysis")
        
        result = await news_analyzer.extract_insights(
            request.news_item.content,
            request.news_item.stock_symbol,
            request.news_item.company_name,
            request.news_item.current_price,
            request.news_item.market_cap
        )
        
        validation = quality_controller.validate_analysis_result(result)
        
        return {
            "analysis_result": result.__dict__,
            "quality_validation": {
                "is_valid": validation.is_valid,
                "quality_score": validation.quality_metrics.overall_score,
                "issues": validation.quality_metrics.issues
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze/market-impact")
async def analyze_market_impact(request: AnalysisRequest):
    """Analyze market impact"""
    try:
        result = await news_analyzer.analyze_market_impact(
            request.news_item.content,
            request.news_item.stock_symbol,
            request.news_item.company_name,
            request.news_item.sector,
            request.news_item.market_context
        )
        
        validation = quality_controller.validate_analysis_result(result)
        
        return {
            "analysis_result": result.__dict__,
            "quality_validation": {
                "is_valid": validation.is_valid,
                "quality_score": validation.quality_metrics.overall_score,
                "issues": validation.quality_metrics.issues
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze/comprehensive")
async def comprehensive_analysis(request: AnalysisRequest):
    """Run comprehensive analysis (all types)"""
    try:
        results = await news_analyzer.comprehensive_analysis(
            request.news_item.content,
            request.news_item.stock_symbol,
            request.news_item.company_name,
            request.news_item.sector,
            request.news_item.current_price,
            request.news_item.market_cap,
            request.news_item.market_context
        )
        
        # Validate all results
        validated_results = {}
        for analysis_type, result in results.items():
            if hasattr(result, '__dict__'):  # Valid NewsAnalysisResult
                validation = quality_controller.validate_analysis_result(result)
                validated_results[analysis_type] = {
                    "analysis_result": result.__dict__,
                    "quality_validation": {
                        "is_valid": validation.is_valid,
                        "quality_score": validation.quality_metrics.overall_score,
                        "issues": validation.quality_metrics.issues
                    }
                }
            else:  # Error result
                validated_results[analysis_type] = result
        
        return validated_results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/analyze/batch")
async def batch_analysis(request: BatchAnalysisRequest, background_tasks: BackgroundTasks):
    """Batch analyze multiple news items"""
    try:
        # Convert to dict format for batch processing
        news_items = []
        for item in request.news_items:
            news_items.append({
                'content': item.content,
                'stock_symbol': item.stock_symbol,
                'company_name': item.company_name,
                'sector': item.sector,
                'current_price': item.current_price,
                'market_cap': item.market_cap
            })
        
        batch_result = await news_analyzer.batch_analyze(news_items, request.analysis_types)
        
        # Validate batch results
        if batch_result.results:
            validation_summary = quality_controller.batch_validate(batch_result.results)
        else:
            validation_summary = {"message": "No results to validate"}
        
        return {
            "batch_summary": {
                "total_processed": batch_result.total_processed,
                "successful": batch_result.successful,
                "failed": batch_result.failed,
                "total_cost": batch_result.total_cost,
                "avg_processing_time": batch_result.avg_processing_time
            },
            "validation_summary": validation_summary,
            "results": [result.__dict__ for result in batch_result.results],
            "errors": batch_result.errors
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/usage/stats")
async def get_usage_stats():
    """Get current usage statistics"""
    return llm_client.get_usage_stats()

@app.get("/prompts/templates")
async def list_prompt_templates():
    """List available prompt templates"""
    return prompt_manager.list_templates()

@app.post("/text/process")
async def process_text(text: str):
    """Process and analyze text quality"""
    processed = text_processor.process_text(text)
    return {
        "original_length": len(processed.original),
        "cleaned_length": len(processed.cleaned),
        "language": processed.language,
        "quality_score": processed.quality_score,
        "chunk_count": len(processed.chunks),
        "entities": processed.metadata.get('entities', {}),
        "avg_chunk_quality": processed.metadata.get('avg_chunk_quality', 0)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )