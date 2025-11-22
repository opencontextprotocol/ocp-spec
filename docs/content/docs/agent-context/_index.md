---
title: "Agent Context"
next: /docs/specs
prev: /docs/ide-integration
weight: 5
cascade:
  type: docs
---

HTTP headers that carry agent context across API calls, enabling persistent conversations.

## Context Injection

OCP agents automatically inject context headers into all API calls:

```python
from ocp_agent import OCPAgent

agent = OCPAgent(
    agent_type="coding_assistant",
    user="alice", 
    workspace="payment-service"
)

# Context headers added automatically to every API call
github_api = agent.register_api("github")
issues = agent.call_tool("search_issues", {"q": "payment bug"})
```

**Generated Headers:**
```http
GET /search/issues?q=payment+bug HTTP/1.1
Host: api.github.com
Authorization: Bearer ghp_xxxxxxxxxxxx
OCP-Context-ID: ocp-abc123
OCP-Agent-Type: coding_assistant
OCP-User: alice
OCP-Workspace: payment-service
```

**Core Headers:**
- `OCP-Context-ID`: Unique conversation identifier  
- `OCP-Session`: Compressed conversation state
- `OCP-Agent-Type`: Type of AI agent

**Contextual Headers:**
- `OCP-User`: Current user
- `OCP-Workspace`: Current project
- `OCP-Current-Goal`: Agent's objective

## Context Flow Across APIs

Context persists across different APIs and builds conversation memory:

```python
agent = OCPAgent(workspace="payment-service", current_goal="debug_payment_issue")

# Each call updates the conversation history
issues = agent.call_tool("search_issues", {"q": "payment timeout"})
# -> Sets current context: recent search, found issues

logs = agent.call_tool("get_application_logs", {"service": "payments"}) 
# -> Carries forward: workspace, goal, previous search results

metrics = agent.call_tool("query_metrics", {"metric": "payment_latency"})
# -> Full context: workspace + goal + search + logs + metrics
```

**Context Updates Automatically:**
- **Interaction History**: Each API call recorded with timestamp and results
- **Current Goal**: Agent objective persists across different APIs  
- **Recent Changes**: Track modifications for debugging context
- **Error Context**: Automatic error state capture

## Session Persistence

Conversations persist across agent sessions with automatic save/restore:

```python
# Save conversation state
agent.storage.save_session("debug-session-123", agent.context)

# Later: restore full conversation context
agent = OCPAgent()
restored_context = agent.storage.load_session("debug-session-123") 
agent.context = restored_context

# Continue where you left off with full history
agent.call_tool("create_issue", {
    "title": "Payment timeout issue",
    "body": "Based on previous investigation..."  # AI has full context
})
```

**Session Management:**
```python
# List all saved conversations
sessions = agent.storage.list_sessions(limit=10)
# [{"id": "debug-session-123", "last_updated": "2025-11-22T10:30:00Z", ...}]

# Clean up old sessions
agent.storage.cleanup_sessions(keep_recent=25)
```

## Context Debugging

View context headers to troubleshoot conversation state:

```python
from ocp_agent.headers import OCPHeaders

# Get readable context summary
headers = agent.context.to_headers()
summary = OCPHeaders.get_context_summary(headers)
print(summary)
# Output: "OCP Context: ocp-abc123 | Agent: coding_assistant | Goal: debug_payment | Workspace: payment-service"

# Inspect full context
print(f"Context ID: {agent.context.context_id}")
print(f"Conversation: {len(agent.context.history)} interactions")
print(f"Goal: {agent.context.current_goal}")
print(f"Recent: {agent.context.recent_changes}")
```

**Header Compression:**
- Sessions >1KB automatically compressed with gzip
- Base64 encoded for HTTP header compatibility
- Decompressed transparently by receiving clients

## Working with Any API

Context headers work immediately with any HTTP API ([Level 1 compatibility](/docs/specs/#level-1-context-aware)):

```python
# Works with any API - no server changes required
import requests
from ocp_agent import AgentContext

context = AgentContext(workspace="ecommerce", current_goal="process_order")
headers = context.to_headers()

# Add to any HTTP request
response = requests.get(
    "https://api.stripe.com/v1/payment_intents",
    headers={**headers, "Authorization": "Bearer sk_test_..."}
)

# Context flows through, even if API doesn't use it
# Future: Level 2 APIs will provide enhanced responses
```

**Benefits:**
- **Zero Infrastructure**: Works with existing APIs immediately
- **Persistent Memory**: Full conversation history across API calls  
- **Cross-API Workflows**: Context bridges different services
- **Session Recovery**: Resume conversations after restarts
- **Automatic State**: No manual context management required
