"""Cache and database integration tests."""
import pytest
import json


@pytest.mark.integration
def test_cache_miss_fallback_to_db(clean_redis, clean_mongodb, sample_companies):
    """Test cache miss with database fallback."""
    # Insert data to MongoDB
    company = sample_companies[0]
    clean_mongodb.test_stocks.insert_one(company)
    
    # Check cache (should miss)
    cache_key = f"test:stock:{company['symbol']}"
    cached = clean_redis.get(cache_key)
    assert cached is None
    
    # Fetch from DB and cache
    db_result = clean_mongodb.test_stocks.find_one({"symbol": company['symbol']})
    assert db_result is not None
    
    # Cache the result
    db_result.pop('_id')  # Remove MongoDB _id
    clean_redis.setex(cache_key, 300, json.dumps(db_result))
    
    # Verify cache hit
    cached = json.loads(clean_redis.get(cache_key))
    assert cached['symbol'] == company['symbol']


@pytest.mark.integration
def test_cache_invalidation(clean_redis, clean_mongodb, sample_companies):
    """Test cache invalidation on data update."""
    company = sample_companies[0]
    cache_key = f"test:stock:{company['symbol']}"
    
    # Insert and cache
    clean_mongodb.test_stocks.insert_one(company)
    clean_redis.setex(cache_key, 300, json.dumps(company))
    
    # Update in DB
    clean_mongodb.test_stocks.update_one(
        {"symbol": company['symbol']},
        {"$set": {"organ_name": "Updated Name"}}
    )
    
    # Invalidate cache
    clean_redis.delete(cache_key)
    
    # Verify cache miss
    assert clean_redis.get(cache_key) is None


@pytest.mark.integration
def test_bulk_cache_warming(clean_redis, clean_mongodb, sample_companies):
    """Test bulk cache warming from database."""
    # Insert companies to DB
    companies = sample_companies[:10]
    clean_mongodb.test_stocks.insert_many(companies)
    
    # Warm cache
    for company in companies:
        cache_key = f"test:stock:{company['symbol']}"
        company_copy = company.copy()
        company_copy.pop('_id', None)
        clean_redis.setex(cache_key, 300, json.dumps(company_copy))
    
    # Verify all cached
    for company in companies:
        cache_key = f"test:stock:{company['symbol']}"
        cached = clean_redis.get(cache_key)
        assert cached is not None


@pytest.mark.integration
def test_cache_price_data(clean_redis, clean_mongodb, sample_prices):
    """Test caching price data."""
    prices = sample_prices[:20]
    clean_mongodb.test_prices.insert_many(prices)
    
    # Cache latest prices
    latest_price = prices[-1]
    cache_key = f"test:price:latest:{latest_price['symbol']}"
    clean_redis.setex(cache_key, 60, json.dumps(latest_price))
    
    # Verify
    cached = json.loads(clean_redis.get(cache_key))
    assert cached['symbol'] == latest_price['symbol']
