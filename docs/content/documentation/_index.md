---
title: Documentation
---

Turn any OpenAPI spec into hundreds of agent tools instantly.

## Core Features

{{< cards >}}
{{< card title="Tool Discovery" subtitle="Auto-generate tools from OpenAPI specs" link="tools/" icon="cog" >}}
{{< card title="HTTP Context" subtitle="Persistent state across API calls" link="context/" icon="chat" >}}
{{< card title="Marketplace" subtitle="Pre-indexed API catalog" link="registry/" icon="collection" >}}
{{< card title="IDE Integration" subtitle="Workspace-aware agents" link="ide/" icon="code" >}}
{{< /cards >}}

## How It Works

```python
from ocp_agent import OCPAgent

agent = OCPAgent(workspace="ecommerce-app")

# Registry lookup + instant tool discovery
github_api = agent.register_api("github")           # 800+ tools from registry
stripe_api = agent.register_api("stripe")           # 300+ tools from registry

# Use any tool with auth + context automatically
issues = agent.call_tool("search_issues", {"q": "payment"}, 
                        headers={"Authorization": f"token {github_token}"})
payment = agent.call_tool("create_payment_intent", {"amount": 2000},
                         headers={"Authorization": f"Bearer {stripe_key}"})
```

**The Magic:**
- 🔥 **Registry Integration**: Just name the API → get instant access
- 🚀 **Auto Tool Discovery**: Hundreds of tools from OpenAPI specs automatically  
- 🧠 **Workspace Context**: Every tool call knows your project context
- 🔐 **Simple Auth**: Pass headers inline, no complex setup

## Next

Dive into the following section to begin using OCP:

{{< cards >}}
{{< card link="getting-started/" title="Getting Started" subtitle="Setup and first usage" icon="play" >}}
{{< /cards >}}