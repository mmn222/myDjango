import pytest_django, pytest
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from rest_framework import status

from rbr_srv_side.models import Server
from rbr_srv_side.serializer import ServerSerializer, ServersReviewSerializer


# Django TestCase Tests
class ServerModelTestCase(TestCase):
    """Unit tests for Server model"""

    def setUp(self):
        """Create test data"""
        self.server_data = {
            'name': 'Test Server 1',
            'ip_address': '192.168.1.1',
            'description': 'Test server description',
            'server_is_active': True
        }
        self.server = Server.objects.create(**self.server_data)

    def test_server_creation(self):
        """Test that a server can be created with correct data"""
        self.assertEqual(self.server.name, 'Test Server 1')
        self.assertEqual(self.server.ip_address, '192.168.1.1')
        self.assertEqual(self.server.description, 'Test server description')
        self.assertTrue(self.server.server_is_active)

    def test_server_default_values(self):
        """Test default values for server"""
        server = Server.objects.create(name='Default Server')
        self.assertEqual(server.ip_address, '0.0.0.0')
        self.assertEqual(server.description, 'no_description')
        self.assertFalse(server.server_is_active)

    def test_server_string_representation(self):
        """Test server model string representation"""
        self.assertEqual(str(self.server.name), 'Test Server 1')

    def test_server_update(self):
        """Test updating server data"""
        self.server.name = 'Updated Server'
        self.server.server_is_active = False
        self.server.save()
        
        updated_server = Server.objects.get(id=self.server.id)
        self.assertEqual(updated_server.name, 'Updated Server')
        self.assertFalse(updated_server.server_is_active)

    def test_server_deletion(self):
        """Test server deletion"""
        server_id = self.server.id
        self.server.delete()
        
        with self.assertRaises(Server.DoesNotExist):
            Server.objects.get(id=server_id)

    def test_server_query_all(self):
        """Test querying all servers"""
        Server.objects.create(name='Test Server 2', ip_address='192.168.1.2')
        servers = Server.objects.all()
        self.assertEqual(servers.count(), 2)

    def test_server_filter_by_active_status(self):
        """Test filtering servers by active status"""
        Server.objects.create(name='Inactive Server', server_is_active=False)
        active_servers = Server.objects.filter(server_is_active=True)
        self.assertEqual(active_servers.count(), 1)
        self.assertEqual(active_servers.first().name, 'Test Server 1')

    def test_server_filter_by_ip_address(self):
        """Test filtering servers by IP address"""
        result = Server.objects.filter(ip_address='192.168.1.1')
        self.assertEqual(result.count(), 1)
        self.assertEqual(result.first().name, 'Test Server 1')

    def test_server_max_length_validation(self):
        """Test field max length constraints"""
        # Name max length is 255
        long_name = 'x' * 256
        server = Server(name=long_name, ip_address='192.168.1.100')
        # Django doesn't enforce max_length at DB level by default,
        # but we can check the field definition
        self.assertEqual(Server._meta.get_field('name').max_length, 255)


class ServerSerializerTestCase(TestCase):
    """Unit tests for ServerSerializer"""

    def setUp(self):
        """Create test server"""
        self.server = Server.objects.create(
            name='Serializer Test Server',
            ip_address='10.0.0.1',
            description='Testing serializer',
            server_is_active=True
        )

    def test_serializer_with_valid_data(self):
        """Test serializer with valid data"""
        data = {
            'name': 'New Server',
            'ip_address': '172.16.0.1',
            'description': 'New description',
            'server_is_active': False
        }
        serializer = ServerSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_serializer_contains_expected_fields(self):
        """Test that serializer contains all expected fields"""
        serializer = ServerSerializer(self.server)
        data = serializer.data
        self.assertEqual(set(data.keys()), {'id', 'ip_address', 'description', 'name', 'server_is_active'})

    def test_serializer_data_matches_model(self):
        """Test that serialized data matches model"""
        serializer = ServerSerializer(self.server)
        data = serializer.data
        
        self.assertEqual(data['name'], 'Serializer Test Server')
        self.assertEqual(data['ip_address'], '10.0.0.1')
        self.assertEqual(data['description'], 'Testing serializer')
        self.assertTrue(data['server_is_active'])

    def test_serializer_invalid_ip_address(self):
        """Test serializer with invalid IP address"""
        data = {
            'name': 'Invalid IP Server',
            'ip_address': 'not-an-ip',
            'description': 'Invalid IP test'
        }
        serializer = ServerSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('ip_address', serializer.errors)

    def test_server_review_serializer(self):
        """Test ServersReviewSerializer with limited fields"""
        serializer = ServersReviewSerializer(self.server)
        data = serializer.data
        
        # Should only contain ip_address and server_is_active
        self.assertEqual(set(data.keys()), {'ip_address', 'server_is_active'})
        self.assertEqual(data['ip_address'], '10.0.0.1')
        self.assertTrue(data['server_is_active'])


# API Tests using Django REST Framework test tools
class ServerAPIViewTestCase(APITestCase):
    """API tests for Server endpoints"""

    def setUp(self):
        """Create test data and API client"""
        self.client = APIClient()
        self.server1 = Server.objects.create(
            name='API Test Server 1',
            ip_address='192.168.1.10',
            description='First test server',
            server_is_active=True
        )
        self.server2 = Server.objects.create(
            name='API Test Server 2',
            ip_address='192.168.1.20',
            description='Second test server',
            server_is_active=False
        )

    def test_list_servers(self):
        """Test listing all servers"""
        response = self.client.get('/api/servers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_servers_response_structure(self):
        """Test the structure of list response"""
        response = self.client.get('/api/servers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        server_data = response.data[0]
        self.assertIn('id', server_data)
        self.assertIn('name', server_data)
        self.assertIn('ip_address', server_data)
        self.assertIn('description', server_data)
        self.assertIn('server_is_active', server_data)

    def test_create_server(self):
        """Test creating a new server"""
        data = {
            'name': 'New API Server',
            'ip_address': '192.168.1.100',
            'description': 'Created via API',
            'server_is_active': True
        }
        response = self.client.post('/api/servers/add', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New API Server')
        self.assertEqual(Server.objects.count(), 3)

    def test_create_server_with_minimal_data(self):
        """Test creating server with minimal required data"""
        data = {
            'name': 'Minimal Server'
        }
        response = self.client.post('/api/servers/add', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Minimal Server')
        self.assertEqual(response.data['ip_address'], '0.0.0.0')

    def test_create_server_missing_name(self):
        """Test creating server without required name field"""
        data = {
            'ip_address': '192.168.1.101'
        }
        response = self.client.post('/api/servers/add', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_server_invalid_ip(self):
        """Test creating server with invalid IP address"""
        data = {
            'name': 'Invalid IP Server',
            'ip_address': 'invalid-ip-address'
        }
        response = self.client.post('/api/servers/add', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_server_detail(self):
        """Test retrieving a single server"""
        response = self.client.get(f'/api/servers/{self.server1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'API Test Server 1')
        self.assertEqual(response.data['ip_address'], '192.168.1.10')

    def test_retrieve_nonexistent_server(self):
        """Test retrieving a server that doesn't exist"""
        response = self.client.get('/api/servers/9999')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_server(self):
        """Test updating a server (PUT)"""
        data = {
            'name': 'Updated Server Name',
            'ip_address': '192.168.1.10',
            'description': 'Updated description',
            'server_is_active': False
        }
        response = self.client.put(f'/api/servers/{self.server1.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Server Name')
        
        # Verify in database
        updated_server = Server.objects.get(id=self.server1.id)
        self.assertEqual(updated_server.name, 'Updated Server Name')
        self.assertFalse(updated_server.server_is_active)

    def test_partial_update_server(self):
        """Test partial update of a server (PATCH)"""
        data = {
            'name': 'Partially Updated Server'
        }
        response = self.client.patch(f'/api/servers/{self.server1.id}', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Partially Updated Server')
        
        # Verify other fields unchanged
        updated_server = Server.objects.get(id=self.server1.id)
        self.assertEqual(updated_server.ip_address, '192.168.1.10')
        self.assertTrue(updated_server.server_is_active)

    def test_delete_server(self):
        """Test deleting a server"""
        server_id = self.server1.id
        response = self.client.delete(f'/api/servers/{server_id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify deletion
        with self.assertRaises(Server.DoesNotExist):
            Server.objects.get(id=server_id)
        self.assertEqual(Server.objects.count(), 1)

    def test_get_server_status_review(self):
        """Test getting server status review endpoint"""
        response = self.client.get('/api/servers/status')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Verify limited fields in response
        for item in response.data:
            self.assertIn('ip_address', item)
            self.assertIn('server_is_active', item)
            self.assertNotIn('name', item)
            self.assertNotIn('description', item)


# Pytest style tests
class TestServerEndpointsWithPytest:
    """Pytest-style tests for server API endpoints"""
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.client = APIClient()
        self.server = Server.objects.create(
            name="Pytest Server",
            ip_address="10.20.30.40",
            description="Pytest test server",
            server_is_active=True,
        )
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test data"""
        self.client = APIClient()
        self.server = Server.objects.create(
            name='Pytest Server',
            ip_address='10.20.30.40',
            description='Pytest test server',
            server_is_active=True
        )
        yield
        # Cleanup
        Server.objects.all().delete()

    def test_list_servers_returns_ok_status(self):
        """Test that list servers endpoint returns 200 OK"""
        response = self.client.get('/api/servers/')
        assert response.status_code == status.HTTP_200_OK

    def test_list_servers_returns_list(self):
        """Test that list servers returns a list"""
        response = self.client.get('/api/servers/')
        assert isinstance(response.data, list)

    def test_list_servers_contains_created_server(self):
        """Test that created server is in list"""
        response = self.client.get('/api/servers/')
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'Pytest Server'

    def test_create_server_returns_created_status(self):
        """Test that create endpoint returns 201 Created"""
        data = {
            'name': 'New Pytest Server',
            'ip_address': '10.20.30.50',
            'server_is_active': False
        }
        response = self.client.post('/api/servers/add', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_retrieve_server_by_id(self):
        """Test retrieving specific server by ID"""
        response = self.client.get(f'/api/servers/{self.server.id}')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == self.server.id

    def test_update_server_changes_data(self):
        """Test that PUT request updates server data"""
        data = {
            'name': 'Changed Name',
            'ip_address': '10.20.30.40',
            'description': 'Changed description',
            'server_is_active': False
        }
        response = self.client.put(f'/api/servers/{self.server.id}', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Changed Name'

    def test_delete_server_removes_from_database(self):
        """Test that DELETE removes server from database"""
        server_id = self.server.id
        response = self.client.delete(f'/api/servers/{server_id}')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        with pytest.raises(Server.DoesNotExist):
            Server.objects.get(id=server_id)

    @pytest.mark.parametrize("ip_address,expected_valid", [
        ('192.168.1.1', True),
        ('10.0.0.1', True),
        ('172.16.0.1', True),
        ('invalid_ip', False),
        ('999.999.999.999', False),
    ])
    def test_ip_address_validation(self, ip_address, expected_valid):
        """Test IP address validation with multiple values"""
        data = {
            'name': 'IP Test Server',
            'ip_address': ip_address
        }
        response = self.client.post('/api/servers/add', data, format='json')
        
        if expected_valid:
            assert response.status_code == status.HTTP_201_CREATED
        else:
            assert response.status_code == status.HTTP_400_BAD_REQUEST


# Integration tests
class TestServerAPIIntegration(APITestCase):
    """Integration tests for complete server workflows"""

    def setUp(self):
        """Setup for integration tests"""
        self.client = APIClient()

    def test_complete_server_lifecycle(self):
        """Test creating, updating, and deleting a server"""
        # Create
        create_data = {
            'name': 'Lifecycle Server',
            'ip_address': '192.168.100.1',
            'description': 'Testing complete lifecycle',
            'server_is_active': True
        }
        create_response = self.client.post('/api/servers/add', create_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        server_id = create_response.data['id']
        
        # Retrieve
        retrieve_response = self.client.get(f'/api/servers/{server_id}')
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data['name'], 'Lifecycle Server')
        
        # Update
        update_data = {
            'name': 'Updated Lifecycle Server',
            'ip_address': '192.168.100.1',
            'description': 'Updated description',
            'server_is_active': False
        }
        update_response = self.client.put(f'/api/servers/{server_id}', update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        
        # Delete
        delete_response = self.client.delete(f'/api/servers/{server_id}')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify deletion
        final_response = self.client.get(f'/api/servers/{server_id}')
        self.assertEqual(final_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_multiple_servers_management(self):
        """Test managing multiple servers"""
        servers_data = [
            {'name': 'Server 1', 'ip_address': '192.168.1.1', 'server_is_active': True},
            {'name': 'Server 2', 'ip_address': '192.168.1.2', 'server_is_active': False},
            {'name': 'Server 3', 'ip_address': '192.168.1.3', 'server_is_active': True},
        ]
        
        # Create multiple servers
        created_ids = []
        for data in servers_data:
            response = self.client.post('/api/servers/add', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            created_ids.append(response.data['id'])
        
        # List and verify
        list_response = self.client.get('/api/servers/')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 3)
        
        # Clean up
        for server_id in created_ids:
            delete_response = self.client.delete(f'/api/servers/{server_id}')
            self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)