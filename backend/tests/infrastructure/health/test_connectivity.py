"""Network connectivity tests."""
import pytest
import socket


@pytest.mark.health
def test_mongodb_port():
    """Test MongoDB port is accessible."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 27017))
    sock.close()
    assert result == 0


@pytest.mark.health
def test_redis_port():
    """Test Redis port is accessible."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 6379))
    sock.close()
    assert result == 0


@pytest.mark.health
def test_kafka_port():
    """Test Kafka port is accessible."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 9092))
    sock.close()
    assert result == 0


@pytest.mark.health
def test_elasticsearch_port():
    """Test Elasticsearch port is accessible."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 9200))
    sock.close()
    assert result == 0


@pytest.mark.health
def test_prometheus_port():
    """Test Prometheus port is accessible."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 9090))
    sock.close()
    assert result == 0


@pytest.mark.health
def test_grafana_port():
    """Test Grafana port is accessible."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 3000))
    sock.close()
    assert result == 0
