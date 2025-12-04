"""Logging stack integration tests."""
import pytest
import requests


@pytest.mark.integration
def test_elasticsearch_cluster():
    """Test Elasticsearch cluster health."""
    response = requests.get("http://localhost:9200/_cluster/health")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] in ['green', 'yellow']


@pytest.mark.integration
def test_kibana_connection():
    """Test Kibana connection."""
    response = requests.get("http://localhost:5601/api/status")
    assert response.status_code == 200


@pytest.mark.integration
def test_elasticsearch_indices():
    """Test Elasticsearch indices."""
    response = requests.get("http://localhost:9200/_cat/indices?format=json")
    assert response.status_code == 200
