# OCP Python Library

Zero-infrastructure context sharing for AI agents.

## Installation

```bash
pip install ocp-agent
```

## Quick Start

```python
from ocp import AgentContext, enhance_http_client
import requests

# Create agent context
context = AgentContext(
    agent_type="ide_copilot",
    workspace="payment-service",
    current_file="test_payment.py"
)

# Enhance any HTTP client with OCP
github = enhance_http_client(requests, context)

# API calls automatically include context
response = github.get("https://api.github.com/search/issues", 
                     params={"q": "payment test failure"})
# GitHub gets rich context about debugging session
```

## Features

- **Zero Infrastructure**: No servers to deploy or maintain
- **Standard HTTP**: Works with any HTTP client (requests, httpx, aiohttp)
- **Agent-First**: Built specifically for AI agent workflows
- **Context Memory**: Persistent context across API calls
- **OpenAPI Integration**: Enhances existing APIs with context

## Examples

See the `examples/` directory for:
- `github_agent.py` - GitHub API integration with debugging context
- `debugging_workflow.py` - Multi-step debugging scenario
- `vs_code_integration.py` - VS Code extension integration

## Development

```bash
git clone https://github.com/opencontextprotocol/specification.git
cd specification/ocp-python
pip install -e ".[dev]"
pytest
```

## License

MIT License - see LICENSE file.