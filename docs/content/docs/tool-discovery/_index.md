---
title: "Tool Discovery"
next: /docs/api-registry
prev: /docs/getting-started
weight: 2
cascade:
  type: docs
---

OCP's schema discovery system automatically finds and converts OpenAPI specifications into callable tools with intelligent caching and lookup.

```python
from ocp_agent import OCPAgent

agent = OCPAgent()

# One spec → 800+ instant tools
github = agent.register_api("github")   # fast lookup from registry
stripe = agent.register_api("stripe")   

# Each endpoint becomes callable
agent.call_tool("searchIssues", {"q": "bug"})
agent.call_tool("createPaymentIntent", {"amount": 2000})
```

## Schema Discovery

- **Intelligent Lookup**: Memory → Local Cache → Registry → Direct OpenAPI (network)
- **OpenAPI Parsing**: Extracts endpoints, parameters, and response schemas
- **Tool Generation**: Each operation becomes a callable tool with deterministic naming
- **Automatic Caching**: Specs cached locally for 7 days with configurable expiration
- **Built-in Validation**: Parameters validated against OpenAPI schemas automatically

## Tool Naming Rules

OCP generates predictable camelCase tool names from OpenAPI specifications with automatic normalization:

**1. Use `operationId` (when present) with camelCase normalization:**
```yaml
# OpenAPI spec
paths:
  /repos/{owner}/{repo}/issues:
    get:
      operationId: "listRepositoryIssues"  # → Tool name: "listRepositoryIssues"
  /meta:
    get:
      operationId: "meta/root"             # → Tool name: "metaRoot"
  /admin/apps:
    put:
      operationId: "admin_apps_approve"    # → Tool name: "adminAppsApprove"
  /accounts:
    get:
      operationId: "FetchAccount"          # → Tool name: "fetchAccount"
```

**2. Generate from HTTP method + path (when `operationId` missing) with camelCase normalization:**
```yaml
# OpenAPI spec                  # Generated tool name
GET /items                      # → "getItems"
POST /items                     # → "postItems"  
GET /items/{id}                 # → "getItemsId"
DELETE /repos/{owner}/{repo}    # → "deleteReposOwnerRepo"
```

**Normalization Rules:**
- Special characters (`/`, `_`, `-`, `.`) are removed and surrounding words capitalized
- PascalCase is converted to camelCase (e.g., `FetchAccount` → `fetchAccount`)
- Numbers and version prefixes are preserved (e.g., `v2010/Accounts` → `v2010Accounts`)
- Multiple consecutive separators are collapsed (e.g., `api//users` → `apiUsers`)

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

## Handling Discovery Errors

**Tool Not Found:**
```python
try:
    agent.call_tool("nonexistentTool")
except ValueError as e:
    print(e)
    # Tool 'nonexistentTool' not found. Available tools: searchIssues, createIssue, getUser
```

**Parameter Validation:**
```python
try:
    # Missing required parameter
    agent.call_tool("createIssue", {})
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

## Discovery Lookup Chain

OCP uses a four-tier lookup system for maximum performance:

**1. Memory Cache (Instant)**
```python
agent = OCPAgent()
agent.register_api("github")  # Downloads and stores in memory
agent.register_api("github")  # Instant memory hit
```

**2. Local Storage Cache (Fast)**
```python
from ocp_agent import OCPAgent

agent = OCPAgent()  # Cache enabled by default

# First run: downloads and caches for 7 days
agent.register_api("github")

# Restart application, run again: instant cache hit
agent = OCPAgent()
agent.register_api("github")  # No network call needed
```

**3. Community Registry (Network, Pre-indexed)**
```python
# Fast registry lookup for popular APIs
agent.register_api("github")
agent.register_api("stripe") 
```

**4. Direct OpenAPI Discovery (Network, Parse)**
```python
# For custom/internal APIs  
agent.register_api("my-api", "https://api.company.com/openapi.json")
```

## Cache Management

OCP automatically caches discovered API specifications locally:

- **Cache Location:** `~/.ocp/cache/apis/`  
- **Default Expiration:** 7 days
- **Survives Restarts:** Cache persists across application restarts
- **Automatic Cleanup:** Expired specs automatically refetched when needed

**Cache Control:**

```python
from ocp_agent import OCPAgent, OCPStorage

# List what's cached locally
storage = OCPStorage()
cached_apis = storage.list_cached_apis()
print(f"Cached: {cached_apis}")  # ['github', 'stripe', 'slack']

# Force fresh discovery (bypass cache)
agent = OCPAgent()
agent.register_api("github", max_age_days=0)  # Ignores cache, downloads fresh

# Clear cache to force re-discovery
storage.clear_cache("github")    # Clear specific API
storage.clear_cache()            # Clear all cached APIs
```

**When Cache is Used:**
- Specs cached after first discovery
- Cache checked before registry or network calls
- Automatic expiration handling (7 days default)
- Manual cache control for testing

## Next: API Registry

The cache hits in your local storage, but what about the first discovery? For popular APIs like GitHub, Stripe, and Slack, OCP's [API Registry](/docs/api-registry) provides pre-indexed specifications for instant discovery without parsing delays. Learn how the registry accelerates discovery and explore hundreds of pre-indexed APIs.
