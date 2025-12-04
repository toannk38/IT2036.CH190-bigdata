"""Elasticsearch unit tests."""
import pytest


@pytest.mark.unit
def test_elasticsearch_connection(elasticsearch_client):
    """Test Elasticsearch connection."""
    assert elasticsearch_client.ping() is True


@pytest.mark.unit
def test_create_index(elasticsearch_client):
    """Test creating index."""
    index_name = "test_stocks"
    
    if elasticsearch_client.indices.exists(index=index_name):
        elasticsearch_client.indices.delete(index=index_name)
    
    elasticsearch_client.indices.create(index=index_name)
    assert elasticsearch_client.indices.exists(index=index_name)
    
    # Cleanup
    elasticsearch_client.indices.delete(index=index_name)


@pytest.mark.unit
def test_index_document(elasticsearch_client, sample_companies):
    """Test indexing document."""
    index_name = "test_companies"
    
    if elasticsearch_client.indices.exists(index=index_name):
        elasticsearch_client.indices.delete(index=index_name)
    
    company = sample_companies[0]
    result = elasticsearch_client.index(index=index_name, document=company)
    
    assert result['result'] == 'created'
    
    # Cleanup
    elasticsearch_client.indices.delete(index=index_name)


@pytest.mark.unit
def test_search_documents(elasticsearch_client, sample_companies):
    """Test searching documents."""
    index_name = "test_search"
    
    if elasticsearch_client.indices.exists(index=index_name):
        elasticsearch_client.indices.delete(index=index_name)
    
    # Index multiple documents
    for company in sample_companies[:5]:
        elasticsearch_client.index(index=index_name, document=company)
    
    # Refresh index
    elasticsearch_client.indices.refresh(index=index_name)
    
    # Search
    result = elasticsearch_client.search(index=index_name, query={"match_all": {}})
    assert result['hits']['total']['value'] >= 5
    
    # Cleanup
    elasticsearch_client.indices.delete(index=index_name)


@pytest.mark.unit
def test_bulk_index(elasticsearch_client, sample_prices):
    """Test bulk indexing."""
    index_name = "test_prices"
    
    if elasticsearch_client.indices.exists(index=index_name):
        elasticsearch_client.indices.delete(index=index_name)
    
    from elasticsearch.helpers import bulk
    
    actions = [
        {
            "_index": index_name,
            "_source": price
        }
        for price in sample_prices[:100]
    ]
    
    success, _ = bulk(elasticsearch_client, actions)
    assert success == 100
    
    # Cleanup
    elasticsearch_client.indices.delete(index=index_name)


@pytest.mark.unit
def test_cluster_health(elasticsearch_client):
    """Test cluster health."""
    health = elasticsearch_client.cluster.health()
    assert health['status'] in ['green', 'yellow', 'red']
