---
title: "Tool Discovery"
weight: 2
cascade:
  type: docs
---

Automatically convert any OpenAPI specification into hundreds of callable tools.

```python
from ocp_agent import OCPAgent

agent = OCPAgent()

# One spec → 800+ instant tools
github = agent.register_api("github")   # ms from registry
stripe = agent.register_api("stripe")   # ms from registry  

# Each endpoint becomes callable
agent.call_tool("search_issues", {"q": "bug"})
agent.call_tool("create_payment_intent", {"amount": 2000})
```

## How It Works

- **OpenAPI Analysis**: OCP extracts endpoints, parameters, and schemas.
- **Tool Generation**: Each operation becomes a callable tool with deterministic naming.
- **Smart Caching**: Memory → Cache → Registry → Network lookup chain.
- **Built-in Validation**: All parameters validated against OpenAPI schemas automatically.

## Benefits

**🔥 Instant Tools**: Any OpenAPI spec becomes hundreds of callable tools  
**⚡ Registry Speed**: 50ms lookup vs 2-5 seconds for popular APIs  
**✅ Auto Validation**: Parameters validated against schemas  
**🎯 Zero Setup**: Works with existing APIs, no infrastructure required
