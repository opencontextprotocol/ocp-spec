---
title: "Context Schema"
weight: 2
---

# Context Schema

The `OCP-Session` header contains a Base64-encoded JSON object that represents the full agent context.

## Minimal Context (Level 1)

Every OCP context must include these required fields:

```json
{
  "context_id": "ocp-debug-payment-abc123",
  "agent_type": "ide_coding_assistant",
  "created_at": "2025-11-15T10:30:00Z",
  "last_updated": "2025-11-15T10:35:00Z"
}
```

### Required Fields

| Field | Type | Description | Max Length |
|-------|------|-------------|------------|
| `context_id` | string | Unique session identifier | 64 chars |
| `agent_type` | string | Type of agent (IDE, CLI, etc.) | 128 chars |
| `created_at` | string | ISO 8601 timestamp of context creation | - |
| `last_updated` | string | ISO 8601 timestamp of last update | - |

## Extended Context (Recommended)

Include additional fields for richer context:

```json
{
  "context_id": "ocp-debug-payment-abc123",
  "agent_type": "ide_coding_assistant", 
  "user": "alice",
  "workspace": "ecommerce-backend",
  "current_goal": "debug_payment_validation_error",
  "current_file": "payment_validator.py",
  "git_branch": "fix-payment-error",
  "session": {
    "interaction_count": 7,
    "last_api_call": "github.list_repository_issues",
    "tools_used": ["github", "stripe"]
  },
  "workspace_context": {
    "project_type": "python_web_app",
    "framework": "django",
    "recent_files": [
      "payment_validator.py",
      "test_payment_validation.py",
      "payment_models.py"
    ]
  },
  "history": [
    {
      "timestamp": "2025-11-15T10:30:00Z",
      "action": "file_opened",
      "file": "payment_validator.py"
    },
    {
      "timestamp": "2025-11-15T10:31:00Z",
      "action": "api_call",
      "api": "github",
      "operation": "list_repository_issues",
      "result": "success",
      "context": "searching for similar payment validation errors"
    },
    {
      "timestamp": "2025-11-15T10:33:00Z",
      "action": "test_run",
      "result": "failed",
      "error": "ValidationError: Invalid card number format"
    }
  ],
  "created_at": "2025-11-15T10:30:00Z",
  "last_updated": "2025-11-15T10:35:00Z"
}
```

## Context Fields Reference

### Core Identity
- **`user`**: User identifier (`"alice"`, `"dev-team-lead"`)
- **`workspace`**: Project/workspace name (`"ecommerce-backend"`)
- **`current_goal`**: Active objective (`"debug_payment_validation_error"`)

### Workspace Context
- **`current_file`**: Currently active file (`"payment_validator.py"`)
- **`git_branch`**: Current git branch (`"fix-payment-error"`)
- **`workspace_context`**: Project metadata (frameworks, recent files, etc.)

### Session Tracking
- **`session.interaction_count`**: Number of API interactions
- **`session.last_api_call`**: Most recent API operation
- **`session.tools_used`**: List of APIs/tools used in session

### History Tracking
- **`history[]`**: Array of interaction events
- **`history[].timestamp`**: ISO 8601 timestamp
- **`history[].action`**: Type of action (`"api_call"`, `"file_opened"`, `"test_run"`)
- **`history[].result`**: Operation result (`"success"`, `"failed"`)

## Context Evolution

Context objects grow and evolve throughout an agent session:

### Session Start
```json
{
  "context_id": "ocp-debug-payment-abc123",
  "agent_type": "ide_coding_assistant",
  "user": "alice",
  "created_at": "2025-11-15T10:30:00Z",
  "last_updated": "2025-11-15T10:30:00Z"
}
```

### After Goal Setting
```json
{
  "context_id": "ocp-debug-payment-abc123",
  "agent_type": "ide_coding_assistant",
  "user": "alice",
  "current_goal": "debug_payment_validation_error",
  "workspace": "ecommerce-backend",
  "created_at": "2025-11-15T10:30:00Z",
  "last_updated": "2025-11-15T10:31:00Z"
}
```

### After API Interactions
```json
{
  "context_id": "ocp-debug-payment-abc123",
  "agent_type": "ide_coding_assistant",
  "user": "alice",
  "current_goal": "debug_payment_validation_error",
  "workspace": "ecommerce-backend",
  "session": {
    "interaction_count": 3,
    "last_api_call": "github.list_repository_issues",
    "tools_used": ["github"]
  },
  "history": [
    {
      "timestamp": "2025-11-15T10:31:00Z",
      "action": "api_call",
      "api": "github",
      "operation": "list_repository_issues"
    }
  ],
  "created_at": "2025-11-15T10:30:00Z",
  "last_updated": "2025-11-15T10:33:00Z"
}
```

## Size & Performance Guidelines

**Maximum Size**: 8KB after Base64 encoding  
**Compression**: Use gzip compression for large contexts  
**History Limit**: Keep last 20-50 interactions to stay under size limits  
**Cleanup**: Remove old history entries when approaching size limits

**Size Optimization Tips:**
- Use short, descriptive field values
- Compress repeated data structures
- Truncate old history entries
- Use abbreviations for common patterns