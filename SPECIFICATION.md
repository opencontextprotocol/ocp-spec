# Open Context Protocol (OCP)
## Zero-Infrastructure Context for AI Agents

**TL;DR**: OCP enables AI agents to share context across API calls using standard HTTP headers. No servers, no custom protocols, just smarter APIs.

---

## The AI Agent Context Problem

**Current State with MCP**:
- ❌ Deploy custom MCP servers for each integration
- ❌ Learn new protocol schemas and JSON-RPC
- ❌ Maintain server infrastructure for simple context passing
- ❌ Stateless MCP servers lose conversation memory
- ❌ Complex setup kills adoption in IDEs

**OCP's Agent-First Solution**:
- ✅ Context flows in HTTP headers to existing APIs
- ✅ APIs become intelligent conversation participants
- ✅ Zero servers - direct API calls from agents
- ✅ Persistent context across multi-step workflows
- ✅ IDE integration is trivial

---

## Core Principle: Agents + Context + Existing APIs

OCP transforms existing APIs into intelligent conversation participants for AI agents.

### The Agent Context Flow:
```mermaid
graph LR
    A[AI Agent] -->|HTTP + Context Headers| B[GitHub API]
    B -->|Enhanced Response| A
    A -->|Accumulated Context| C[Jira API] 
    C -->|Smart Response| A
    A -->|Full Context| D[Slack API]
    
    subgraph "Zero Additional Infrastructure"
        B
        C  
        D
    end
```

**Key Insight**: Context accumulates across API calls, making each subsequent call smarter.

---

## Agent-First Architecture

### 1. **Agent Context Object**
```json
{
  "context_id": "agent-session-123",
  "agent_type": "ide_coding_assistant",
  "agent_goal": "debug_deployment_failure",
  "user": "alice",
  "workspace": {
    "name": "payment-service",
    "language": "python",
    "current_file": "deployment.py"
  },
  "conversation": {
    "history": [
      {"role": "user", "content": "My deployment is failing"},
      {"role": "assistant", "content": "Let me check your GitHub workflows"}
    ]
  },
  "accumulated_context": {
    "github_repos": ["payment-service"],
    "recent_deployments": [{"status": "failed", "error": "permission_denied"}],
    "investigation_focus": "github_actions_permissions"
  }
}
```

### 2. **Context-Aware API Calls**
```http
GET /repos/alice/payment-service/actions/runs HTTP/1.1
Host: api.github.com
Authorization: token ghp_xxxxxxxxxxxx
OCP-Context-ID: agent-session-123
OCP-Agent-Type: ide_coding_assistant
OCP-Agent-Goal: debug_deployment_failure
OCP-Session: eyJhZ2VudF9nb2FsIjoiZGVidWdfZGVwbG95bWVudF9mYWlsdXJlIn0=
```

### 3. **Enhanced API Responses**
```json
{
  "workflow_runs": [
    {
      "id": 123456,
      "status": "failure",
      "conclusion": "failure",
      "permissions_analysis": {     // ← Added because context shows permission debugging
        "missing": ["secrets:write", "contents:write"],
        "suggested_fix": "Add permissions to workflow file"
      },
      "similar_failures": [         // ← Related failures based on context
        {"repo": "other-service", "fix": "Updated GITHUB_TOKEN permissions"}
      ]
    }
  ]
}
```

---

## Primary Use Case: IDE Coding Agents

### **VS Code Copilot Chat** Enhanced with OCP

#### Current MCP Setup (Complex):
```json
{
  "mcp.servers": {
    "github": {"command": "node", "args": ["/path/to/github-mcp-server"]},
    "filesystem": {"command": "node", "args": ["/path/to/fs-mcp-server"]}
  }
}
```
**Result**: 2 server processes, custom protocols, stateless interactions

#### OCP Setup (Simple):
```json
{
  "ocp.enabled": true,
  "github.token": "ghp_xxx"
}
```
**Result**: Zero servers, direct API calls, persistent context

### **Agent Conversation Example**

**User**: "This test is failing, help me debug it"

#### MCP Flow:
```
User → Copilot → MCP Server → GitHub API → Response Chain
              ↑ (stateless server, no memory of previous conversation)
```

#### OCP Flow:
```javascript
// Agent builds rich context from IDE state + conversation
const context = {
  agent_goal: "debug_test_failure",
  current_file: "test_payment.py", 
  test_name: "test_process_refund",
  error_message: "AssertionError: Expected 200, got 500",
  recent_git_activity: ["Modified payment_processor.py"],
  conversation_context: "user_asked_about_failing_test"
};

// Direct GitHub API call with context
const response = await fetch('https://api.github.com/search/issues', {
  headers: {
    'Authorization': 'token ghp_xxx',
    'OCP-Context-ID': 'debug-session-456',
    'OCP-Agent-Goal': 'debug_test_failure',
    'OCP-Session': base64(JSON.stringify(context))
  },
  params: {q: 'repo:myproject payment test failure'}
});
```

**GitHub API Response (OCP-Enhanced)**:
```json
{
  "items": [
    {
      "number": 89,
      "title": "Payment test intermittently fails with 500 error",
      "test_context_match": true,        // ← Knows this is about test debugging
      "related_files": ["payment_processor.py", "test_payment.py"],
      "similar_error_patterns": ["AssertionError", "500 status"],
      "suggested_investigation": [       // ← Smart suggestions based on context
        "Check payment_processor.py recent changes",
        "Verify test database setup",
        "Review payment service logs"
      ]
    }
  ]
}
```

**Agent Response**: "I found a similar issue (#89) with the same error pattern. Based on your recent changes to payment_processor.py, try checking the database connection in your test setup."

---

## OpenAPI Integration (Optional Enhancement)

### **Phase 1: Works with Existing OpenAPI Specs**
OCP works immediately with any REST API that has an OpenAPI specification:

```javascript
// Agent discovers tools from existing OpenAPI spec
const githubSpec = await fetch('https://api.github.com/rest/openapi.json');
const tools = parseOpenAPIToTools(githubSpec);

// Agent can now call any GitHub API operation with context
await callTool('createIssue', {
  title: "Bug report",
  body: "Found in payment flow"
}, context);
```

### **Phase 2: OCP-Enhanced OpenAPI Specs**
APIs can optionally add OCP extensions to their OpenAPI specs to provide smarter responses:

```yaml
# Enhanced GitHub OpenAPI spec (future)
openapi: 3.0.0
info:
  title: GitHub API
  version: 3.0.0
  x-ocp-enabled: true              # This API can read OCP context

paths:
  /repos/{owner}/{repo}/issues:
    post:
      summary: Create an issue
      x-ocp-context:                # OCP behavior for this operation
        enhances_with:
          - agent_goal              # Use agent goal to customize response
          - workspace_context       # Use workspace info for smarter defaults
          - conversation_history    # Use chat history for better issue descriptions
      responses:
        201:
          description: Issue created
          x-ocp-enhanced-response:  # What gets added when OCP context is present
            properties:
              suggested_labels:     # Auto-suggest labels based on context
                type: array
              related_issues:       # Find related issues based on context
                type: array
              next_actions:         # Suggest follow-up actions
                type: array
```

### **Discovery Mechanism**
Agents discover OCP capabilities through standard OpenAPI specs:

```javascript
// Check if API supports OCP
const spec = await fetch('https://api.github.com/rest/openapi.json');
const ocpEnabled = spec.info['x-ocp-enabled'];

if (ocpEnabled) {
  // Use OCP context headers for enhanced responses
  headers['OCP-Context-ID'] = context.id;
  headers['OCP-Session'] = encodeContext(context);
} else {
  // Standard API calls (still works!)
  // Context managed client-side only
}
```

### **Key Points**:
1. **No special discovery endpoint needed** - Uses existing OpenAPI specs
2. **Backward compatible** - OCP-unaware clients work normally  
3. **Standards-based** - Just extensions to existing OpenAPI format
4. **Optional** - APIs can add OCP extensions gradually

---

## OCP Extensions to OpenAPI

Add these optional extensions to your OpenAPI specs:

```yaml
info:
  x-ocp-enabled: true           # This API supports OCP
  x-ocp-context-aware: true     # This API can use context

paths:
  /weather:
    get:
      x-ocp-context:
        requires: ["location"]   # Needs location from context
        provides: ["weather"]    # Adds weather to context
        preserves: ["user_prefs"] # Passes through user preferences
```

---

## Implementation Examples

### 1. Convert Any OpenAPI Service
```python
from ocp import wrap_openapi

# Automatically wrap any OpenAPI service
weather_service = wrap_openapi("https://weather-api.com/openapi.json")

# Use with OCP context
result = weather_service.get_weather(
    location="NYC",
    context=ocp_context
)
```

### 2. Add OCP to Existing API
```python
from flask import Flask, request
from ocp import parse_context, add_context_headers

app = Flask(__name__)

@app.route('/weather')
def get_weather():
    # Parse OCP context from headers
    context = parse_context(request.headers)
    
    # Your existing logic
    weather = fetch_weather(request.args.get('location'))
    
    # Add context to response
    response = make_response(weather)
    add_context_headers(response, context)
    return response
```

### 3. AI Agent with OCP
```python
class WeatherAgent:
    def __init__(self):
        self.context = OCPContext()
        
    def get_weather(self, location):
        # Standard HTTP call with OCP headers
        response = requests.get(
            'https://weather-api.com/weather',
            params={'location': location},
            headers=self.context.to_headers()
        )
        
        # Update context from response
        self.context.update_from_headers(response.headers)
        return response.json()
```

---

## Migration from MCP

| MCP Concept | OCP Equivalent |
|-------------|----------------|
| MCP Server | HTTP API with OpenAPI spec |
| Tool Definition | OpenAPI operation |
| Resource | HTTP endpoint |
| Prompt | OpenAPI example |
| Transport | HTTP with OCP headers |

### MCP to OCP Converter
```bash
# Convert MCP server to OCP-compatible API
ocp convert mcp-server.json --output openapi.json

# Generate OCP client from OpenAPI
ocp generate client --spec openapi.json --lang python
```

---

## Benefits Over MCP

### For Developers
- **No new concepts** - Use HTTP, OpenAPI, OAuth2 you already know
- **Instant tooling** - Postman, curl, Swagger UI work immediately
- **No servers** - Add OCP headers to existing APIs
- **Standard auth** - OAuth2, JWT, API keys work as-is

### For Enterprises
- **Zero infrastructure** - No new servers to deploy/maintain
- **Security compliance** - Use existing API security policies
- **Monitoring/logging** - Standard HTTP traffic, existing tools work
- **Cost effective** - No additional hosting costs

### For AI Applications
- **Immediate ecosystem** - Every REST API becomes a potential tool
- **Better performance** - Direct HTTP calls, no proxy servers
- **Simplified deployment** - No server dependencies
- **Standards-based** - Future-proof, interoperable

---

## Getting Started

### 1. Add OCP Headers to Existing API
```javascript
// Express.js example
app.use((req, res, next) => {
  // Parse OCP context if present
  if (req.headers['ocp-context-id']) {
    req.ocp_context = parseOCPHeaders(req.headers);
  }
  next();
});

app.get('/weather', (req, res) => {
  const weather = getWeather(req.query.location);
  
  // Add OCP headers to response
  if (req.ocp_context) {
    res.set('OCP-Context-ID', req.ocp_context.id);
    res.set('OCP-Session', encodeContext(req.ocp_context));
  }
  
  res.json(weather);
});
```

### 2. Use Existing APIs with OCP
```python
import ocp

# Create context
context = ocp.Context(user="alice", session_id="123")

# Call any HTTP API with context
response = ocp.call(
    method="GET",
    url="https://api.github.com/user",
    context=context,
    auth={"token": "ghp_xxx"}
)

# Context automatically flows between calls
repos = ocp.call(
    method="GET", 
    url="https://api.github.com/user/repos",
    context=context  # Same context, accumulated state
)
```

### 3. Enable AI Agents
```python
from openai import OpenAI
import ocp

client = OpenAI()
context = ocp.Context()

# AI can call any OCP-enabled API
tools = ocp.discover_from_openapi([
    "https://weather-api.com/openapi.json",
    "https://calendar-api.com/openapi.json"
])

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the weather in NYC?"}],
    tools=tools,
    context=context  # OCP context flows automatically
)
```

---

## Specification Status

**Current Version**: 1.0  
**Status**: Draft  
**License**: MIT  

### Contributing
1. Add examples to `examples/` directory
2. Submit OpenAPI extensions to `schemas/`
3. Build reference implementations in `tools/`
4. Create migration guides in `docs/migration/`

### Reference Implementations
- Python: `ocp-python` (planned)
- JavaScript: `ocp-js` (planned)  
- Go: `ocp-go` (planned)
- CLI: `ocp-cli` (planned)

---

**The goal**: Make AI context sharing as simple as adding HTTP headers to APIs you already have.

**No servers. No new protocols. Just standards.**