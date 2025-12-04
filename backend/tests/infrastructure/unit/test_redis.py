"""Redis unit tests."""
import pytest
import json


@pytest.mark.unit
def test_redis_connection(redis_client):
    """Test Redis connection."""
    assert redis_client.ping() is True


@pytest.mark.unit
def test_set_get_string(clean_redis):
    """Test set and get string value."""
    clean_redis.set("test:key1", "value1")
    assert clean_redis.get("test:key1") == "value1"


@pytest.mark.unit
def test_set_get_json(clean_redis, sample_companies):
    """Test set and get JSON data."""
    company = sample_companies[0]
    clean_redis.set("test:company:VCB", json.dumps(company))
    
    result = json.loads(clean_redis.get("test:company:VCB"))
    assert result["symbol"] == company["symbol"]


@pytest.mark.unit
def test_ttl(clean_redis):
    """Test TTL functionality."""
    clean_redis.setex("test:temp", 10, "temporary")
    ttl = clean_redis.ttl("test:temp")
    assert ttl > 0 and ttl <= 10


@pytest.mark.unit
def test_hash_operations(clean_redis):
    """Test hash operations."""
    clean_redis.hset("test:hash", "field1", "value1")
    clean_redis.hset("test:hash", "field2", "value2")
    
    assert clean_redis.hget("test:hash", "field1") == "value1"
    assert clean_redis.hlen("test:hash") == 2


@pytest.mark.unit
def test_list_operations(clean_redis):
    """Test list operations."""
    clean_redis.rpush("test:list", "item1", "item2", "item3")
    
    assert clean_redis.llen("test:list") == 3
    assert clean_redis.lindex("test:list", 0) == "item1"


@pytest.mark.unit
def test_cache_stock_data(clean_redis, sample_companies):
    """Test caching stock data."""
    for company in sample_companies[:5]:
        key = f"test:stock:{company['symbol']}"
        clean_redis.setex(key, 300, json.dumps(company))
    
    # Verify cached data
    cached = json.loads(clean_redis.get(f"test:stock:{sample_companies[0]['symbol']}"))
    assert cached["symbol"] == sample_companies[0]["symbol"]


@pytest.mark.unit
def test_delete_keys(clean_redis):
    """Test deleting keys."""
    clean_redis.set("test:delete1", "value1")
    clean_redis.set("test:delete2", "value2")
    
    clean_redis.delete("test:delete1")
    assert clean_redis.get("test:delete1") is None
    assert clean_redis.get("test:delete2") == "value2"
