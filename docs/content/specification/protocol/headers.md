---
title: HTTP Headers
weight: 1
---

OCP uses standard HTTP headers to transmit context information between agents and APIs.

## Required Headers

### `OCP-Context-ID`
- **Purpose**: Unique identifier for the agent session
- **Format**: Max 64 characters, alphanumeric + hyphens
- **Example**: `ocp-a1b2c3d4`

### `OCP-Agent-Type`  
- **Purpose**: Type of agent making the request
- **Format**: Max 128 characters
- **Example**: `ide_coding_assistant`, `cli_tool`, `jupyter_notebook`

## Optional Headers

### `OCP-Agent-Goal`
- **Purpose**: Current agent objective or task
- **Format**: Max 256 characters  
- **Example**: `debug_deployment_failure`, `implement_new_feature`

### `OCP-Session`
- **Purpose**: Base64-encoded JSON context object
- **Format**: Max 8KB after encoding
- **Example**: `eyJjb250ZXh0X2lkIjoib2NwLWExYjJjM2Q0In0=`

### `OCP-User`
- **Purpose**: User identifier for multi-user environments
- **Format**: Max 64 characters
- **Example**: `alice`, `user123`

### `OCP-Workspace`
- **Purpose**: Current workspace or project context
- **Format**: Max 128 characters
- **Example**: `payment-service`, `mobile-app`

## Complete Example

```http
GET /repos/owner/payment-service/issues HTTP/1.1
Host: api.github.com
Authorization: Bearer ghp_xxxxxxxxxxxx
OCP-Context-ID: ocp-debug-abc123
OCP-Agent-Type: ide_coding_assistant
OCP-Agent-Goal: debug_deployment_failure
OCP-User: alice
OCP-Workspace: payment-service
OCP-Session: eyJjb250ZXh0X2lkIjoib2NwLWRlYnVnLWFiYzEyMyIsImFnZW50X3R5cGUiOiJpZGVfY29kaW5nX2Fzc2lzdGFudCJ9
```

## Header Processing

**Client Libraries**: Automatically inject headers into HTTP requests based on current agent context.

**API Servers**: Can read headers for enhanced responses (Level 2) or ignore them entirely (Level 1).

**Proxies/CDNs**: Headers pass through standard HTTP infrastructure without modification.