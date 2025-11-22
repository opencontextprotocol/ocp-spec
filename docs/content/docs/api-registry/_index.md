---
title: "API Registry"
next: /docs/ide-integration
prev: /docs/tool-discovery
weight: 3
cascade:
  type: docs
---

Community registry providing instant access to pre-parsed API tools with intelligent discovery and error handling.

```python
from ocp_agent import OCPRegistry

registry = OCPRegistry()

# Search for APIs by keyword
payment_apis = registry.search_apis("payment")
print(payment_apis)  # ["stripe", "paypal", "square"]

dev_tools = registry.search_apis("git")
print(dev_tools)     # ["github", "gitlab", "bitbucket"]

# List all available APIs
all_apis = registry.list_apis()
print(f"Total APIs: {len(all_apis)}")

# Get specific API specification
api_spec = registry.get_api_spec("github")
print(f"GitHub API: {api_spec.title}")
print(f"Tools: {len(api_spec.tools)}")
```

## Registry Configuration

Configure which registry to use for API discovery:

```python
from ocp_agent import OCPRegistry

# Default: uses https://registry.ocp.dev
registry = OCPRegistry()

# Environment variable override
# export OCP_REGISTRY_URL=https://internal-registry.company.com
registry = OCPRegistry()

# Explicit URL
registry = OCPRegistry("https://custom-registry.com")
```

## Error Handling & Suggestions

The registry provides intelligent suggestions when APIs aren't found:

```python
from ocp_agent import OCPAgent, APINotFound

agent = OCPAgent()

try:
    # Typo in API name
    agent.register_api("githb")  # Missing 'u'
except APINotFound as e:
    print(f"API '{e.api_name}' not found")
    print(f"Suggestions: {e.suggestions}")  # ["github", "gitlab"]
    
    # Use suggestion
    github = agent.register_api(e.suggestions[0])
```

**Registry Unavailable Handling:**
```python
from ocp_agent import RegistryUnavailable

try:
    agent.register_api("github")
except RegistryUnavailable:
    # Automatic fallback to direct OpenAPI
    agent.register_api("github", "https://api.github.com/rest/openapi.json")
```

## Custom Deployments  

Use registry tools with custom API deployments:

```python
# GitHub with custom base URL
github_custom = agent.register_api(
    "github", 
    base_url="https://github.enterprise.com/api/v3"
)

# Stripe private deployment
stripe_private = agent.register_api(
    "stripe",
    base_url="https://payments.company.com/api"
)

# Direct registry client usage
registry = OCPRegistry()
api_spec = registry.get_api_spec("github", "https://custom.github.com/api/v3")
# → Same 800+ tools, but calls go to custom instance
```

## Integration with Tool Discovery

The registry accelerates the lookup chain from [Tool Discovery](/docs/tool-discovery):

1. **Memory Cache** → Already registered APIs
2. **Local Storage** → Cached from previous sessions
3. **Registry Lookup** → Pre-parsed tools
4. **Direct OpenAPI** → Parse on demand

## Next: IDE Integration

With APIs instantly discoverable through the registry, the next step is bringing those tools into your development workflow. [IDE Integration](/docs/ide-integration) shows how to use discovered API tools directly in your editor with autocomplete, documentation, and intelligent assistance.
