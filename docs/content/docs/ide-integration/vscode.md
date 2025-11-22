---
title: "VS Code"
prev: /docs/ide-integration
next: /docs/agent-context
weight: 1
cascade:
  type: docs
---

VS Code extension that provides OCP tools to any AI agent through Language Model Tools API.

## Extension Installation

1. Open VS Code Extensions (Ctrl+Shift+X)
2. Search "Open Context Protocol"
3. Install the extension
4. Restart VS Code

The extension automatically registers 5 OCP tools that any AI agent can use.

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
    "github": {
      "Authorization": "Bearer ghp_your_github_token"
    },
    "stripe": {
      "Authorization": "Bearer sk_your_stripe_key"
    }
  }
}
```

**Settings:**
- `ocp.user` - User identifier (defaults to git username)
- `ocp.registryUrl` - Registry URL for API discovery
- `ocp.apiAuth` - API authentication headers by API name

## API Authentication

API credentials are stored securely in VS Code settings and automatically merged with tool parameters:

**GitHub Token Setup:**
1. Generate token at github.com/settings/tokens
2. Add to settings: `"github": {"Authorization": "Bearer ghp_xxx"}`
3. Agents can now call GitHub tools without exposing your token

**Stripe API Key Setup:**
1. Get API key from Stripe dashboard
2. Add to settings: `"stripe": {"Authorization": "Bearer sk_xxx"}`
3. Agents can process payments, create customers, etc.

**Security:**
- Credentials stay in VS Code settings
- Never exposed to AI agents
- Automatically injected during tool execution

## Next: Agent Context

With OCP tools available in your IDE, learn how [Agent Context](/docs/agent-context) maintains state and provides intelligent context management across your development workflow.