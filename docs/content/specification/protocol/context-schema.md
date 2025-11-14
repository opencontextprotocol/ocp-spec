---
title: Context Schema
weight: 2
---

The `OCP-Session` header contains a Base64-encoded JSON object that carries agent context across API calls.

## Minimal Context

All context objects must include these fields:

```json
{
  "context_id": "ocp-a1b2c3d4",
  "agent_type": "ide_coding_assistant",
  "created_at": "2025-10-24T15:30:00Z",
  "last_updated": "2025-10-24T15:35:00Z"
}
```

## Extended Context

Optional fields for richer context:

```json
{
  "context_id": "ocp-a1b2c3d4",
  "agent_type": "ide_coding_assistant", 
  "user": "alice",
  "workspace": "payment-service",
  "current_goal": "debug_deployment_failure",
  "session": {
    "interaction_count": 5,
    "last_api_call": "github.listRepositoryIssues",
    "start_time": "2025-10-24T15:30:00Z"
  },
  "history": [
    {
      "timestamp": "2025-10-24T15:30:00Z",
      "action": "api_call",
      "api": "github",
      "operation": "listRepositoryIssues",
      "result": "success"
    }
  ],
  "workspace_context": {
    "current_files": ["payment.py", "test_payment.py"],
    "recent_changes": ["fix payment validation"]
  },
  "created_at": "2025-10-24T15:30:00Z",
  "last_updated": "2025-10-24T15:35:00Z"
}
```

## Field Definitions

### Required Fields

- **`context_id`**: Must match `OCP-Context-ID` header value
- **`agent_type`**: Must match `OCP-Agent-Type` header value  
- **`created_at`**: ISO 8601 timestamp of context creation
- **`last_updated`**: ISO 8601 timestamp of last modification

### Optional Fields

- **`user`**: User identifier for multi-user environments
- **`workspace`**: Current workspace or project name
- **`current_goal`**: Agent's current objective or task
- **`session`**: Session-specific metadata and statistics
- **`history`**: Array of recent actions and API calls
- **`workspace_context`**: Environment-specific context (files, state, etc.)

## Context Evolution

Context objects grow over time as agents interact with APIs:

```json
// Initial context
{
  "context_id": "ocp-abc123",
  "agent_type": "coding_assistant",
  "created_at": "2025-10-24T15:30:00Z",
  "last_updated": "2025-10-24T15:30:00Z"
}

// After GitHub API calls
{
  "context_id": "ocp-abc123",
  "agent_type": "coding_assistant",
  "current_goal": "debug_tests",
  "session": {
    "interaction_count": 3
  },
  "history": [
    {"action": "api_call", "api": "github", "operation": "listIssues"},
    {"action": "api_call", "api": "github", "operation": "getIssue"}
  ],
  "created_at": "2025-10-24T15:30:00Z",
  "last_updated": "2025-10-24T15:32:00Z"
}
```

## Size Management

Keep context objects under 8KB encoded:

- **Focus on recent history**: Limit history arrays to recent actions
- **Summarize old data**: Replace old detailed history with summaries
- **Use compression**: Enable gzip compression for large contexts
- **Prune unused fields**: Remove fields not relevant to current goal