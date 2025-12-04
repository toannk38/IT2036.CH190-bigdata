"""MongoDB unit tests."""
import pytest


@pytest.mark.unit
def test_mongodb_connection(mongodb_client):
    """Test MongoDB connection."""
    assert mongodb_client.server_info() is not None


@pytest.mark.unit
def test_insert_companies(clean_mongodb, sample_companies):
    """Test inserting company data."""
    companies = sample_companies[:10]
    result = clean_mongodb.test_stocks.insert_many(companies)
    assert len(result.inserted_ids) == 10


@pytest.mark.unit
def test_query_companies(clean_mongodb, sample_companies):
    """Test querying company data."""
    companies = sample_companies[:5]
    clean_mongodb.test_stocks.insert_many(companies)
    
    result = clean_mongodb.test_stocks.find_one({"symbol": companies[0]["symbol"]})
    assert result is not None
    assert result["organ_name"] == companies[0]["organ_name"]


@pytest.mark.unit
def test_insert_prices(clean_mongodb, sample_prices):
    """Test inserting price data."""
    prices = sample_prices[:100]
    result = clean_mongodb.test_prices.insert_many(prices)
    assert len(result.inserted_ids) == 100


@pytest.mark.unit
def test_query_prices_by_time(clean_mongodb, sample_prices):
    """Test querying prices by time range."""
    prices = sample_prices[:50]
    clean_mongodb.test_prices.insert_many(prices)
    
    result = list(clean_mongodb.test_prices.find({"symbol": "VCI"}).limit(10))
    assert len(result) == 10


@pytest.mark.unit
def test_insert_news(clean_mongodb, sample_news):
    """Test inserting news data."""
    news = sample_news[:5]
    result = clean_mongodb.test_news.insert_many(news)
    assert len(result.inserted_ids) == 5


@pytest.mark.unit
def test_create_index(clean_mongodb):
    """Test creating indexes."""
    clean_mongodb.test_stocks.create_index("symbol", unique=True)
    indexes = list(clean_mongodb.test_stocks.list_indexes())
    assert len(indexes) >= 2  # _id and symbol


@pytest.mark.unit
def test_aggregation(clean_mongodb, sample_prices):
    """Test aggregation query."""
    prices = sample_prices[:100]
    clean_mongodb.test_prices.insert_many(prices)
    
    pipeline = [
        {"$group": {
            "_id": "$symbol",
            "avg_volume": {"$avg": "$volume"}
        }}
    ]
    result = list(clean_mongodb.test_prices.aggregate(pipeline))
    assert len(result) > 0
