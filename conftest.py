import pytest
import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from rbr_srv_side.models import Server


@pytest.fixture
def api_client():
    """Provide an API client for testing"""
    return APIClient()


@pytest.fixture
def sample_server():
    """Create a sample server for testing"""
    return Server.objects.create(
        name='Sample Server',
        ip_address='192.168.1.1',
        description='Sample test server',
        server_is_active=True
    )


@pytest.fixture
def multiple_servers():
    """Create multiple servers for testing"""
    servers = [
        Server.objects.create(
            name=f'Test Server {i}',
            ip_address=f'192.168.1.{i}',
            description=f'Test server {i}',
            server_is_active=(i % 2 == 0)
        )
        for i in range(1, 4)
    ]
    return servers


@pytest.fixture
def server_data():
    """Provide sample server data for API requests"""
    return {
        'name': 'Test Server',
        'ip_address': '10.0.0.1',
        'description': 'A test server',
        'server_is_active': True
    }


@pytest.fixture(autouse=True)
def reset_sequences(db):
    """Reset database sequences after each test"""
    from django.core.management import call_command
    call_command('flush', '--no-input', verbosity=0)
    yield
    # Cleanup happens automatically with pytest-django
