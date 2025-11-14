---
title: Specification
weight: 1
cascade:
  type: docs
---

The Open Context Protocol enables AI agents to maintain persistent context across API calls using standard HTTP headers and automatically generate agent tools from OpenAPI specifications.

## Key Features

**Automatic Tool Generation**: Convert any OpenAPI specification into callable agent tools with parameter validation and request building.

**Context Persistence**: Maintain conversation state and workspace context across all API interactions using HTTP headers.

**Zero Infrastructure**: Works with existing APIs without requiring server modifications or additional infrastructure.

## Protocol Core

{{< cards >}}
{{< card link="protocol/headers/" title="HTTP Headers" subtitle="Required and optional headers for context transmission" >}}
{{< card link="protocol/context-schema/" title="Context Schema" subtitle="JSON structure for agent context objects" >}}
{{< card link="protocol/encoding/" title="Encoding Rules" subtitle="Base64 encoding, compression, and size limits" >}}
{{< card link="protocol/compatibility/" title="Compatibility" subtitle="Level 1 and Level 2 API compatibility modes" >}}
{{< /cards >}}

## Implementation Guides

{{< cards >}}
{{< card link="guides/quick-start/" title="Quick Start" subtitle="Get started with OCP in minutes" >}}
{{< card link="guides/openapi-tools/" title="OpenAPI Tools" subtitle="Automatic tool generation from specifications" >}}
{{< card link="guides/examples/" title="Examples" subtitle="Common implementation patterns" >}}
{{< /cards >}}