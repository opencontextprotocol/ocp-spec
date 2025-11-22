---
title: "VS Code"
prev: /docs/ide-integration
next: /docs/agent-context
weight: 1
cascade:
  type: docs
---

VS Code extension that provides OCP capabilities to any AI agent through the VS Code [Language Model Tool API](https://code.visualstudio.com/api/extension-guides/ai/tools).

## Extension Installation

1. Open VS Code Extensions
2. Search "Open Context Protocol"
3. Install the extension

## Language Model Tools

The extension registers these tools with VS Code's Language Model Tools API:

**`ocp_registerApi`** - Add APIs to make their tools available
```
Agent: "Register the GitHub API"
Result: 800+ GitHub tools now available
```

**`ocp_listTools`** - List available tools, optionally filtered by API
```
Agent: "What GitHub tools are available?"
Result: search_issues, create_issue, get_repository, etc.
```

**`ocp_callTool`** - Execute any registered tool with parameters
```
Agent: "Search for issues labeled 'bug'"
Result: Calls GitHub search_issues with label filter
```

**`ocp_searchTools`** - Find tools by name or description
```
Agent: "Find tools for creating tickets"
Result: create_issue, create_pull_request, etc.
```

**`ocp_getContext`** - Get current workspace context and session state
```
Agent: "Show me the current context"
Result: User, workspace, registered APIs, session history
```

## VS Code Settings

Configure the extension through VS Code settings:

```json
{
  "ocp.user": "john.doe",
  "ocp.registryUrl": "https://registry.opencontextprotocol.org", 
  "ocp.apiAuth": {
    "api-name": {
      "Authorization": "Bearer your-token",
      "X-Custom-Header": "custom-value"
    }
  }
}
```

**Settings:**
- `ocp.user` - User identifier (defaults to git username)
- `ocp.registryUrl` - Registry URL for API discovery
- `ocp.apiAuth` - API authentication headers by API name

## API Authentication

API credentials are stored securely in VS Code settings:

```json
{
  "ocp.apiAuth": {
    "api-name": {
      "Authorization": "Bearer your-token",
      "X-Custom-Header": "custom-value"
    }
  }
}
```

**Security:**
- Credentials stay in VS Code settings
- Never exposed to AI agents
- Automatically injected during tool execution

## Next: Agent Context

With OCP tools available in your IDE, learn how [Agent Context](/docs/agent-context) maintains state and provides intelligent context management across your development workflow.