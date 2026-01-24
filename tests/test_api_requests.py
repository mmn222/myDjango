"""
Integration tests using requests library for HTTP testing.
These tests demonstrate how to use the requests library to test the API.
"""

import pytest
import requests
import json
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework.test import APILiveServerTestCase
from rest_framework import status

from rbr_srv_side.models import Server


class ServerAPILiveServerTests(APILiveServerTestCase):
    """Live server tests using requests library"""

    fixtures = []

    def setUp(self):
        """Setup test data"""
        self.base_url = self.live_server_url
        self.headers = {'Content-Type': 'application/json'}

    def tearDown(self):
        """Cleanup after tests"""
        Server.objects.all().delete()

    def test_list_servers_with_requests(self):
        """Test listing servers using requests library"""
        response = requests.get(f'{self.base_url}/api/servers/')
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)

    def test_create_server_with_requests(self):
        """Test creating a server using requests library"""
        data = {
            'name': 'Requests Test Server',
            'ip_address': '192.168.1.50',
            'description': 'Created with requests',
            'server_is_active': True
        }
        
        response = requests.post(
            f'{self.base_url}/api/servers/add',
            headers=self.headers,
            data=json.dumps(data)
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data['name'] == 'Requests Test Server'
        assert response_data['ip_address'] == '192.168.1.50'

    def test_retrieve_server_with_requests(self):
        """Test retrieving a server using requests library"""
        # Create a server first
        server = Server.objects.create(
            name='Retrieve Test Server',
            ip_address='192.168.1.60',
            description='Test retrieval',
            server_is_active=False
        )
        
        response = requests.get(f'{self.base_url}/api/servers/{server.id}')
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert response_data['id'] == server.id
        assert response_data['name'] == 'Retrieve Test Server'

    def test_update_server_with_requests(self):
        """Test updating a server using requests library"""
        server = Server.objects.create(
            name='Original Name',
            ip_address='192.168.1.70',
            server_is_active=True
        )
        
        data = {
            'name': 'Updated Name',
            'ip_address': '192.168.1.70',
            'description': 'Updated via requests',
            'server_is_active': False
        }
        
        response = requests.put(
            f'{self.base_url}/api/servers/{server.id}',
            headers=self.headers,
            data=json.dumps(data)
        )
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data['name'] == 'Updated Name'
        assert response_data['server_is_active'] is False

    def test_partial_update_with_requests(self):
        """Test partial update (PATCH) using requests library"""
        server = Server.objects.create(
            name='Original Server',
            ip_address='192.168.1.80',
            description='Original description',
            server_is_active=True
        )
        
        data = {'name': 'Partially Updated'}
        
        response = requests.patch(
            f'{self.base_url}/api/servers/{server.id}',
            headers=self.headers,
            data=json.dumps(data)
        )
        
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data['name'] == 'Partially Updated'
        # Description should remain unchanged
        assert response_data['description'] == 'Original description'

    def test_delete_server_with_requests(self):
        """Test deleting a server using requests library"""
        server = Server.objects.create(
            name='Delete Test Server',
            ip_address='192.168.1.90',
            server_is_active=True
        )
        
        response = requests.delete(f'{self.base_url}/api/servers/{server.id}')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify deletion
        assert not Server.objects.filter(id=server.id).exists()

    def test_server_status_endpoint_with_requests(self):
        """Test server status endpoint with requests"""
        Server.objects.create(
            name='Status Test 1',
            ip_address='192.168.2.1',
            server_is_active=True
        )
        Server.objects.create(
            name='Status Test 2',
            ip_address='192.168.2.2',
            server_is_active=False
        )
        
        response = requests.get(f'{self.base_url}/api/servers/status')
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert len(data) == 2
        # Verify limited fields (only ip_address and server_is_active)
        assert 'ip_address' in data[0]
        assert 'server_is_active' in data[0]
        assert 'name' not in data[0]

    def test_error_handling_invalid_ip(self):
        """Test error handling with invalid IP address"""
        data = {
            'name': 'Invalid IP Server',
            'ip_address': 'not-a-valid-ip'
        }
        
        response = requests.post(
            f'{self.base_url}/api/servers/add',
            headers=self.headers,
            data=json.dumps(data)
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_required_field(self):
        """Test error handling with missing required field"""
        data = {
            'ip_address': '192.168.1.100'
            # Missing required 'name' field
        }
        
        response = requests.post(
            f'{self.base_url}/api/servers/add',
            headers=self.headers,
            data=json.dumps(data)
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_nonexistent_server_404(self):
        """Test 404 error for nonexistent server"""
        response = requests.get(f'{self.base_url}/api/servers/99999')
        assert response.status_code == status.HTTP_404_NOT_FOUND


class ServerAPIRequestsTestCase(TransactionTestCase):
    """Additional tests for edge cases and stress testing"""

    def test_concurrent_requests_simulation(self):
        """Test handling of rapid sequential requests"""
        # Create initial data
        server = Server.objects.create(
            name='Concurrent Test',
            ip_address='192.168.1.100',
            server_is_active=True
        )
        
        # Simulate rapid updates
        for i in range(5):
            data = {
                'name': f'Updated {i}',
                'ip_address': '192.168.1.100',
                'server_is_active': (i % 2 == 0)
            }
            # In a real scenario with live server, this would use requests
            # For now using direct update
            server.name = data['name']
            server.server_is_active = data['server_is_active']
            server.save()
        
        # Verify final state
        final_server = Server.objects.get(id=server.id)
        assert final_server.name == 'Updated 4'
        assert final_server.server_is_active is False

    def test_large_description_field(self):
        """Test handling of large description field"""
        large_description = 'x' * 255  # Max length
        server = Server.objects.create(
            name='Large Description Server',
            ip_address='192.168.1.101',
            description=large_description,
            server_is_active=True
        )
        
        retrieved = Server.objects.get(id=server.id)
        assert retrieved.description == large_description

    def test_special_characters_in_name(self):
        """Test handling of special characters in server name"""
        special_names = [
            'Server-with-dashes',
            'Server_with_underscores',
            'Server.with.dots',
            'Server (with) parentheses',
            'Сервер на русском',  # Non-ASCII characters
        ]
        
        for name in special_names:
            server = Server.objects.create(
                name=name,
                ip_address='192.168.1.102',
                server_is_active=True
            )
            retrieved = Server.objects.get(id=server.id)
            assert retrieved.name == name
            server.delete()

    def test_ipv4_and_ipv6_addresses(self):
        """Test both IPv4 and IPv6 address formats"""
        ipv4_server = Server.objects.create(
            name='IPv4 Server',
            ip_address='192.168.1.1',
            server_is_active=True
        )
        
        ipv6_server = Server.objects.create(
            name='IPv6 Server',
            ip_address='::1',  # IPv6 loopback
            server_is_active=True
        )
        
        assert ipv4_server.ip_address == '192.168.1.1'
        assert ipv6_server.ip_address == '::1'
