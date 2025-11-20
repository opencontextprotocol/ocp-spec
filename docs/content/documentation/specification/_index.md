---
title: Open Context Protocol v1.0
linkTitle: Specification
weight: 7
cascade:
  type: docs
---

The Open Context Protocol (OCP) is a specification for maintaining persistent context across HTTP API calls using standard HTTP headers and automatically discovering tools from OpenAPI specifications.

## Protocol Definition

### HTTP Headers

OCP uses standard HTTP headers to transmit context information between agents and APIs.

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

The `OCP-Session` header contains a JSON object that MUST conform to the [Context Schema](context-schema). See the schema for detailed field definitions, validation rules, and examples.

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

## Schema Discovery

### Tool Generation from OpenAPI

OCP implementations MUST be able to parse OpenAPI 3.0+ specifications and generate callable tools.

#### Tool Schema Definition

Each discovered tool MUST conform to the [Tool Schema](tool-schema). See the schema for complete parameter definitions, validation rules, and examples.

#### Deterministic Naming

Tool names MUST be generated deterministically:

1. **Use operationId**: If present in OpenAPI specification
2. **Generate from HTTP method + path**: If operationId is missing
   - Convert path to snake_case
   - Prefix with lowercase HTTP method
   - Replace path parameters with descriptive names

**Examples:**
```
operationId: "listRepositories" → Tool name: "listRepositories"
GET /repos/{owner}/{repo}/issues → Tool name: "get_repos_owner_repo_issues"  
POST /users → Tool name: "post_users"
```

#### Parameter Processing

For each OpenAPI operation, implementations MUST:

1. Extract path parameters from the URL template
2. Extract query parameters from the `parameters` array
3. Extract request body schema for POST/PUT/PATCH operations
4. Validate parameter types against OpenAPI schema
5. Map parameters to the appropriate HTTP location

#### Specification Validation

Implementations MUST:
- Validate OpenAPI specification structure
- Support OpenAPI 3.0 and 3.1
- Handle missing or malformed specifications gracefully
- Provide clear error messages for invalid specifications

---

## Implementation Requirements

### Client Libraries

All OCP client libraries MUST provide:

1. **Context Management**
   - Create, update, and serialize AgentContext objects
   - Generate OCP headers from context
   - Parse context from HTTP response headers
   - Validate context against JSON schema

2. **Schema Discovery**
   - Fetch and parse OpenAPI specifications
   - Generate tools according to deterministic naming rules
   - Validate tool parameters against OpenAPI schemas
   - Cache specifications for performance

3. **Tool Execution**
   - Build HTTP requests from tool calls and parameters
   - Inject OCP headers into all requests
   - Parse and validate API responses
   - Update context based on tool execution results

4. **Error Handling**
   - Gracefully handle malformed OpenAPI specifications
   - Validate context without failing requests
   - Provide meaningful error messages
   - Support operation without OCP headers (degraded mode)

### Performance Requirements

- **Tool Discovery**: SHOULD cache OpenAPI specifications locally
- **Context Compression**: MUST compress contexts >1KB before encoding  
- **Memory Efficiency**: MUST handle large OpenAPI specifications
- **Network Optimization**: SHOULD minimize redundant specification downloads

### Validation Requirements

Implementations MUST validate:
- OCP header format and constraints
- Context object against JSON schema
- OpenAPI specification structure
- Tool parameter types and requirements

