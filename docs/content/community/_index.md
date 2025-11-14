---
title: Community
weight: 3
cascade:
  type: docs
---

Join the OCP developer community and contribute to the future of AI agent integration.

## API Registry

The OCP community registry provides fast API discovery with pre-cached OpenAPI specifications.

### Registry Benefits

**Instant Discovery**: Pre-indexed APIs with cached specifications for immediate tool generation.

**Quality Curation**: Community-verified APIs with reliable OpenAPI documentation.

**Search & Suggestions**: Find APIs by category, functionality, or similar services.

### Using the Registry

```python
import ocp

# Search for APIs
results = ocp.search_apis("payment")
# [{'name': 'stripe', 'description': 'Payment processing'}, 
#  {'name': 'paypal', 'description': 'Digital payments'}]

# Fast tool discovery (pre-cached)
stripe_tools = ocp.discover_tools("stripe")  # Instant, no network call
github_tools = ocp.discover_tools("github")  # Pre-cached OpenAPI spec
```

### Registry Configuration

```python
# Use community registry (default)
ocp.set_registry("https://registry.ocp.dev")

# Use private registry
ocp.set_registry("https://internal-registry.company.com")

# Disable registry (direct OpenAPI only)
ocp.disable_registry()
```

## Contributing

### Add Your API

Submit your OpenAPI-documented API to the community registry:

1. **Verify OpenAPI**: Ensure your API has complete OpenAPI 3.0+ documentation
2. **Test Tools**: Verify OCP can generate functional tools from your spec
3. **Submit PR**: Add your API to the registry via GitHub

### Contribute Code

- **Client Libraries**: Help build OCP implementations in new languages
- **Registry Service**: Improve search, caching, and indexing
- **Documentation**: Add examples and guides

### Community Channels

- **GitHub**: [opencontextprotocol/specification](https://github.com/opencontextprotocol/specification)
- **Issues**: Report bugs and request features
- **Discussions**: Ask questions and share use cases

## Ecosystem

### VS Code Extension
Official VS Code extension for OCP-aware AI agents with automatic API discovery.

### CLI Tool
Command-line interface for API discovery, testing, and context management.

### Framework Integrations
Libraries for FastAPI, Express.js, Django, and other frameworks to support OCP-enhanced APIs.