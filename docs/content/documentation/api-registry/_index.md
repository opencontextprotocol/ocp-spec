---
title: "API Registry"
weight: 3
cascade:
  type: docs
---

Community-maintained registry for instant API tool discovery.

## What It Is

The registry pre-indexes popular OpenAPI specs so agents get tools instantly.

```python
from ocp_agent import OCPAgent

agent = OCPAgent()

# Fast registry lookup
github = agent.register_api("github")   # → 800+ tools
stripe = agent.register_api("stripe")   # → 300+ tools

# Falls back to direct OpenAPI parsing
custom = agent.register_api("my-api", "https://api.example.com/openapi.json")
```

## Popular APIs

**Developer Tools:** GitHub, GitLab, Bitbucket  
**Payments:** Stripe, PayPal, Square  
**Communication:** Slack, Discord, Twilio  
**Cloud:** AWS, Azure, Google Cloud  

## How It Works

- **Community Maintained**: Popular APIs are pre-indexed and verified by the community.
- **Automatic Fallback**: If API not in registry, fetches and parses OpenAPI spec.
- **Optional**: Registry provides speed and convenience.. OCP works without it.

## Benefits

- **Instant tools** for popular APIs
- **Community verified** specifications
- **Automatic fallback** for custom APIs
- **Zero configuration** required
