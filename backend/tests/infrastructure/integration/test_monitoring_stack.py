"""Monitoring stack integration tests."""
import pytest
import requests


@pytest.mark.integration
def test_prometheus_connection():
    """Test Prometheus connection."""
    response = requests.get("http://localhost:9090/-/healthy")
    assert response.status_code == 200


@pytest.mark.integration
def test_prometheus_targets():
    """Test Prometheus targets."""
    response = requests.get("http://localhost:9090/api/v1/targets")
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'


@pytest.mark.integration
def test_grafana_connection():
    """Test Grafana connection."""
    response = requests.get("http://localhost:3000/api/health")
    assert response.status_code == 200


@pytest.mark.integration
def test_grafana_datasources():
    """Test Grafana datasources."""
    auth = ('admin', 'StockAI@Grafana2024')
    response = requests.get("http://localhost:3000/api/datasources", auth=auth)
    assert response.status_code == 200
