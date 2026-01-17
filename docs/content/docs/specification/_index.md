---
title: Open Context Protocol v1.0
linkTitle: Specification
next: /docs/specs/context-schema/
prev: /docs/agent-context
weight: 6
cascade:
  type: docs
---

Specification for automatic API tool discovery and persistent context sharing across HTTP APIs.

## Protocol Overview

Open Context Protocol (OCP) defines a standard for automatic API tool discovery and persistent context sharing across HTTP APIs. The protocol consists of two core specifications:

**1. Tool Discovery**
- Parse OpenAPI 3.0+ specifications into callable tools
- Deterministic naming and parameter mapping
- Standardized tool schema definition

**2. Context Transmission**
- HTTP headers for conversation state transmission
- Session persistence and recovery
- Cross-API workflow coordination

**Compatibility Levels:**
- **Level 1**: APIs accept context headers without modification
- **Level 2**: APIs read context and provide enhanced responses

---

## HTTP Headers Specification

OCP transmits context information using standard HTTP headers with defined formats and validation rules.

#### Required Headers

**`OCP-Context-ID`**
- **Purpose**: Unique identifier for the agent session
- **Format**: 1-64 characters, pattern `^[a-zA-Z0-9\-]{1,64}$`
- **Example**: `ocp-a1b2c3d4`

**`OCP-Agent-Type`**
- **Purpose**: Type of agent making the request
- **Format**: 1-128 characters, pattern `^[a-zA-Z0-9_\-\.]{1,128}$`
- **Example**: `ide_coding_assistant`

#### Optional Headers

**`OCP-Current-Goal`**
- **Purpose**: Current agent objective
- **Format**: 1-256 characters
- **Example**: `debug_payment_error`

**`OCP-Session`**
- **Purpose**: Base64-encoded context object (see Context Schema)
- **Format**: Base64-encoded, optionally gzip-compressed JSON
- **Size Limit**: 8KB after encoding

**`OCP-User`**
- **Purpose**: User identifier
- **Format**: 1-64 characters
- **Example**: `alice`

**`OCP-Workspace`**
- **Purpose**: Current workspace or project
- **Format**: 1-128 characters
- **Example**: `payment-service`

**`OCP-Version`**
- **Purpose**: OCP specification version
- **Format**: Semantic version string
- **Value**: `1.0`

#### Complete Example
```http
GET /api/resource HTTP/1.1
OCP-Context-ID: ocp-a1b2c3d4
OCP-Agent-Type: ide_coding_assistant
OCP-Current-Goal: debug_payment_error
OCP-User: alice
OCP-Workspace: payment-service
OCP-Session: eyJjb250ZXh0X2lkIjoib2NwLWExYjJjM2Q0In0=
OCP-Version: 1.0
```

### Context Schema

{{< callout type="info" >}}
The `OCP-Session` header contains a JSON object that MUST conform to the [Context Schema](context-schema). See the schema for detailed field definitions, validation rules, and examples.
{{< /callout >}}

### Encoding Requirements

1. **JSON Serialization**: Context must be valid UTF-8 JSON
2. **Compression**: Optional gzip compression before Base64 encoding for contexts >1KB
3. **Base64 Encoding**: Standard Base64 encoding per RFC 4648
4. **Size Limits**: Maximum 8KB for `OCP-Session` header after encoding

### Error Handling

- **Invalid Headers**: APIs MUST ignore invalid OCP headers and process requests normally
- **Oversized Context**: Headers exceeding limits MUST be ignored
- **Missing Context**: APIs MUST function normally without OCP headers
- **Malformed JSON**: Invalid JSON in `OCP-Session` MUST be ignored

---

## OpenAPI Tool Discovery

OCP defines how OpenAPI 3.0+ specifications are parsed into callable tools with deterministic naming and parameter mapping.

### Tool Generation Rules

{{< callout type="info" >}}
Each discovered tool MUST conform to the [Tool Schema](tool-schema). See the schema for complete parameter definitions, validation rules, and examples.
{{< /callout >}}

#### Deterministic Naming

Tool names are generated using a deterministic algorithm with camelCase normalization:

1. **Use operationId with camelCase normalization**: If present in OpenAPI specification
2. **Generate from HTTP method + path with camelCase normalization**: If operationId is missing
   - Convert path to camelCase
   - Prefix with lowercase HTTP method
   - Replace path parameters with descriptive names
   - Normalize special characters (/, _, -) to camelCase

**Examples:**
```
operationId: "listRepositories" → Tool name: "listRepositories"
operationId: "meta/root" → Tool name: "metaRoot"
operationId: "admin_apps_approve" → Tool name: "adminAppsApprove"
operationId: "FetchAccount" → Tool name: "fetchAccount"
GET /repos/{owner}/{repo}/issues → Tool name: "getReposOwnerRepoIssues"  
POST /users → Tool name: "postUsers"
```

#### Parameter Mapping

For each OpenAPI operation, parameter extraction follows this specification:

1. **Path Parameters**: Extract from URL template (e.g., `{owner}`, `{repo}`)
2. **Query Parameters**: Extract from `parameters` array with `in: "query"`
3. **Request Body**: Extract schema for POST/PUT/PATCH operations
4. **Headers**: Extract from `parameters` array with `in: "header"`

All parameters maintain their OpenAPI type definitions and validation constraints.

#### Validation Requirements

Tool discovery MUST:
- Support OpenAPI 3.0 and 3.1 specifications
- Handle missing operationId gracefully
- Preserve all parameter validation rules from OpenAPI schema
- Generate consistent tool names across implementations

---

## Compatibility Levels

{{< callout type="info" >}}
APIs can declare OCP support using extensions defined in the [OpenAPI Extensions Schema](openapi-extensions-schema).
{{< /callout >}}

### Level 1: Context-Aware

APIs receive OCP headers but do not modify their behavior. Context management is entirely client-side.

**Requirements:**
- Accept OCP headers without errors
- Process requests normally regardless of OCP header presence
- Optionally log context for debugging (respecting privacy)

### Level 2: Context-Enhanced

APIs read OCP context and provide enhanced, context-aware responses.

**Requirements:**
- Parse and validate OCP context
- Modify responses based on context (when appropriate)
- Include context-aware information in responses
- Support OCP OpenAPI extensions for behavior specification

---

## Implementation Requirements

### Client Library Requirements

OCP-compliant client libraries MUST implement:

**Context Management:**
- Create and serialize AgentContext objects per [Context Schema](context-schema)
- Generate OCP headers from context following encoding requirements
- Parse context from HTTP response headers
- Validate context against JSON schema

**Tool Discovery:**
- Parse OpenAPI 3.0+ specifications
- Generate tools using deterministic naming rules
- Validate parameters against OpenAPI schemas
- Cache specifications for performance optimization

**HTTP Integration:**
- Inject OCP headers into all API requests automatically
- Build requests from tool calls and parameters
- Parse API responses and extract context updates
- Handle requests gracefully when OCP headers are rejected

### Performance Standards

- **Caching**: SHOULD cache OpenAPI specifications locally
- **Compression**: MUST compress contexts >1KB before Base64 encoding
- **Memory**: MUST handle large OpenAPI specifications
- **Network**: SHOULD minimize redundant specification downloads

### Error Handling Standards

Implementations MUST:
- Process requests normally when OCP headers are invalid or rejected
- Provide clear error messages for malformed OpenAPI specifications
- Validate context without failing API requests
- Support graceful degradation when context features are unavailable

