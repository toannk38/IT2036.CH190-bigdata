# LLM Engine Testing with OpenAI

This guide explains how to test the LLM Engine with OpenAI API integration.

## Prerequisites

1. **OpenAI API Key**: You need a valid OpenAI API key
2. **Python Environment**: Make sure all dependencies are installed
3. **Environment Variables**: Configure your `.env` file

## Configuration

### 1. Set up your `.env` file

Make sure your `.env` file contains:

```bash
# LLM Configuration
OPENAI_API_KEY=your_actual_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4, gpt-4-turbo, etc.
```

**Valid OpenAI Models:**
- `gpt-3.5-turbo` - Fast and cost-effective (recommended for testing)
- `gpt-4` - More capable but slower and more expensive
- `gpt-4-turbo` - Latest GPT-4 with better performance
- `gpt-4o` - Optimized GPT-4 model
- `gpt-4o-mini` - Smaller, faster GPT-4 variant

### 2. Install Dependencies

If you haven't already:

```bash
pip install openai
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Running Tests

### Option 1: Run the Test Script

The test script will test all LLM functionality including:
- Sentiment analysis with OpenAI
- Summary generation with OpenAI
- Full LLM Engine workflow
- Fallback mode (keyword-based analysis)

```bash
python scripts/test_llm_openai.py
```

### Option 2: Interactive Python Testing

You can also test interactively:

```python
from src.engines.llm_engine import LLMEngine, LLMClient
from src.config import config
from unittest.mock import Mock

# Test 1: Simple sentiment analysis
client = LLMClient(
    api_key=config.OPENAI_API_KEY,
    model=config.OPENAI_MODEL,
    use_openai=True
)

text = "Vinamilk công bố lợi nhuận tăng 25% trong quý 4"
result = client.analyze_sentiment(text)
print(f"Sentiment: {result['sentiment']}")
print(f"Score: {result['score']}")
print(f"Confidence: {result['confidence']}")

# Test 2: Summary generation
articles = [
    "Vinamilk tăng trưởng mạnh với lợi nhuận tăng 25%.",
    "Vietcombank mở rộng mạng lưới chi nhánh.",
    "FPT Software ký hợp đồng lớn với đối tác Nhật Bản."
]
summary = client.generate_summary(articles)
print(f"Summary: {summary}")
```

## Test Cases

The test script includes the following test cases:

### 1. Sentiment Analysis Tests
- **Positive Vietnamese News**: Tests detection of positive sentiment in Vietnamese
- **Negative Vietnamese News**: Tests detection of negative sentiment in Vietnamese
- **Neutral Vietnamese News**: Tests detection of neutral sentiment
- **Positive English News**: Tests English language support
- **Negative English News**: Tests negative sentiment in English

### 2. Summary Generation Test
- Tests summarization of multiple Vietnamese news articles

### 3. Full Engine Test
- Tests the complete LLM Engine workflow with mock MongoDB
- Includes sentiment analysis, influence scoring, and summary generation

### 4. Fallback Mode Test
- Tests keyword-based analysis when OpenAI is not available

## Expected Output

When running the test script, you should see output like:

```
================================================================================
LLM Engine OpenAI Integration Test Suite
================================================================================

📋 Environment Check:
  OPENAI_API_KEY: ✓ Set
  OPENAI_MODEL: gpt-3.5-turbo

================================================================================
Testing LLM Client Sentiment Analysis
================================================================================

✓ OpenAI API Key found (length: 51)
✓ Using model: gpt-3.5-turbo

📡 Initializing LLM Client with OpenAI API...

🧪 Running sentiment analysis tests...

Test 1: Positive Vietnamese News
Text: Vinamilk (VNM) công bố kết quả kinh doanh quý 4 tăng trưởng mạnh...
Expected: positive
Result:
  - Sentiment: positive
  - Score: 0.75
  - Confidence: 0.90
  ✓ PASS

...

================================================================================
Results: 5/5 tests passed
================================================================================
```

## Troubleshooting

### Error: "OPENAI_API_KEY not set"
- Make sure your `.env` file contains a valid `OPENAI_API_KEY`
- The key should start with `sk-`
- Don't use the placeholder value `your_openai_api_key_here`

### Error: "Invalid model name"
- Check that `OPENAI_MODEL` is set to a valid OpenAI model
- Use `gpt-3.5-turbo` for testing (fastest and cheapest)
- See the list of valid models above

### Error: "Rate limit exceeded"
- You've exceeded your OpenAI API rate limit
- Wait a few minutes and try again
- Consider using a lower rate of requests

### Error: "Insufficient quota"
- Your OpenAI account doesn't have enough credits
- Add credits to your OpenAI account
- Or use the fallback mode (keyword-based analysis)

### Fallback to Keyword-Based Analysis
If OpenAI API fails, the LLM Engine automatically falls back to keyword-based sentiment analysis. This ensures the system continues to work even without OpenAI access.

## Cost Considerations

OpenAI API usage incurs costs. Here are approximate costs for testing:

- **gpt-3.5-turbo**: ~$0.001 per test (very cheap)
- **gpt-4**: ~$0.03 per test (more expensive)
- **gpt-4-turbo**: ~$0.01 per test (moderate)

The test script runs about 8 API calls total, so:
- With `gpt-3.5-turbo`: ~$0.01 total
- With `gpt-4`: ~$0.25 total

## Integration with Full System

To use the LLM Engine with OpenAI in your application:

```python
from pymongo import MongoClient
from src.engines.llm_engine import LLMEngine
from src.config import config

# Connect to MongoDB
mongo_client = MongoClient(config.MONGODB_URI)

# Create LLM Engine with OpenAI
engine = LLMEngine(
    mongo_client,
    database_name=config.MONGODB_DATABASE,
    api_key=config.OPENAI_API_KEY,
    model=config.OPENAI_MODEL,
    use_openai=True
)

# Analyze news for a stock
result = engine.analyze_news('VNM', lookback_days=7)

if result:
    print(f"Sentiment: {result.sentiment.sentiment}")
    print(f"Score: {result.sentiment.score}")
    print(f"Summary: {result.summary}")
```

## Next Steps

After testing the LLM Engine:

1. Integrate with the News Collector to analyze real news data
2. Set up the Aggregation Service to combine AI/ML and LLM results
3. Configure the API Service to expose LLM analysis results
4. Set up Airflow DAGs to run LLM analysis on schedule

## Support

If you encounter issues:
1. Check the logs for detailed error messages
2. Verify your OpenAI API key is valid
3. Test with the fallback mode first
4. Check OpenAI API status at https://status.openai.com/
