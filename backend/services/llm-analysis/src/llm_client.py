import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import openai
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
import redis
import json
import hashlib

@dataclass
class LLMResponse:
    content: str
    model: str
    tokens_used: int
    cost: float
    cached: bool = False

class LLMClient:
    """LLM API client with rate limiting, caching, and fallback support"""
    
    def __init__(self, config: Dict[str, Any]):
        self.openai_client = openai.AsyncOpenAI(api_key=config.get('openai_api_key'))
        self.anthropic_client = anthropic.AsyncAnthropic(api_key=config.get('anthropic_api_key'))
        self.redis_client = redis.Redis.from_url(config.get('redis_url', 'redis://localhost:6379'))
        
        # Rate limiting
        self.rate_limits = {
            'openai': {'requests_per_minute': 3000, 'tokens_per_minute': 250000},
            'anthropic': {'requests_per_minute': 1000, 'tokens_per_minute': 100000}
        }
        self.usage_tracking = {'openai': {}, 'anthropic': {}}
        
        # Cost tracking
        self.pricing = {
            'gpt-4': {'input': 0.03, 'output': 0.06},
            'gpt-3.5-turbo': {'input': 0.001, 'output': 0.002},
            'claude-3-sonnet': {'input': 0.003, 'output': 0.015}
        }
        
        self.cache_ttl = config.get('cache_ttl', 3600)  # 1 hour
    
    def _get_cache_key(self, prompt: str, model: str, params: Dict) -> str:
        """Generate cache key for prompt"""
        cache_data = f"{prompt}:{model}:{json.dumps(params, sort_keys=True)}"
        return f"llm_cache:{hashlib.md5(cache_data.encode()).hexdigest()}"
    
    def _check_cache(self, cache_key: str) -> Optional[LLMResponse]:
        """Check if response is cached"""
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                return LLMResponse(**data, cached=True)
        except Exception:
            pass
        return None
    
    def _cache_response(self, cache_key: str, response: LLMResponse):
        """Cache LLM response"""
        try:
            cache_data = {
                'content': response.content,
                'model': response.model,
                'tokens_used': response.tokens_used,
                'cost': response.cost
            }
            self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(cache_data))
        except Exception:
            pass
    
    def _check_rate_limit(self, provider: str) -> bool:
        """Check if within rate limits"""
        current_minute = int(time.time() // 60)
        usage = self.usage_tracking[provider].get(current_minute, {'requests': 0, 'tokens': 0})
        
        limits = self.rate_limits[provider]
        return (usage['requests'] < limits['requests_per_minute'] and 
                usage['tokens'] < limits['tokens_per_minute'])
    
    def _update_usage(self, provider: str, tokens: int):
        """Update usage tracking"""
        current_minute = int(time.time() // 60)
        if current_minute not in self.usage_tracking[provider]:
            self.usage_tracking[provider][current_minute] = {'requests': 0, 'tokens': 0}
        
        self.usage_tracking[provider][current_minute]['requests'] += 1
        self.usage_tracking[provider][current_minute]['tokens'] += tokens
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate API cost"""
        if model not in self.pricing:
            return 0.0
        
        pricing = self.pricing[model]
        input_cost = (input_tokens / 1000) * pricing['input']
        output_cost = (output_tokens / 1000) * pricing['output']
        return input_cost + output_cost
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _call_openai(self, prompt: str, model: str = "gpt-3.5-turbo", **kwargs) -> LLMResponse:
        """Call OpenAI API with retry logic"""
        if not self._check_rate_limit('openai'):
            await asyncio.sleep(60)  # Wait for rate limit reset
        
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        
        tokens_used = response.usage.total_tokens
        cost = self._calculate_cost(model, response.usage.prompt_tokens, response.usage.completion_tokens)
        
        self._update_usage('openai', tokens_used)
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=model,
            tokens_used=tokens_used,
            cost=cost
        )
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _call_anthropic(self, prompt: str, model: str = "claude-3-sonnet-20240229", **kwargs) -> LLMResponse:
        """Call Anthropic API with retry logic"""
        if not self._check_rate_limit('anthropic'):
            await asyncio.sleep(60)
        
        response = await self.anthropic_client.messages.create(
            model=model,
            max_tokens=kwargs.get('max_tokens', 1000),
            messages=[{"role": "user", "content": prompt}]
        )
        
        tokens_used = response.usage.input_tokens + response.usage.output_tokens
        cost = self._calculate_cost('claude-3-sonnet', response.usage.input_tokens, response.usage.output_tokens)
        
        self._update_usage('anthropic', tokens_used)
        
        return LLMResponse(
            content=response.content[0].text,
            model=model,
            tokens_used=tokens_used,
            cost=cost
        )
    
    async def analyze_text(self, prompt: str, provider: str = "openai", model: str = None, **kwargs) -> LLMResponse:
        """Analyze text with specified LLM provider"""
        # Set default models
        if not model:
            model = "gpt-3.5-turbo" if provider == "openai" else "claude-3-sonnet-20240229"
        
        # Check cache first
        cache_key = self._get_cache_key(prompt, model, kwargs)
        cached_response = self._check_cache(cache_key)
        if cached_response:
            return cached_response
        
        try:
            if provider == "openai":
                response = await self._call_openai(prompt, model, **kwargs)
            elif provider == "anthropic":
                response = await self._call_anthropic(prompt, model, **kwargs)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Cache successful response
            self._cache_response(cache_key, response)
            return response
            
        except Exception as e:
            # Fallback to alternative provider
            if provider == "openai":
                return await self._call_anthropic(prompt, "claude-3-sonnet-20240229", **kwargs)
            else:
                return await self._call_openai(prompt, "gpt-3.5-turbo", **kwargs)
    
    async def batch_analyze(self, prompts: List[str], provider: str = "openai", **kwargs) -> List[LLMResponse]:
        """Batch analyze multiple prompts"""
        tasks = [self.analyze_text(prompt, provider, **kwargs) for prompt in prompts]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        current_minute = int(time.time() // 60)
        stats = {}
        
        for provider in ['openai', 'anthropic']:
            usage = self.usage_tracking[provider].get(current_minute, {'requests': 0, 'tokens': 0})
            limits = self.rate_limits[provider]
            
            stats[provider] = {
                'current_requests': usage['requests'],
                'max_requests': limits['requests_per_minute'],
                'current_tokens': usage['tokens'],
                'max_tokens': limits['tokens_per_minute'],
                'requests_remaining': limits['requests_per_minute'] - usage['requests'],
                'tokens_remaining': limits['tokens_per_minute'] - usage['tokens']
            }
        
        return stats