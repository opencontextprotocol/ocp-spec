# OCP Python Library

Context-aware HTTP client framework for AI agents.

## Installation

```bash
pip install open-context-agent
# or with poetry
poetry add open-context-agent
```

## Quick Start

```python
from ocp_agent import OCPAgent, wrap_api

# Create an OCP agent
agent = OCPAgent(
    agent_type="api_explorer",
    user=None,
    workspace="my-project",
    agent_goal="Analyze API endpoints"
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
    headers={"Authorization": "token your_token_here"}
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
agent = OCPAgent(agent_type, user=None, workspace=None, agent_goal=None, registry_url=None, enable_cache=True)
agent.register_api(name, spec_url=None, base_url=None)
agent.list_tools(api_name=None)
agent.call_tool(tool_name, parameters=None, api_name=None)
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
from ocp_agent import wrap_api, OCPHTTPClient

# Create API-specific client
api_client = wrap_api(base_url, context, headers=None)

# Create OCP-aware HTTP client directly
client = OCPHTTPClient(context)
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
src/ocp_agent/
├── __init__.py          # Public API exports
├── agent.py             # OCPAgent class
├── context.py           # AgentContext class  
├── http_client.py       # HTTP client wrappers
├── headers.py           # Header encoding/decoding
├── schema_discovery.py  # OpenAPI parsing
├── registry.py          # Registry client
├── storage.py           # Local storage and caching
├── validation.py        # JSON schema validation
└── errors.py            # Error classes

tests/
├── test_agent.py        # OCPAgent tests
├── test_context.py      # AgentContext tests
├── test_http_client.py  # HTTP client tests
├── test_headers.py      # Header tests
├── test_schema_discovery.py # Schema parsing tests
├── test_registry.py     # Registry tests
├── test_storage.py      # Storage tests
├── test_validation.py   # Validation tests
└── conftest.py          # Test fixtures
```

## License

MIT License - see LICENSE file.