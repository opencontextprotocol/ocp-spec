---
title: Getting Started
weight: 1
cascade:
  type: docs
---

Turn any OpenAPI spec into hundreds of agent tools in seconds.

## Installation & Quick Start

{{< tabs items="Python,JavaScript,VS Code" >}}

{{< tab >}}
**Prerequisites:** Python 3.8+

```bash
# Install the library
pip install open-context-agent
```

**Quick Start:**
```python
from ocp_agent import OCPAgent
import os

# Set your GitHub token
os.environ['GITHUB_TOKEN'] = 'ghp_your_token_here'

# Create an agent with workspace context
agent = OCPAgent(
    agent_type="api_explorer",
    workspace="my-project"
)

# Register GitHub API (discovers all available tools automatically)
api_spec = agent.register_api(
    name="github", 
    spec_url="https://api.github.com/openapi.json"
)
print(f"🚀 Auto-discovered {len(api_spec.tools)} tools!")

# That's it. No manual tool definitions, no proxy servers.
# You now have access to the entire GitHub API as agent tools.

# List some tools
tools = agent.list_tools("github")
print(f"Available: {[tool.name for tool in tools[:5]]}...")

# Call any tool
issues = agent.call_tool("search_issues",
    {"q": "bug in:readme"},
    headers={"Authorization": f"token {os.getenv('GITHUB_TOKEN')}"}))
```
{{< /tab >}}

{{< tab >}}
**Prerequisites:** Node.js 16+

```bash
# Install the library
npm install @opencontextprotocol/agent
```

**Quick Start:**
```typescript
import { OCPAgent } from '@opencontextprotocol/agent';

// Set environment variable
process.env.GITHUB_TOKEN = 'ghp_your_token_here';

// Create an agent with workspace context
const agent = new OCPAgent(
    'api_explorer',
    undefined,
    'my-project'
);

# Register GitHub API (discovers all available tools automatically)
const apiSpec = await agent.registerApi(
    'github',
    'https://api.github.com/openapi.json'
);
console.log(`🚀 Auto-discovered ${apiSpec.tools.length} tools!`);

// That's it. No manual tool definitions, no proxy servers.
// You now have access to the entire GitHub API as agent tools.

// List some tools
const tools = agent.listTools('github');
console.log(`Available: ${tools.slice(0, 5).map(t => t.name).join(', ')}...`);

// Call any tool
const issues = await agent.callTool('search_issues',
    {q: 'bug in:readme'},
    {headers: {'Authorization': `token ${process.env.GITHUB_TOKEN}`}});
```
{{< /tab >}}

{{< tab >}}
**Prerequisites:** VS Code

```bash
# Install the extension
code --install-extension opencontextprotocol.ocp-vscode-extension
```

**Auth Setup:**
1. Get a GitHub token with `repo` scope
2. Open VS Code settings in JSON mode  
3. Search for `ocp` and add your token:

```json
{
  "ocp.apiAuth": {
    "github": {
      "Authorization": "Bearer ghp_your_token_here"
    }
  }
}
```

**Quick Start:**
1. Open VS Code in your project folder
2. Open any AI chat (Copilot, Cursor, etc.)
3. Try this prompt:

```
Use ocp to register the GitHub API, then show me what tools you discovered.
```
{{< /tab >}}

{{< /tabs >}}

## What You Just Did

🤯 **Auto Tool Discovery**: One API registration = hundreds of tools instantly available.

⚡ **Direct Integration**: OCP talks directly to APIs using their OpenAPI specs.

🔧 **Zero Setup**: No servers, no containers, no infrastructure required.

## Next Steps

Dive into the following sections to learn more about OCP:

{{< cards >}}
{{< card link="../examples/" title="More Examples" subtitle="Stripe, Slack, and other real-world integrations" icon="book-open" >}}
{{< card link="../tools/" title="Add Any API" subtitle="Turn any OpenAPI spec into agent tools" icon="cog" >}}
{{< card link="../context/" title="Context Deep Dive" subtitle="How workspace context enhances tool responses" icon="chat" >}}
{{< /cards >}}