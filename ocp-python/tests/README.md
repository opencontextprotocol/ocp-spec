# Tests for OCP Python Library

This directory contains unit tests for the OCP Python library.

## Running Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=ocp

# Run specific test file
pytest tests/test_context.py

# Run with verbose output
pytest -v
```

## Test Structure

- `test_context.py` - Tests for AgentContext class
- `test_headers.py` - Tests for OCP header encoding/decoding
- `test_http_client.py` - Tests for HTTP client enhancement
- `test_schemas.py` - Tests for validation functionality
- `test_integration.py` - Integration tests with mock APIs
- `conftest.py` - Shared test fixtures and configuration