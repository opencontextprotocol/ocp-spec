---
title: Implementation Examples
weight: 3
---

Practical examples of implementing OCP in different scenarios.

## Basic Usage

### Minimal Context
```python
import ocp

# Create agent with minimal context
agent = ocp.Agent("debug-session")
agent.set_goal("investigate_payment_failures") 

# Discover and use tools
github = ocp.discover_tools("github")
repos = github.list_repositories()
```

**Generated HTTP Request**:
```http
GET /user/repos HTTP/1.1
Host: api.github.com
Authorization: Bearer token
OCP-Context-ID: debug-session
OCP-Agent-Type: python_agent
OCP-Agent-Goal: investigate_payment_failures
```

### Rich Context
```python
# Agent with workspace context
agent = ocp.Agent("debug-session")
agent.set_workspace("payment-service")
agent.set_user("alice")
agent.add_history("opened_file", "payment.py")
agent.add_history("test_failed", "test_payment_flow")

# All tool calls include this context
issues = github.list_issues(owner="myorg", repo="payment-service")
```

**Generated Context**:
```json
{
  "context_id": "debug-session",
  "agent_type": "python_agent",
  "user": "alice",
  "workspace": "payment-service",
  "current_goal": "investigate_payment_failures",
  "history": [
    {"action": "opened_file", "file": "payment.py"},
    {"action": "test_failed", "test": "test_payment_flow"}
  ],
  "created_at": "2025-11-13T10:00:00Z"
}
```

## Multi-API Workflows

### Cross-Platform Debugging
```python
# Register multiple APIs
github = ocp.discover_tools("github")
slack = ocp.discover_tools("slack") 
sentry = ocp.discover_tools("sentry")

# Context flows across all APIs
errors = sentry.list_errors(project="payment-service")
issue = github.create_issue(
    owner="myorg",
    repo="payment-service", 
    title=f"Payment error: {errors[0].title}",
    body=errors[0].description
)
slack.post_message(
    channel="#engineering",
    text=f"Created issue for payment error: {issue.html_url}"
)
```

Each API call includes the same session context, enabling correlation.

## Framework Integration

### FastAPI Integration
```python
from fastapi import FastAPI, Request
import ocp

app = FastAPI()

@app.middleware("http")
async def ocp_middleware(request: Request, call_next):
    # Extract OCP context
    context = ocp.extract_context(request.headers)
    
    # Make context available to handlers
    request.state.ocp_context = context
    
    response = await call_next(request)
    return response

@app.get("/api/users/{user_id}")
async def get_user(user_id: str, request: Request):
    context = request.state.ocp_context
    
    # Use context to enhance response
    if context and context.agent_goal == "debug_user_issues":
        # Include extra debug info
        return {
            "user": user_data,
            "debug_info": get_debug_info(user_id),
            "recent_activity": get_activity(user_id)
        }
    
    return {"user": user_data}
```

### Express.js Integration
```javascript
const express = require('express');
const ocp = require('ocp-js');

const app = express();

// OCP middleware
app.use((req, res, next) => {
  req.ocpContext = ocp.extractContext(req.headers);
  next();
});

app.get('/api/orders/:id', (req, res) => {
  const context = req.ocpContext;
  
  if (context?.agentGoal === 'investigate_payment_failure') {
    // Enhanced response for debugging
    return res.json({
      order: orderData,
      payment_logs: getPaymentLogs(req.params.id),
      related_errors: getRelatedErrors(req.params.id)
    });
  }
  
  res.json({ order: orderData });
});
```

## Error Handling

### Graceful Degradation
```python
try:
    # Try with OCP context
    issues = github.create_issue(title="Bug report")
except ocp.ContextError:
    # Fallback to direct API call
    issues = github_client.issues.create(
        owner="myorg",
        repo="myrepo", 
        title="Bug report"
    )
```

### Context Validation
```python
import ocp

# Validate context before API calls
agent = ocp.Agent("session-123")

if not agent.validate_context():
    agent.reset_context()
    agent.set_minimal_context()

# Proceed with validated context
tools = ocp.discover_tools("github")
```

## Best Practices

### Context Management
```python
# Start with minimal context
agent = ocp.Agent("session-id")
agent.set_goal("debug_issue")

# Add context progressively
agent.set_workspace("payment-service")
agent.add_history("file_opened", "payment.py")

# Context grows naturally with agent actions
for repo in github.list_repositories():
    if "payment" in repo.name:
        agent.add_history("found_repo", repo.name)
        issues = github.list_issues(owner="org", repo=repo.name)
```

### Tool Discovery Caching
```python
# Cache discovered tools
@lru_cache(maxsize=128)
def get_tools(api_name: str):
    return ocp.discover_tools(api_name)

# Fast subsequent access
github = get_tools("github")
stripe = get_tools("stripe")
```

### Session Persistence
```python
# Save session for later resumption
agent = ocp.Agent("debug-session")
# ... work with agent ...
agent.save_session("~/.ocp/sessions/debug-session.json")

# Resume later
agent = ocp.Agent.load_session("~/.ocp/sessions/debug-session.json")
# Context and history restored
```