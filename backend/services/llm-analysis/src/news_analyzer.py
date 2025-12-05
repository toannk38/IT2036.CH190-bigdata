import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from .llm_client import LLMClient, LLMResponse
from .prompt_templates import PromptManager, PromptType
from .text_processor import TextProcessor, ProcessedText

@dataclass
class NewsAnalysisResult:
    news_id: str
    stock_symbol: str
    analysis_type: str
    result: Dict[str, Any]
    confidence: float
    processing_time: float
    model_used: str
    cost: float
    timestamp: datetime
    quality_score: float

@dataclass
class BatchAnalysisResult:
    total_processed: int
    successful: int
    failed: int
    total_cost: float
    avg_processing_time: float
    results: List[NewsAnalysisResult]
    errors: List[Dict[str, Any]]

class NewsAnalyzer:
    """Main news analysis engine using LLM"""
    
    def __init__(self, llm_client: LLMClient, prompt_manager: PromptManager, text_processor: TextProcessor):
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
        self.text_processor = text_processor
        
        # Analysis configuration
        self.min_quality_threshold = 0.5
        self.min_confidence_threshold = 0.6
        self.max_retries = 2
        
    async def analyze_sentiment(self, news_content: str, stock_symbol: str, 
                              company_name: str, sector: str = "") -> NewsAnalysisResult:
        """Analyze news sentiment for a stock"""
        start_time = datetime.now()
        
        # Process text
        processed_text = self.text_processor.process_text(news_content)
        
        if processed_text.quality_score < self.min_quality_threshold:
            raise ValueError(f"Text quality too low: {processed_text.quality_score}")
        
        # Prepare prompt parameters
        prompt_params = {
            'news_content': processed_text.cleaned,
            'stock_symbol': stock_symbol,
            'company_name': company_name,
            'sector': sector
        }
        
        # Format prompt
        prompt = self.prompt_manager.format_prompt(PromptType.SENTIMENT_ANALYSIS, prompt_params)
        
        # Call LLM
        llm_response = await self.llm_client.analyze_text(prompt, provider="openai")
        
        # Parse and validate result
        try:
            result = json.loads(llm_response.content)
            confidence = result.get('confidence', 0) / 100.0  # Convert to 0-1 scale
            
            if confidence < self.min_confidence_threshold:
                raise ValueError(f"Confidence too low: {confidence}")
                
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from LLM")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return NewsAnalysisResult(
            news_id=f"news_{hash(news_content)}",
            stock_symbol=stock_symbol,
            analysis_type="sentiment",
            result=result,
            confidence=confidence,
            processing_time=processing_time,
            model_used=llm_response.model,
            cost=llm_response.cost,
            timestamp=datetime.now(),
            quality_score=processed_text.quality_score
        )
    
    async def summarize_news(self, news_content: str, stock_symbol: str, 
                           company_name: str) -> NewsAnalysisResult:
        """Generate news summary"""
        start_time = datetime.now()
        
        processed_text = self.text_processor.process_text(news_content)
        
        if processed_text.quality_score < self.min_quality_threshold:
            raise ValueError(f"Text quality too low: {processed_text.quality_score}")
        
        prompt_params = {
            'news_content': processed_text.cleaned,
            'stock_symbol': stock_symbol,
            'company_name': company_name
        }
        
        prompt = self.prompt_manager.format_prompt(PromptType.NEWS_SUMMARY, prompt_params)
        llm_response = await self.llm_client.analyze_text(prompt, provider="openai")
        
        try:
            result = json.loads(llm_response.content)
            confidence = result.get('relevance_score', 5) / 10.0  # Convert to 0-1 scale
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from LLM")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return NewsAnalysisResult(
            news_id=f"news_{hash(news_content)}",
            stock_symbol=stock_symbol,
            analysis_type="summary",
            result=result,
            confidence=confidence,
            processing_time=processing_time,
            model_used=llm_response.model,
            cost=llm_response.cost,
            timestamp=datetime.now(),
            quality_score=processed_text.quality_score
        )
    
    async def extract_insights(self, news_content: str, stock_symbol: str, 
                             company_name: str, current_price: float, 
                             market_cap: str) -> NewsAnalysisResult:
        """Extract investment insights"""
        start_time = datetime.now()
        
        processed_text = self.text_processor.process_text(news_content)
        
        if processed_text.quality_score < self.min_quality_threshold:
            raise ValueError(f"Text quality too low: {processed_text.quality_score}")
        
        prompt_params = {
            'news_content': processed_text.cleaned,
            'stock_symbol': stock_symbol,
            'company_name': company_name,
            'current_price': current_price,
            'market_cap': market_cap
        }
        
        prompt = self.prompt_manager.format_prompt(PromptType.INSIGHT_EXTRACTION, prompt_params)
        llm_response = await self.llm_client.analyze_text(prompt, provider="openai")
        
        try:
            result = json.loads(llm_response.content)
            # Calculate confidence based on number of insights and their quality
            insight_count = len(result.get('catalysts', [])) + len(result.get('risks', []))
            confidence = min(0.9, insight_count / 6)  # Normalize to 0-1
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from LLM")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return NewsAnalysisResult(
            news_id=f"news_{hash(news_content)}",
            stock_symbol=stock_symbol,
            analysis_type="insights",
            result=result,
            confidence=confidence,
            processing_time=processing_time,
            model_used=llm_response.model,
            cost=llm_response.cost,
            timestamp=datetime.now(),
            quality_score=processed_text.quality_score
        )
    
    async def analyze_market_impact(self, news_content: str, stock_symbol: str, 
                                  company_name: str, sector: str, 
                                  market_context: str) -> NewsAnalysisResult:
        """Analyze broader market impact"""
        start_time = datetime.now()
        
        processed_text = self.text_processor.process_text(news_content)
        
        if processed_text.quality_score < self.min_quality_threshold:
            raise ValueError(f"Text quality too low: {processed_text.quality_score}")
        
        prompt_params = {
            'news_content': processed_text.cleaned,
            'stock_symbol': stock_symbol,
            'company_name': company_name,
            'sector': sector,
            'market_context': market_context
        }
        
        prompt = self.prompt_manager.format_prompt(PromptType.MARKET_IMPACT, prompt_params)
        llm_response = await self.llm_client.analyze_text(prompt, provider="openai")
        
        try:
            result = json.loads(llm_response.content)
            # Map impact magnitude to confidence
            impact_map = {'HIGH': 0.9, 'MEDIUM': 0.7, 'LOW': 0.5}
            confidence = impact_map.get(result.get('impact_magnitude', 'LOW'), 0.5)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response from LLM")
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return NewsAnalysisResult(
            news_id=f"news_{hash(news_content)}",
            stock_symbol=stock_symbol,
            analysis_type="market_impact",
            result=result,
            confidence=confidence,
            processing_time=processing_time,
            model_used=llm_response.model,
            cost=llm_response.cost,
            timestamp=datetime.now(),
            quality_score=processed_text.quality_score
        )
    
    async def comprehensive_analysis(self, news_content: str, stock_symbol: str, 
                                   company_name: str, sector: str = "", 
                                   current_price: float = 0, market_cap: str = "",
                                   market_context: str = "") -> Dict[str, NewsAnalysisResult]:
        """Run all analysis types on a news article"""
        tasks = []
        
        # Sentiment analysis
        tasks.append(('sentiment', self.analyze_sentiment(
            news_content, stock_symbol, company_name, sector)))
        
        # News summary
        tasks.append(('summary', self.summarize_news(
            news_content, stock_symbol, company_name)))
        
        # Insights extraction (if price data available)
        if current_price > 0:
            tasks.append(('insights', self.extract_insights(
                news_content, stock_symbol, company_name, current_price, market_cap)))
        
        # Market impact (if context available)
        if market_context:
            tasks.append(('market_impact', self.analyze_market_impact(
                news_content, stock_symbol, company_name, sector, market_context)))
        
        # Execute all tasks concurrently
        results = {}
        for analysis_type, task in tasks:
            try:
                result = await task
                results[analysis_type] = result
            except Exception as e:
                results[analysis_type] = {
                    'error': str(e),
                    'analysis_type': analysis_type,
                    'timestamp': datetime.now()
                }
        
        return results
    
    async def batch_analyze(self, news_items: List[Dict[str, Any]], 
                          analysis_types: List[str] = None) -> BatchAnalysisResult:
        """Batch process multiple news items"""
        if not analysis_types:
            analysis_types = ['sentiment', 'summary']
        
        start_time = datetime.now()
        results = []
        errors = []
        total_cost = 0.0
        
        # Process items concurrently with semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
        
        async def process_item(item):
            async with semaphore:
                try:
                    if 'sentiment' in analysis_types:
                        result = await self.analyze_sentiment(
                            item['content'], item['stock_symbol'], 
                            item.get('company_name', ''), item.get('sector', ''))
                        return result
                except Exception as e:
                    return {'error': str(e), 'item': item}
        
        # Execute batch processing
        batch_results = await asyncio.gather(
            *[process_item(item) for item in news_items], 
            return_exceptions=True
        )
        
        # Process results
        for result in batch_results:
            if isinstance(result, NewsAnalysisResult):
                results.append(result)
                total_cost += result.cost
            elif isinstance(result, dict) and 'error' in result:
                errors.append(result)
            elif isinstance(result, Exception):
                errors.append({'error': str(result)})
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return BatchAnalysisResult(
            total_processed=len(news_items),
            successful=len(results),
            failed=len(errors),
            total_cost=total_cost,
            avg_processing_time=processing_time / len(news_items) if news_items else 0,
            results=results,
            errors=errors
        )