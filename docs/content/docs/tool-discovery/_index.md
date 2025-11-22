---
title: "Tool Discovery"
next: /docs/api-registry
prev: /docs/getting-started
weight: 2
cascade:
  type: docs
---

Automatically convert any OpenAPI specification into callable tools.

```python
from ocp_agent import OCPAgent

agent = OCPAgent()

# One spec → 800+ instant tools
github = agent.register_api("github")   # fast lookup from registry
stripe = agent.register_api("stripe")   

# Each endpoint becomes callable
agent.call_tool("search_issues", {"q": "bug"})
agent.call_tool("create_payment_intent", {"amount": 2000})
```

## How It Works

- **OpenAPI Analysis**: OCP extracts endpoints, parameters, and schemas.
- **Tool Generation**: Each operation becomes a callable tool with deterministic naming.
- **Smart Caching**: Memory → Cache → Registry → Network lookup chain.
- **Built-in Validation**: All parameters validated against OpenAPI schemas automatically.

## Benefits

- **🔥 Instant Tools**: Any OpenAPI spec becomes hundreds of callable tools  
- **⚡ Registry Speed**: Huge library of popular APIs pre-indexed for fast lookup  
- **✅ Auto Validation**: Parameters validated against schemas  
- **🎯 Zero Setup**: Works with existing APIs, no infrastructure required

## Tool Naming Rules

OCP generates predictable tool names from OpenAPI specifications:

**1. Use `operationId` (when present):**
```yaml
# OpenAPI spec
paths:
  /repos/{owner}/{repo}/issues:
    get:
      operationId: "listRepositoryIssues"  # → Tool name: "listRepositoryIssues"
```

**2. Generate from HTTP method + path (when `operationId` missing):**
```yaml
# OpenAPI spec                  # Generated tool name
GET /items                      # → "get_items"
POST /items                     # → "post_items"  
GET /items/{id}                 # → "get_items_id"
DELETE /repos/{owner}/{repo}    # → "delete_repos_owner_repo"
```

## Handling Tool Conflicts

When multiple APIs have tools with the same name, use the optional `apiName` parameter:

```python
from ocp_agent import OCPAgent

agent = OCPAgent()
agent.register_api("github")
agent.register_api("jira")

# Both APIs might have "createIssue" - specify which one
github_issue = agent.call_tool("createIssue", {
    "title": "Bug in payment flow",
    "body": "Found during testing"
}, "github")

jira_issue = agent.call_tool("createIssue", {
    "fields": {
        "summary": "Payment bug",
        "issuetype": {"name": "Bug"}
    }
}, "jira")
```

## Error Handling

**Tool Not Found:**
```python
try:
    agent.call_tool("nonexistent_tool")
except ValueError as e:
    print(e)
    # Tool 'nonexistent_tool' not found. Available tools: search_issues, create_issue, get_user
```

**Parameter Validation:**
```python
try:
    # Missing required parameter
    agent.call_tool("create_issue", {})
except ValueError as e:
    print(e)
    # Parameter validation failed: title is required
```

**Malformed Spec:**
```python
try:
    agent.register_api("broken-api", "https://example.com/invalid-spec.json")
except Exception as e:
    # Graceful fallback - continues without this API
    print(f"Failed to register API: {e}")
```

## Lookup Chain

Memory → Cache → Registry → Network

**Use Registry (Recommended):**
```python
# Fast lookup for popular APIs
agent.register_api("github")
agent.register_api("stripe") 
agent.register_api("slack")
```

**Use Direct OpenAPI:**
```python
# For custom/internal APIs
agent.register_api("my-api", "https://api.company.com/openapi.json")

# Enterprise GitHub with custom base URL
agent.register_api("github", base_url="https://raw.githubusercontent.com/github/rest-api-description/refs/heads/main/descriptions/ghec/dereferenced/ghec.deref.json")
```

## Local Cache

OCP automatically caches API specifications locally for faster repeat access:

- **Cache Location:** `~/.ocp/cache/apis/`
- **Default Expiration:** 7 days

```python
from ocp_agent import OCPAgent

agent = OCPAgent()

# First registration: downloads and caches
agent.register_api("github")

# Subsequent registrations: instant cache hit
agent.register_api("github")
```

**Cache Control:**

```python
from ocp_agent import OCPStorage

storage = OCPStorage()

# List cached APIs
cached_apis = storage.list_cached_apis()
print(f"Cached: {cached_apis}")  # ['github', 'stripe', 'slack']

# Clear specific API cache
storage.clear_cache("github")    # Forces fresh download next time

# Clear entire cache
storage.clear_cache()            # Clears all cached APIs

# Force fresh download (ignore cache)
agent.register_api("github", max_age_days=0)
```

**When Cache is Used:**
- API specs cached for 7 days by default
- Cache automatically bypassed when expired
- Manual cache control for testing/debugging
- Cache survives application restarts
