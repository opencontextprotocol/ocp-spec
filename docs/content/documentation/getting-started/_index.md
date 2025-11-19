---
title: Getting Started
weight: 1
cascade:
  type: docs
---

Set up OCP and turn any API into hundreds of agent tools in seconds.

## Prerequisites

- Python 3.8+ or Node.js 16+
- GitHub token for API access

## Authentication

{{< tabs items="Python,JavaScript,VS Code" >}}

{{< tab >}}
Get a GitHub token:
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` scope
3. Save it as environment variable:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```
{{< /tab >}}

{{< tab >}}
Get a GitHub token:
1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Generate a new token with `repo` scope
3. Save it as environment variable:

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```
{{< /tab >}}

{{< tab >}}
Configure API authentication in VS Code settings:
1. Open VS Code settings (Cmd/Ctrl + ,)
2. Search for "ocp"
3. Add your GitHub token:

```json
{
  "ocp.apiAuth": {
    "github": {
      "Authorization": "Bearer ghp_your_token_here"
    }
  }
}
```
{{< /tab >}}

{{< /tabs >}}

## Installation

{{< tabs items="Python,JavaScript,VS Code" >}}

{{< tab >}}
```bash
pip install ocp-python
```
{{< /tab >}}

{{< tab >}}
```bash
npm install @opencontextprotocol/agent
```
{{< /tab >}}

{{< tab >}}
```bash
ext install opencontextprotocol.ocp-vscode
```
{{< /tab >}}

{{< /tabs >}}

## First Usage

{{< tabs items="Python,JavaScript,VS Code" >}}

{{< tab >}}
```python
import ocp
import os

# Create agent
agent = ocp.OCPAgent(workspace="my-project")

# Register GitHub API
github_spec = agent.register_api("github")
print(f"{len(github_spec.tools)} tools discovered from GitHub API")

# Use tools with authentication
headers = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}
issues = agent.call_tool("github", "search_issues", {"q": "bug"}, headers=headers)
```
{{< /tab >}}

{{< tab >}}
```javascript
import { OCPAgent } from '@opencontextprotocol/agent';

// Create agent
const agent = new OCPAgent({workspace: "my-project"});

// Register GitHub API
const githubSpec = await agent.registerApi("github");
console.log(`${githubSpec.tools.length} tools discovered from GitHub API`);

// Use tools with authentication
const headers = {"Authorization": `Bearer ${process.env.GITHUB_TOKEN}`};
const issues = await agent.callTool("github", "search_issues", {q: "bug"}, {headers});
```
{{< /tab >}}

{{< tab >}}
1. Open VS Code in your project folder
2. Install the OCP extension (if not already done)
3. Use Copilot Chat or any AI agent:

```
@workspace Please use the ocp_registerApi tool to register the GitHub API, then use ocp_listTools to see what's available.
```

The AI agent will:
- Register GitHub API (using your configured auth)
- Show you hundreds of available tools
- Use tools with full workspace context
{{< /tab >}}

{{< /tabs >}}

## Next Steps

{{< cards >}}
{{< card link="../tools/" title="Tool Discovery" subtitle="Add your own APIs and discover more tools" icon="cog" >}}
{{< card link="../examples/" title="Examples" subtitle="Real-world use cases and implementations" icon="book-open" >}}
{{< card link="../context/" title="Understanding Context" subtitle="How persistent context enhances responses" icon="chat" >}}
{{< card link="../ide/" title="IDE Integration" subtitle="VS Code workspace integration" icon="code" >}}
{{< /cards >}}