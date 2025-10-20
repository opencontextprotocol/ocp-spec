# OCP Python Library

Context-aware HTTP client framework for AI agents.

## Installation

```bash
poetry install
```

## Quick Start

```python
from ocp import OCPAgent, wrap_api

# Create an OCP agent
agent = OCPAgent(
    agent_type="api_explorer",
    workspace="my-project",
    current_goal="Analyze API endpoints"
)

# Register an API from OpenAPI specification
api_spec = agent.register_api(
    name="github",
    spec_url="https://api.github.com/openapi.json"
)

# Create context-aware HTTP client
github_client = wrap_api(
    "https://api.github.com",
    agent.context,
    auth="token your_token_here"
)

# All requests include OCP context headers
response = github_client.get("/user")
```

## Core Components

- **OCPAgent**: Main agent class with API discovery and tool invocation
- **AgentContext**: Context management with persistent conversation tracking
- **OCPHTTPClient**: Context-aware HTTP client wrapper
- **OCPSchemaDiscovery**: OpenAPI specification parsing and tool extraction
- **Headers**: OCP context encoding/decoding for HTTP headers
- **Validation**: JSON schema validation for context objects

## API Reference

### OCPAgent

```python
agent = OCPAgent(agent_type, workspace=None, current_goal=None)
agent.register_api(name, spec_url)
agent.list_tools(api_name=None)
agent.call_tool(tool_name, **kwargs)
```

### AgentContext

```python
context = AgentContext(agent_type, user=None, workspace=None)
context.add_interaction(action, api_endpoint, result)
context.update_goal(new_goal)
context.to_dict()
```

### HTTP Client Functions

```python
from ocp import enhance_http_client, wrap_api

# Enhance existing client
enhanced = enhance_http_client(requests.Session(), context)

# Create API-specific client
api_client = wrap_api(base_url, context, auth=None)
```

## Development

```bash
# Clone repository
git clone https://github.com/opencontextprotocol/specification.git
cd specification/ocp-python

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=src/ocp --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_context.py -v
```

## Project Structure

```
src/ocp/
├── __init__.py          # Public API exports
├── agent.py             # OCPAgent class
├── context.py           # AgentContext class  
├── http_client.py       # HTTP client wrappers
├── headers.py           # Header encoding/decoding
├── schema_discovery.py  # OpenAPI parsing
└── validation.py        # JSON schema validation

tests/
├── test_agent.py        # OCPAgent tests
├── test_context.py      # AgentContext tests
├── test_http_client.py  # HTTP client tests
├── test_headers.py      # Header tests
├── test_schema_discovery.py # Schema parsing tests
├── test_validation.py   # Validation tests
└── conftest.py          # Test fixtures
```

## License

MIT License - see LICENSE file.