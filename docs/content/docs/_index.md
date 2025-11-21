---
title: Introduction
linkTItle: Documentation
---

Turn any OpenAPI spec into hundreds of agent tools instantly.

## Core Features

{{< cards >}}
{{< card title="Tool Discovery" subtitle="Auto-generate tools from OpenAPI specs" link="tool-discovery/" icon="cog" >}}
{{< card title="Registry" subtitle="Pre-indexed API catalog for speed" link="api-registry/" icon="collection" >}}
{{< card title="IDE Integration" subtitle="VS Code Language Model tools" link="ide-integration/" icon="code" >}}
{{< card title="Context Protocol" subtitle="HTTP headers for state sharing" link="agent-context/" icon="chat" >}}
{{< /cards >}}

## How It Works

```python
from ocp_agent import OCPAgent

agent = OCPAgent(workspace="ecommerce-app")

# Tool Discovery: OpenAPI → hundreds of tools automatically
github_api = agent.register_api("github")   # fast registry lookup → 800+ tools
stripe_api = agent.register_api("stripe")   # fast registry lookup → 300+ tools

# Or discover directly from OpenAPI spec (2-5 seconds)
custom_api = agent.register_api("my-api", "https://api.example.com/openapi.json")

# Use any discovered tool with automatic context injection
issues = agent.call_tool("search_issues", {"q": "payment bug"})
payment = agent.call_tool("create_payment_intent", {"amount": 2000})
```

**The Value:**
- 🔥 **Instant Tools**: OpenAPI specs become hundreds of callable tools automatically  
- 🚀 **Registry Speed**: Huge library of popular APIs pre-indexed for fast lookup
- 🧠 **Smart Context**: HTTP headers carry state across all tool calls
- 🔐 **Simple Integration**: Works with existing APIs, no server setup required

## Next

Dive into the following section to begin using OCP:

{{< cards >}}
{{< card link="getting-started/" title="Getting Started" subtitle="Setup and first usage" icon="play" >}}
{{< /cards >}}