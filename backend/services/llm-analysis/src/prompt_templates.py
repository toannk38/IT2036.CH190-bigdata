from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class PromptType(Enum):
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    NEWS_SUMMARY = "news_summary"
    INSIGHT_EXTRACTION = "insight_extraction"
    MARKET_IMPACT = "market_impact"

@dataclass
class PromptTemplate:
    name: str
    template: str
    version: str
    parameters: List[str]
    expected_output: str

class PromptManager:
    """Manages prompt templates with versioning and A/B testing"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.active_versions = {}
    
    def _load_templates(self) -> Dict[str, Dict[str, PromptTemplate]]:
        """Load all prompt templates"""
        return {
            PromptType.SENTIMENT_ANALYSIS.value: {
                "v1.0": PromptTemplate(
                    name="sentiment_analysis_v1",
                    template="""Analyze the sentiment of this Vietnamese stock market news article.

News Article:
{news_content}

Stock Symbol: {stock_symbol}
Company Name: {company_name}

Please provide:
1. Overall Sentiment: [POSITIVE/NEGATIVE/NEUTRAL]
2. Confidence Score: [0-100]
3. Key Sentiment Drivers: [List 2-3 main factors]
4. Market Impact Prediction: [HIGH/MEDIUM/LOW]

Format your response as JSON:
{{
    "sentiment": "POSITIVE/NEGATIVE/NEUTRAL",
    "confidence": 85,
    "drivers": ["factor1", "factor2", "factor3"],
    "market_impact": "HIGH/MEDIUM/LOW",
    "reasoning": "Brief explanation"
}}""",
                    version="v1.0",
                    parameters=["news_content", "stock_symbol", "company_name"],
                    expected_output="JSON with sentiment analysis"
                ),
                "v1.1": PromptTemplate(
                    name="sentiment_analysis_v1.1",
                    template="""You are a Vietnamese stock market analyst. Analyze the sentiment of this news article with focus on financial impact.

News Article:
{news_content}

Stock: {stock_symbol} - {company_name}
Sector: {sector}

Analysis Requirements:
1. Sentiment Classification: POSITIVE/NEGATIVE/NEUTRAL
2. Confidence Level: 0-100 (higher = more certain)
3. Financial Impact Areas: Revenue, Profit, Market Share, Regulation
4. Time Horizon: SHORT_TERM (1-3 months), MEDIUM_TERM (3-12 months), LONG_TERM (1+ years)

Response Format (JSON only):
{{
    "sentiment": "POSITIVE",
    "confidence": 85,
    "impact_areas": {{"revenue": "positive", "profit": "neutral", "market_share": "positive", "regulation": "neutral"}},
    "time_horizon": "MEDIUM_TERM",
    "key_factors": ["factor1", "factor2"],
    "risk_level": "LOW/MEDIUM/HIGH"
}}""",
                    version="v1.1",
                    parameters=["news_content", "stock_symbol", "company_name", "sector"],
                    expected_output="Enhanced JSON with financial impact analysis"
                )
            },
            
            PromptType.NEWS_SUMMARY.value: {
                "v1.0": PromptTemplate(
                    name="news_summary_v1",
                    template="""Summarize this Vietnamese stock market news article in a concise, investor-focused format.

News Article:
{news_content}

Stock: {stock_symbol} - {company_name}

Create a summary with:
1. Key Points (3-5 bullet points)
2. Financial Implications
3. Market Relevance Score (1-10)
4. Investor Action Suggestion

Format as JSON:
{{
    "summary": "Brief 2-3 sentence summary",
    "key_points": ["point1", "point2", "point3"],
    "financial_implications": "Impact on company finances",
    "relevance_score": 8,
    "investor_action": "HOLD/BUY/SELL/WATCH",
    "urgency": "HIGH/MEDIUM/LOW"
}}""",
                    version="v1.0",
                    parameters=["news_content", "stock_symbol", "company_name"],
                    expected_output="JSON with structured news summary"
                )
            },
            
            PromptType.INSIGHT_EXTRACTION.value: {
                "v1.0": PromptTemplate(
                    name="insight_extraction_v1",
                    template="""Extract actionable investment insights from this Vietnamese stock market news.

News Article:
{news_content}

Stock: {stock_symbol} - {company_name}
Current Price: {current_price} VND
Market Cap: {market_cap}

Extract:
1. Business Impact Insights
2. Competitive Position Changes
3. Growth Opportunities/Threats
4. Regulatory/Policy Implications
5. Valuation Impact

Response Format:
{{
    "business_impact": "How this affects core business",
    "competitive_position": "Changes in market position",
    "growth_factors": ["opportunity1", "threat1"],
    "regulatory_impact": "Policy/regulation effects",
    "valuation_impact": "Effect on stock valuation",
    "investment_thesis": "Updated investment case",
    "catalysts": ["upcoming catalyst1", "catalyst2"],
    "risks": ["risk1", "risk2"]
}}""",
                    version="v1.0",
                    parameters=["news_content", "stock_symbol", "company_name", "current_price", "market_cap"],
                    expected_output="JSON with investment insights"
                )
            },
            
            PromptType.MARKET_IMPACT.value: {
                "v1.0": PromptTemplate(
                    name="market_impact_v1",
                    template="""Assess the broader market impact of this Vietnamese stock market news.

News Article:
{news_content}

Primary Stock: {stock_symbol} - {company_name}
Sector: {sector}
Market Context: {market_context}

Analyze:
1. Sector-wide Impact
2. Related Stocks Affected
3. Market Trend Implications
4. Systemic Risk Assessment

Response Format:
{{
    "sector_impact": "How this affects the entire sector",
    "impact_magnitude": "HIGH/MEDIUM/LOW",
    "affected_stocks": ["STOCK1", "STOCK2"],
    "market_trend": "Reinforces/Contradicts current trends",
    "systemic_risk": "LOW/MEDIUM/HIGH",
    "contagion_potential": "Risk of spreading to other sectors",
    "market_sentiment_shift": "Expected change in overall sentiment",
    "trading_volume_impact": "Expected volume changes"
}}""",
                    version="v1.0",
                    parameters=["news_content", "stock_symbol", "company_name", "sector", "market_context"],
                    expected_output="JSON with market impact analysis"
                )
            }
        }
    
    def get_template(self, prompt_type: PromptType, version: str = None) -> PromptTemplate:
        """Get specific template version"""
        templates = self.templates.get(prompt_type.value, {})
        
        if version and version in templates:
            return templates[version]
        
        # Return latest version if no specific version requested
        if templates:
            latest_version = max(templates.keys())
            return templates[latest_version]
        
        raise ValueError(f"No template found for {prompt_type.value}")
    
    def format_prompt(self, prompt_type: PromptType, parameters: Dict[str, Any], version: str = None) -> str:
        """Format prompt with parameters"""
        template = self.get_template(prompt_type, version)
        
        # Validate required parameters
        missing_params = set(template.parameters) - set(parameters.keys())
        if missing_params:
            raise ValueError(f"Missing required parameters: {missing_params}")
        
        return template.template.format(**parameters)
    
    def set_active_version(self, prompt_type: PromptType, version: str):
        """Set active version for A/B testing"""
        self.active_versions[prompt_type.value] = version
    
    def get_active_version(self, prompt_type: PromptType) -> str:
        """Get active version for prompt type"""
        return self.active_versions.get(prompt_type.value, "latest")
    
    def list_templates(self) -> Dict[str, List[str]]:
        """List all available templates and versions"""
        return {
            prompt_type: list(versions.keys())
            for prompt_type, versions in self.templates.items()
        }
    
    def validate_template_output(self, prompt_type: PromptType, output: str) -> bool:
        """Validate if output matches expected format"""
        try:
            import json
            # Try to parse as JSON for structured outputs
            json.loads(output)
            return True
        except:
            # For non-JSON outputs, basic validation
            return len(output.strip()) > 0