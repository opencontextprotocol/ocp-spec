---
title: "Context"
weight: 40
cascade:
  type: docs
---

HTTP headers that carry agent context across API calls, enabling persistent conversations without server infrastructure.

## What It Is

OCP uses standard HTTP headers to share context between API calls:

```http
GET /repos/owner/project/issues HTTP/1.1
Host: api.github.com
Authorization: Bearer token
OCP-Context-ID: ocp-abc123
OCP-Agent-Type: vscode-extension
OCP-User: alice
OCP-Workspace: my-project
```

**Required Headers:**
- `OCP-Context-ID`: Unique session identifier
- `OCP-Agent-Type`: Type of AI agent

**Optional Headers:**
- `OCP-User`: Current user
- `OCP-Workspace`: Current project/workspace
- `OCP-Current-Goal`: Agent's current objective

## How It Works

**Automatic**: OCP agents add headers to all API calls automatically.

**Persistent**: Same context ID flows through entire conversation.

**Compatible**: Works with any existing HTTP API immediately.

**Stateful**: Enables multi-step workflows across different APIs.

## Benefits

- **Persistent memory** across API calls
- **Workspace awareness** for better responses  
- **Zero infrastructure** - just HTTP headers
- **Cross-API workflows** with shared state

{{< cards >}}
{{< card link="../tools/" title="Tool Discovery" subtitle="Auto-generate tools from OpenAPI specs" icon="cog" >}}
{{< card link="../getting-started/" title="Get Started" subtitle="Install and start using OCP" icon="play" >}}
{{< /cards >}}