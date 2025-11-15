---
title: "HTTP Headers"
weight: 1
---

# HTTP Headers

OCP uses standard HTTP headers to transmit context information between agents and APIs.

## Required Headers

### `OCP-Context-ID`
- **Purpose**: Unique identifier for the agent session
- **Format**: Max 64 characters, alphanumeric + hyphens
- **Example**: `ocp-debug-payment-abc123`

```http
OCP-Context-ID: ocp-debug-payment-abc123
```

### `OCP-Agent-Type`  
- **Purpose**: Type of agent making the request
- **Format**: Max 128 characters
- **Example**: `ide_coding_assistant`, `cli_tool`, `jupyter_notebook`

```http
OCP-Agent-Type: ide_coding_assistant
```

## Optional Headers

### `OCP-Agent-Goal`
- **Purpose**: Current agent objective or task
- **Format**: Max 256 characters  
- **Example**: `debug_deployment_failure`, `implement_payment_feature`

```http
OCP-Agent-Goal: debug_payment_validation_error
```

### `OCP-Session`
- **Purpose**: Base64-encoded JSON context object
- **Format**: Max 8KB after encoding
- **Compression**: Optional gzip compression before Base64 encoding

```http
OCP-Session: eyJjb250ZXh0X2lkIjoib2NwLWRlYnVnLXBheW1lbnQtYWJjMTIzIiwiYWdlbnRfdHlwZSI6ImlkZV9jb2RpbmdfYXNzaXN0YW50In0=
```

### `OCP-User`
- **Purpose**: User identifier for multi-user environments
- **Format**: Max 64 characters
- **Example**: `alice`, `user123`, `dev-team-lead`

```http
OCP-User: alice
```

### `OCP-Workspace`
- **Purpose**: Current workspace or project context
- **Format**: Max 128 characters
- **Example**: `payment-service`, `mobile-app`, `data-pipeline`

```http
OCP-Workspace: ecommerce-backend
```

## Complete Example

Here's a real-world example of OCP headers in action:

```http
GET /repos/acme-corp/ecommerce-backend/issues HTTP/1.1
Host: api.github.com
Authorization: Bearer ghp_xxxxxxxxxxxx
OCP-Context-ID: ocp-debug-payment-abc123
OCP-Agent-Type: ide_coding_assistant
OCP-Agent-Goal: debug_payment_validation_error
OCP-User: alice
OCP-Workspace: ecommerce-backend
OCP-Session: eyJjb250ZXh0X2lkIjoib2NwLWRlYnVnLXBheW1lbnQtYWJjMTIzIiwiYWdlbnRfdHlwZSI6ImlkZV9jb2RpbmdfYXNzaXN0YW50IiwiY3VycmVudF9nb2FsIjoiZGVidWdfcGF5bWVudF92YWxpZGF0aW9uX2Vycm9yIiwiY3VycmVudF9maWxlIjoicGF5bWVudF92YWxpZGF0b3IucHkiLCJnaXRfYnJhbmNoIjoiZml4LXBheW1lbnQtZXJyb3IifQ==
```

## Header Processing

### Client Libraries
Automatically inject headers into HTTP requests based on current agent context:

```python
# Python
agent = OCPAgent(goal="debug_payment_error")
# Headers automatically added to all subsequent requests

# JavaScript  
const agent = new OCPAgent({goal: "debug_payment_error"});
// Headers flow automatically with every API call
```

### API Servers
- **Level 1**: Can read headers for enhanced responses (optional)
- **Level 2**: Use context for intelligent, context-aware responses
- **Fallback**: Ignore headers entirely - requests work normally

### Infrastructure Compatibility
- **CDNs/Proxies**: Headers pass through unchanged
- **Load Balancers**: Standard HTTP header forwarding
- **API Gateways**: No special handling required
- **Caching**: Context-aware caching strategies possible

## Security & Privacy

**✅ Safe by Design**: Never include sensitive data in context headers  
**✅ Size Limits**: 8KB limit prevents abuse and ensures performance  
**✅ Optional**: APIs work normally even if they ignore OCP headers  
**✅ Logging**: Consider context privacy in request logging