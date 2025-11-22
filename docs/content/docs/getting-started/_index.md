---
title: Getting Started
weight: 1
next: /docs/tool-discovery
prev: /docs
cascade:
  type: docs
---

Install and use OCP libraries for API tool discovery and context management.

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

# Register an API from OpenAPI spec
api_spec = agent.register_api(
    name="example_api", 
    spec_url="https://petstore3.swagger.io/api/v3/openapi.json"
)
print(f"Discovered {len(api_spec.tools)} tools")

# List available tools
tools = agent.list_tools("example_api")
print(f"Available tools: {[tool.name for tool in tools[:3]]}")

# Call a tool
result = agent.call_tool("findPetsByStatus", {"status": "available"}))
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

// Register an API from OpenAPI spec
const apiSpec = await agent.registerApi(
    'example_api',
    'https://petstore3.swagger.io/api/v3/openapi.json'
);
console.log(`Discovered ${apiSpec.tools.length} tools`);

// List available tools
const tools = agent.listTools('example_api');
console.log(`Available tools: ${tools.slice(0, 3).map(t => t.name).join(', ')}`);

// Call a tool
const result = await agent.callTool('findPetsByStatus', {status: 'available'});
```
{{< /tab >}}

{{< tab >}}
**Prerequisites:** VS Code

```bash
# Install the extension
code --install-extension opencontextprotocol.ocp-vscode-extension
```

**Configuration:**
1. Open VS Code settings (JSON mode)
2. Configure API authentication:

```json
{
  "ocp.apiAuth": {
    "petstore": {
      "api_key": "your_api_key_here"
    }
  }
}
```

**Usage:**
1. Open VS Code in your project folder
2. Use Language Model Tools to interact with OCP
3. APIs registered through OCP become available as tools
{{< /tab >}}

{{< /tabs >}}

## Next Steps

Dive into the following sections to learn more about OCP:

{{< cards >}}
{{< card link="../tool-discovery/" title="Tool Discovery" subtitle="Auto-generate tools from OpenAPI specs" icon="cog" >}}
{{< card link="../api-registry/" title="API Registry" subtitle="Fast lookup for popular APIs" icon="collection" >}}
{{< card link="../ide-integration/" title="IDE Integration" subtitle="VS Code extension for AI agents" icon="code" >}}
{{< card link="../agent-context/" title="Agent Context" subtitle="HTTP headers for persistent state" icon="chat" >}}
{{< /cards >}}