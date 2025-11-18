---
title: OpenAPI Extensions Schema
weight: 9
cascade:
  type: docs
---

Schema for OCP extensions in OpenAPI specifications.

**JSON Schema**: [`/schemas/ocp-openapi-extensions.json`](https://github.com/opencontextprotocol/specification/blob/main/schemas/ocp-openapi-extensions.json)

## Definitions

### `ocpInfoExtensions`

OCP extensions for OpenAPI info section

#### Properties

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `x-ocp-agent-types` | array | No | Agent types this API is optimized for |
| `x-ocp-context-aware` | boolean | No | Indicates this API can read and utilize context data in responses |
| `x-ocp-enabled` | boolean | No | Indicates this API acknowledges OCP context headers |
| `x-ocp-version` | [string](#x-ocp-version) | No | OCP specification version this API supports |


### `ocpInfoExtensions.x-ocp-version`

**Type:** string

OCP specification version this API supports

**Pattern:** `^[0-9]+\.[0-9]+$`


### `ocpOperationExtensions`

OCP extensions for OpenAPI operation objects

#### Properties

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `x-ocp-context` | [object](#x-ocp-context) | No | OCP context behavior for this operation |
| `x-ocp-enhanced-response` | [object](#x-ocp-enhanced-response) | No | Additional response properties when OCP context is present |


### `ocpOperationExtensions.x-ocp-context`

**Type:** object

OCP context behavior for this operation

#### Properties

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `enhances_with` | array | No | Context fields this operation uses to enhance responses |
| `requires_context` | boolean | No | Whether this operation requires OCP context to function properly |
| `updates_context` | array | No | Context fields this operation may update |


### `ocpOperationExtensions.x-ocp-enhanced-response`

**Type:** object

Additional response properties when OCP context is present


### `ocpOperationExtensions.x-ocp-enhanced-response.parameters_pattern`

**Type:** object (dynamic properties)

**Pattern:** Properties matching `^[a-zA-Z][a-zA-Z0-9_]*$`

OpenAPI schema for additional response property

Each property matching this pattern must be:

- **Type:** object
- **Description:** OpenAPI schema for additional response property

### `ocpResponseExtensions`

OCP extensions for OpenAPI response objects

#### Properties

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `x-ocp-context-updated` | boolean | No | Indicates this response may include updated context in headers |


