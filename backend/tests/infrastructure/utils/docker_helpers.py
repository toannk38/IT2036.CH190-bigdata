"""Docker helper functions."""
import docker
import subprocess


def check_services_running():
    """Check if all required services are running."""
    try:
        client = docker.from_env()
        containers = client.containers.list()
        
        required_services = ['mongodb', 'redis', 'kafka', 'zookeeper', 'elasticsearch']
        running_services = [c.name for c in containers]
        
        for service in required_services:
            if not any(service in name for name in running_services):
                print(f"Service {service} is not running")
                return False
        
        return True
    except Exception as e:
        print(f"Error checking services: {e}")
        return False


def get_container_status(service_name):
    """Get status of a specific container."""
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        
        for container in containers:
            if service_name in container.name:
                return container.status
        
        return None
    except Exception as e:
        print(f"Error getting container status: {e}")
        return None


def execute_in_container(service_name, command):
    """Execute command in container."""
    try:
        result = subprocess.run(
            ['docker', 'exec', service_name] + command.split(),
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        print(f"Error executing command: {e}")
        return None
