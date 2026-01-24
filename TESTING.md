# Django Server API - Testing Documentation

This project includes comprehensive API and unit tests using `pytest` and `requests`.

## Test Files

- **`tests/test_api.py`** - Main test suite with:
  - Django TestCase unit tests for the Server model
  - Serializer validation tests
  - APITestCase tests for all API endpoints
  - Pytest-style tests with parametrization
  - Integration tests for complete workflows

- **`tests/test_api_requests.py`** - Requests library integration tests:
  - Live server tests using the requests library
  - Edge case and stress testing
  - Special character handling
  - IPv4/IPv6 address testing

- **`conftest.py`** - Pytest configuration and fixtures:
  - API client fixture
  - Sample server fixtures
  - Database reset fixtures

- **`pytest.ini`** - Pytest configuration with coverage settings

## Installation

### 1. Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

Or install individual packages:

```bash
pip install pytest pytest-django pytest-cov requests
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage Report

```bash
pytest --cov=rbr_srv_side --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`

### Run Specific Test File

```bash
pytest tests/test_api.py
```

### Run Specific Test Class

```bash
pytest tests/test_api.py::ServerModelTestCase
```

### Run Specific Test Method

```bash
pytest tests/test_api.py::ServerAPIViewTestCase::test_list_servers
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests in Parallel (requires pytest-xdist)

```bash
pip install pytest-xdist
pytest -n auto
```

## Test Categories

### Model Tests (`ServerModelTestCase`)
- Server creation with default values
- Field updates and deletion
- Filtering and querying
- Field constraints validation

### Serializer Tests (`ServerSerializerTestCase`)
- Serialization/deserialization
- Field validation
- Invalid data handling
- Limited field serialization

### API Endpoint Tests (`ServerAPIViewTestCase`)
- GET `/api/servers/` - List all servers
- POST `/api/servers/add` - Create new server
- GET `/api/servers/{id}` - Retrieve single server
- PUT `/api/servers/{id}` - Full update
- PATCH `/api/servers/{id}` - Partial update
- DELETE `/api/servers/{id}` - Delete server
- GET `/api/servers/status` - Get server status

### Pytest-Style Tests (`TestServerEndpointsWithPytest`)
- Pytest fixtures and markers
- Parametrized tests for IP validation
- Modern pytest conventions

### Integration Tests (`TestServerAPIIntegration`)
- Complete CRUD lifecycle
- Multiple server management
- Request/response validation

### Requests Library Tests (`ServerAPILiveServerTests`)
- HTTP requests using requests library
- JSON payload handling
- Error response handling
- Edge cases and special characters

## Test Data Fixtures

The `conftest.py` provides the following fixtures:

- **`api_client`** - APIClient instance
- **`sample_server`** - Single test server
- **`multiple_servers`** - List of test servers
- **`server_data`** - Sample server data dict
- **`reset_sequences`** - Auto-cleanup after each test

Usage in tests:
```python
def test_example(self, api_client, sample_server):
    response = api_client.get(f'/api/servers/{sample_server.id}')
    assert response.status_code == 200
```

## API Endpoints Tested

| Method | Endpoint | Test Case |
|--------|----------|-----------|
| GET | `/api/servers/` | test_list_servers |
| POST | `/api/servers/add` | test_create_server |
| GET | `/api/servers/{id}` | test_retrieve_server_detail |
| PUT | `/api/servers/{id}` | test_update_server |
| PATCH | `/api/servers/{id}` | test_partial_update_server |
| DELETE | `/api/servers/{id}` | test_delete_server |
| GET | `/api/servers/status` | test_get_server_status_review |

## Test Coverage

Target areas:
- Server model CRUD operations
- Input validation (IP addresses, required fields)
- API response formats and status codes
- Error handling and edge cases
- Serializer field filtering
- Database state consistency

Run `pytest --cov` to see coverage percentages for each module.

## Continuous Integration

For CI/CD pipelines, use:

```bash
pytest --cov=rbr_srv_side --cov-report=xml --cov-report=term-missing --junit-xml=test-results.xml
```

This generates:
- JUnit XML report for CI systems
- Coverage XML for analysis tools
- Terminal report with missing lines

## Debugging Tests

### Run with Print Statements

```bash
pytest -s
```

### Run with PDB on Failure

```bash
pytest --pdb
```

### Run with Detailed Tracebacks

```bash
pytest --tb=long
```

## Common Test Patterns

### Test with Parametrization

```python
@pytest.mark.parametrize("ip_address,expected_valid", [
    ('192.168.1.1', True),
    ('invalid_ip', False),
])
def test_ip_validation(self, ip_address, expected_valid):
    # test code
```

### Test with Fixtures

```python
def test_with_fixture(self, api_client, sample_server):
    response = api_client.get(f'/api/servers/{sample_server.id}')
    assert response.status_code == 200
```

### Test API Requests with Requests Library

```python
response = requests.post(
    'http://localhost:8000/api/servers/add',
    json={'name': 'Test', 'ip_address': '192.168.1.1'},
    headers={'Content-Type': 'application/json'}
)
assert response.status_code == 201
```

## Troubleshooting

### Tests Not Found
Ensure test files are named `test_*.py` or `*_tests.py` and test functions start with `test_`.

### Database Errors
Tests use a separate test database. Ensure `pytest-django` is installed and `DJANGO_SETTINGS_MODULE` is set.

### Import Errors
Make sure the project root is in `PYTHONPATH` and Django is properly configured in `conftest.py`.

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-Django Documentation](https://pytest-django.readthedocs.io/)
- [Django REST Framework Testing](https://www.django-rest-framework.org/api-guide/testing/)
- [Requests Library Documentation](https://requests.readthedocs.io/)
