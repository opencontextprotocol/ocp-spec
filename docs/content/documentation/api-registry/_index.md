---
title: "API Registry"
weight: 3
cascade:
  type: docs
---

Community-maintained registry for instant API tool discovery - 50ms vs 2-5 seconds.

## What It Is

The registry pre-indexes popular OpenAPI specs so agents get tools instantly instead of waiting for spec parsing.

**Performance:**
- **Registry lookup**: 50ms for GitHub, Stripe, Slack, etc.
- **Direct OpenAPI**: 2-5 seconds for custom APIs
- **Fallback**: Registry → OpenAPI parsing automatically

```python
from ocp_agent import OCPAgent

agent = OCPAgent()

# Fast registry lookup
github = agent.register_api("github")    # 50ms → 800+ tools
stripe = agent.register_api("stripe")    # 50ms → 300+ tools

# Falls back to direct OpenAPI parsing
custom = agent.register_api("my-api", "https://api.example.com/openapi.json")  # 2-5s
```

## Popular APIs

**Developer Tools:** GitHub, GitLab, Bitbucket  
**Payments:** Stripe, PayPal, Square  
**Communication:** Slack, Discord, Twilio  
**Cloud:** AWS, Azure, Google Cloud  

## How It Works

**Community Maintained**: Popular APIs are pre-indexed and verified by the community.

**Automatic Fallback**: If API not in registry, automatically fetches and parses OpenAPI spec.

**Optional**: Registry is just a speed optimization - OCP works without it.

## Benefits

- **Instant tools** for popular APIs
- **Community verified** specifications
- **Automatic fallback** for custom APIs
- **Zero configuration** required
