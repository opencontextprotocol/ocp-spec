---
title: "Tool Discovery"
weight: 10
cascade:
  type: docs
---

OCP's core innovation: automatically convert any OpenAPI specification into hundreds of callable tools with deterministic names and proper validation.

## Overview

OCP's core innovation: automatically convert any OpenAPI specification into hundreds of callable tools.

```python
from ocp_agent import OCPAgent

agent = OCPAgent()

# One spec → 800+ instant tools
github = agent.register_api("github")      # 50ms from registry
stripe = agent.register_api("stripe")      # 50ms from registry  

# Each endpoint becomes callable
agent.call_tool("search_issues", {"q": "bug"})
agent.call_tool("create_payment_intent", {"amount": 2000})
```

## How It Works

**OpenAPI Analysis**: OCP parses specifications and extracts endpoints, parameters, and schemas.

**Tool Generation**: Each operation becomes a callable tool with deterministic naming (e.g., `repos/list-for-repo` → `list_repo_issues`).

**Smart Caching**: Memory (0ms) → Cache (1ms) → Registry (50ms) → Network (2-5s) lookup chain.

**Built-in Validation**: All parameters validated against OpenAPI schemas automatically.

## Key Benefits

**🔥 Instant Tools**: Any OpenAPI spec becomes hundreds of callable tools  
**⚡ Registry Speed**: 50ms lookup vs 2-5 seconds for popular APIs  
**✅ Auto Validation**: Parameters validated against schemas  
**🎯 Zero Setup**: Works with existing APIs, no infrastructure required

## Next Steps

{{< cards >}}
{{< card link="../registry/" title="Registry" subtitle="50ms lookup for popular APIs" icon="collection" >}}
{{< card link="../ide/" title="IDE Integration" subtitle="VS Code Language Model tools" icon="code" >}}
{{< card link="../getting-started/" title="Get Started" subtitle="Install and first usage" icon="play" >}}
{{< /cards >}}