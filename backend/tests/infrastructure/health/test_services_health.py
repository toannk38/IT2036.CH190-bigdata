"""Services health check tests."""
import pytest
from backend.tests.infrastructure.utils.docker_helpers import get_container_status


@pytest.mark.health
def test_mongodb_running():
    """Test MongoDB container is running."""
    status = get_container_status("mongodb")
    assert status == "running"


@pytest.mark.health
def test_redis_running():
    """Test Redis container is running."""
    status = get_container_status("redis")
    assert status == "running"


@pytest.mark.health
def test_kafka_running():
    """Test Kafka container is running."""
    status = get_container_status("kafka")
    assert status == "running"


@pytest.mark.health
def test_zookeeper_running():
    """Test Zookeeper container is running."""
    status = get_container_status("zookeeper")
    assert status == "running"


@pytest.mark.health
def test_elasticsearch_running():
    """Test Elasticsearch container is running."""
    status = get_container_status("elasticsearch")
    assert status == "running"


@pytest.mark.health
def test_prometheus_running():
    """Test Prometheus container is running."""
    status = get_container_status("prometheus")
    assert status == "running"


@pytest.mark.health
def test_grafana_running():
    """Test Grafana container is running."""
    status = get_container_status("grafana")
    assert status == "running"


@pytest.mark.health
def test_all_services_healthy(mongodb_client, redis_client, elasticsearch_client):
    """Test all services are healthy."""
    # MongoDB
    assert mongodb_client.server_info() is not None
    
    # Redis
    assert redis_client.ping() is True
    
    # Elasticsearch
    assert elasticsearch_client.ping() is True
