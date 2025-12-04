"""Resource limits tests."""
import pytest
import docker


@pytest.mark.health
@pytest.mark.slow
def test_mongodb_memory_limit():
    """Test MongoDB memory limit."""
    client = docker.from_env()
    containers = client.containers.list()
    
    for container in containers:
        if 'mongodb' in container.name:
            stats = container.stats(stream=False)
            memory_usage = stats['memory_stats'].get('usage', 0)
            memory_limit = stats['memory_stats'].get('limit', 0)
            
            if memory_limit > 0:
                usage_pct = (memory_usage / memory_limit) * 100
                assert usage_pct < 90  # Should not exceed 90%


@pytest.mark.health
@pytest.mark.slow
def test_redis_memory_limit():
    """Test Redis memory limit."""
    client = docker.from_env()
    containers = client.containers.list()
    
    for container in containers:
        if 'redis' in container.name:
            stats = container.stats(stream=False)
            memory_usage = stats['memory_stats'].get('usage', 0)
            assert memory_usage > 0


@pytest.mark.health
def test_disk_space():
    """Test disk space availability."""
    import shutil
    disk = shutil.disk_usage("/")
    free_pct = (disk.free / disk.total) * 100
    assert free_pct > 10  # At least 10% free
