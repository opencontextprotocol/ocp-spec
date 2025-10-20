# OCP Python Library Tests

Comprehensive test suite for the OCP Python library.

## Running Tests

```bash
# Install dependencies  
poetry install

# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=src/ocp --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_context.py -v

# Run tests for specific module
poetry run pytest tests/test_http_client.py::TestOCPHTTPClient -v

# Generate HTML coverage report
poetry run pytest --cov=src/ocp --cov-report=html
```

## Test Structure

### Test Files
- `test_agent.py` - OCPAgent class functionality
- `test_context.py` - AgentContext class and context management  
- `test_headers.py` - OCP header encoding/decoding
- `test_http_client.py` - HTTP client wrappers and enhancement
- `test_schema_discovery.py` - OpenAPI specification parsing
- `test_validation.py` - JSON schema validation functionality
- `conftest.py` - Shared test fixtures and configuration

### Test Coverage
Run `poetry run pytest --cov=src/ocp --cov-report=term-missing` to see current coverage by module.

### Test Categories
- **Unit Tests**: Individual class and function testing
- **Integration Tests**: Multi-component interaction testing
- **Mock Tests**: External API and HTTP interaction simulation
- **Edge Case Tests**: Error handling and boundary condition testing