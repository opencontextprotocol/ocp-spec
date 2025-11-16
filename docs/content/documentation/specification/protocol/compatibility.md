---
title: Compatibility
weight: 4
---

OCP supports two levels of API compatibility to enable gradual adoption.

## Level 1: Context Aware (Available Today)

**Description**: API receives OCP headers but doesn't modify behavior based on context.

**Implementation**: Client-side context management only - works with any existing HTTP API.

**Requirements**: 
- No server-side changes required
- API processes requests normally
- Context flows transparently through existing infrastructure

**Example**:
```http
GET /repos/owner/repo/issues HTTP/1.1
Host: api.github.com
Authorization: Bearer token
OCP-Context-ID: debug-session-123
OCP-Agent-Goal: debug_payment_issue
OCP-Session: eyJ3b3Jrc3BhY2UiOiJwYXltZW50LXNlcnZpY2UifQ==
```

The GitHub API processes this request normally, ignoring OCP headers.

## Level 2: Context Enhanced (Future)

**Description**: API reads OCP context and provides enhanced, context-aware responses.

**Implementation**: Requires API-side OCP implementation and optional OpenAPI extensions.

**Benefits**:
- Enhanced responses based on agent goals
- Context-aware suggestions and recommendations  
- Improved developer experience for AI integrations

**Example**:
```python
# API reads context and provides enhanced response
if context.agent_goal == 'debug_payment_issue':
    response['suggested_fixes'] = find_relevant_solutions(context)
    response['related_issues'] = find_similar_issues(context.workspace)
```

## Migration Path

1. **Start with Level 1**: Use OCP with existing APIs immediately
2. **Add context gradually**: Begin using context headers for session tracking
3. **Upgrade to Level 2**: Add context-aware features when ready

Level 1 compatibility ensures OCP works with any HTTP API today, while Level 2 provides a future path for enhanced integrations.