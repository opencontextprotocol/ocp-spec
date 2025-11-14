---
title: OpenAPI Tool Generation
weight: 2
---

OCP's core capability: automatically convert any OpenAPI specification into callable agent tools. No manual API integration required.

## How It Works

```python
import ocp

# Point to any OpenAPI spec
github_tools = ocp.discover_tools("https://api.github.com/openapi.json")
stripe_tools = ocp.discover_tools("stripe")  # From registry

# Tools are now callable functions
repos = github_tools.list_repositories()
invoice = stripe_tools.create_invoice(amount=1000, currency="usd")
```

## Tool Generation Process

### 1. Fetch OpenAPI Specification
```python
# From URL
spec = fetch_openapi("https://api.github.com/openapi.json")

# From registry (faster)
spec = registry.get_spec("github")

# From local file
spec = load_openapi("./my-api.json")
```

### 2. Parse Operations into Tools
Each OpenAPI operation becomes a callable tool:

```yaml
# OpenAPI operation
paths:
  /repos/{owner}/{repo}/issues:
    post:
      operationId: create_issue
      summary: Create an issue
      parameters:
        - name: owner
        - name: repo
      requestBody:
        properties:
          title:
            type: string
          body:
            type: string
```

Becomes:
```python
# Callable tool
def create_issue(owner: str, repo: str, title: str, body: str = None):
    """Create an issue"""
    # Auto-generated implementation with context injection
```

### 3. Tool Naming Convention

OCP uses deterministic naming to ensure consistency:

- **Method + Path**: `post_repos_owner_repo_issues` → `create_issue`
- **Operation ID**: Uses `operationId` if present
- **Fallback**: HTTP method + simplified path

Examples:
```
GET /users/{id} → get_user
POST /repos/{owner}/{repo}/issues → create_issue  
DELETE /repos/{owner}/{repo} → delete_repository
```

### 4. Parameter Validation

All parameters are validated against the OpenAPI schema:

```python
# Invalid call throws validation error
github_tools.create_issue()  # Error: missing required 'owner', 'repo', 'title'

# Valid call
github_tools.create_issue(
    owner="myorg", 
    repo="myrepo", 
    title="Bug report",
    body="Description of the issue"
)
```

## Context Integration

Tools automatically inject OCP context headers:

```python
# User calls
repos = github_tools.list_repositories()

# OCP automatically adds context
# GET /user/repos HTTP/1.1
# OCP-Context-ID: debug-session-123
# OCP-Agent-Goal: find_failing_tests
# OCP-Session: eyJ3b3Jrc3BhY2UiOiJwYXltZW50LXNlcnZpY2UifQ==
```

## Advanced Features

### Tool Discovery
```python
# List all available tools
tools = github_tools.list_tools()
# ['list_repositories', 'create_issue', 'get_issue', ...]

# Get tool documentation
help(github_tools.create_issue)
# create_issue(owner: str, repo: str, title: str, body: str = None)
# Create an issue in the specified repository
```

### Registry Integration
```python
# Search for APIs
results = ocp.search_apis("payment")
# [{'name': 'stripe', 'description': 'Payment processing'}, ...]

# Fast discovery from registry
stripe_tools = ocp.discover_tools("stripe")  # Pre-cached, instant
```

### Error Handling
```python
try:
    issue = github_tools.create_issue(owner="invalid", repo="repo", title="test")
except ocp.APIError as e:
    print(f"API Error: {e.status_code} - {e.message}")
except ocp.ValidationError as e:
    print(f"Parameter Error: {e.message}")
```

## Supported APIs

OCP works with any OpenAPI 3.0+ specification:

- **Public APIs**: GitHub, Stripe, Slack, Discord, etc.
- **Internal APIs**: Your company's documented APIs
- **Third-party APIs**: Any service with OpenAPI docs
- **Generated specs**: From frameworks like FastAPI, Django REST

The only requirement: a valid OpenAPI specification.