import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def sample_server(db):
    from rbr_srv_side.models import Server
    return Server.objects.create(
        name="Sample Server",
        ip_address="192.168.1.1",
        description="Sample test server",
        server_is_active=True,
    )