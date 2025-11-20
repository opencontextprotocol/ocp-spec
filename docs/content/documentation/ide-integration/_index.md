---
title: "IDE Integration"
weight: 4
cascade:
  type: docs
---

VS Code extension that gives any AI agent access to OCP's capabilities.

## What It Does

Install the OCP extension in VS Code, and every chat agent automatically gets access to hundreds of API tools and persistent context.

**For Users:**
- Install extension once
- Configure API keys in VS Code settings
- Every AI agent can now use GitHub, Stripe, Slack, etc.

**For AI Agents:**
- Register APIs: "Add GitHub API"
- Discover tools: "What GitHub tools are available?"
- Execute workflows: "Search issues and create JIRA tickets"

## How It Works

Extension registers 5 tools that any VS Code AI agent can use:
- `ocp_registerApi` - Register GitHub, Stripe, etc.
- `ocp_listTools` - See available tools
- `ocp_callTool` - Execute any tool
- `ocp_searchTools` - Find tools by name
- `ocp_getContext` - Get workspace info

## Setup

1. **Install**: Search "Open Context Protocol" in VS Code Extensions
2. **Configure**: Add API keys to VS Code settings:
   ```json
   {
     "ocp.apiAuth": {
       "github": {"Authorization": "Bearer ghp_your_token"},
       "stripe": {"Authorization": "Bearer sk_your_key"}
     }
   }
   ```
3. **Use**: Chat with any AI agent.. they now have access to thousands of API tools

## Benefits

- **Universal**: Works with any AI agent in VS Code
- **Secure**: API keys in settings, not exposed to agents  
- **Instant**: Zero configuration, works immediately
- **Contextual**: Tools know your current workspace
