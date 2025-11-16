---
title: Specification
weight: 6
cascade:
  type: docs
---

# Open Context Protocol v1.0

The Open Context Protocol (OCP) enables AI agents to maintain persistent context across HTTP API calls and automatically discover tools from OpenAPI specifications using standard HTTP headers.

## Overview

OCP solves two fundamental problems:
1. **Context Loss**: Agents lose conversation state between API calls
2. **Manual Integration**: Each API requires custom integration code

OCP provides:
- **Context Persistence**: Standard HTTP headers carry conversation state
- **Tool Discovery**: Automatic tool generation from OpenAPI specifications
- **Zero Infrastructure**: No servers or custom protocols required

---

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

The `OCP-Session` header contains a JSON object that MUST conform to the [OCP Context Schema](https://github.com/opencontextprotocol/specification/blob/main/schemas/ocp-context.json).

**Schema Location**: `/schemas/ocp-context.json`

#### Required Fields
- `context_id`: Unique session identifier (matches `OCP-Context-ID` header)
- `agent_type`: Type of agent (matches `OCP-Agent-Type` header)
- `created_at`: ISO 8601 timestamp of context creation
- `last_updated`: ISO 8601 timestamp of last update

#### Optional Fields
- `user`: User identifier
- `workspace`: Current workspace or project
- `current_goal`: Current agent objective
- `current_file`: Currently active file
- `context_summary`: Brief summary of conversation context
- `error_context`: Error information for debugging
- `recent_changes`: Array of recent modifications (max 10)
- `session`: Session metadata object with start_time, interaction_count, agent_type
- `history`: Array of interaction history with timestamp, action, api_endpoint, result, metadata
- `api_specs`: Object mapping API names to their OpenAPI specification URLs

#### Minimal Valid Context
```json
{
  "context_id": "ocp-a1b2c3d4",
  "agent_type": "cli_tool",
  "created_at": "2025-11-16T10:30:00Z",
  "last_updated": "2025-11-16T10:30:00Z"
}
```

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

### Level 1: Context-Aware (Available Today)

APIs receive OCP headers but do not modify their behavior. Context management is entirely client-side.

**Requirements:**
- Accept OCP headers without errors
- Process requests normally regardless of OCP header presence
- Optionally log context for debugging (respecting privacy)

**Works with:** Any existing HTTP API

### Level 2: Context-Enhanced (Future)

APIs read OCP context and provide enhanced, context-aware responses.

**Requirements:**
- Parse and validate OCP context
- Modify responses based on context (when appropriate)
- Include context-aware information in responses
- Support OCP OpenAPI extensions for behavior specification

**OpenAPI Extensions**: APIs can declare OCP support using extensions defined in the [OCP OpenAPI Extensions Schema](https://github.com/opencontextprotocol/specification/blob/main/schemas/ocp-openapi-extensions.json):

- `x-ocp-enabled`: API acknowledges OCP headers
- `x-ocp-context-aware`: API uses context data in responses
- `x-ocp-context`: Operation-level context behavior
- `x-ocp-enhanced-response`: Additional response properties with context

**Implementation:** Requires API-side OCP support

---

## Schema Discovery

### Tool Generation from OpenAPI

OCP implementations MUST be able to parse OpenAPI 3.0+ specifications and generate callable tools.

#### Tool Schema Definition

Each discovered tool MUST conform to the [OCP Tool Schema](https://github.com/opencontextprotocol/specification/blob/main/schemas/ocp-tool.json).

**Schema Location**: `/schemas/ocp-tool.json`

**Key Requirements**:
- `name`: Deterministic tool name (alphanumeric + underscore, starts with letter)
- `description`: Human-readable description from OpenAPI
- `method`: HTTP method (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)
- `path`: API endpoint path template with `{parameter}` placeholders
- `parameters`: Object mapping parameter names to their definitions
- `response_schema`: OpenAPI response schema for successful responses
- `tags`: OpenAPI tags for organization (optional)

**Parameter Definition Requirements**:
- `type`: Data type (string, number, integer, boolean, array, object)
- `required`: Boolean indicating if parameter is required
- `location`: Where parameter goes (path, query, header, body)
- `schema`: Full OpenAPI schema definition
- Additional validation properties (format, enum, min/max, etc.)

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
- **Memory Efficiency**: MUST handle large OpenAPI specifications without excessive memory usage
- **Network Optimization**: SHOULD minimize redundant specification downloads

### Validation Requirements

Implementations MUST validate:
- OCP header format and constraints
- Context object against JSON schema
- OpenAPI specification structure
- Tool parameter types and requirements

---

## Examples

### Minimal Context
```json
{
  "context_id": "ocp-a1b2c3d4",
  "agent_type": "cli_tool",
  "created_at": "2025-11-16T10:30:00Z",
  "last_updated": "2025-11-16T10:30:00Z"
}
```

### Complete Context
```json
{
  "context_id": "ocp-debug-123",
  "agent_type": "ide_coding_assistant",
  "user": "alice",
  "workspace": "payment-service", 
  "current_goal": "debug_payment_validation",
  "current_file": "payment_validator.py",
  "session": {
    "start_time": "2025-11-16T10:20:00Z",
    "interaction_count": 5,
    "agent_type": "ide_coding_assistant"
  },
  "history": [
    {
      "timestamp": "2025-11-16T10:25:00Z",
      "action": "api_call",
      "api_endpoint": "https://api.github.com/repos/alice/payment-service/issues",
      "result": "success",
      "metadata": {
        "operation": "list_issues",
        "tool_name": "github.list_issues"
      }
    }
  ],
  "context_summary": "Debugging payment validation error in Django app",
  "recent_changes": [
    "Modified payment_validator.py line 42",
    "Added test case for edge condition"
  ],
  "api_specs": {
    "github": "https://api.github.com/openapi.json",
    "stripe": "https://stripe.com/openapi.json"
  },
  "created_at": "2025-11-16T10:20:00Z",
  "last_updated": "2025-11-16T10:30:00Z"
}
```

### Tool Example
```json
{
  "name": "create_issue",
  "description": "Create a new issue in a repository", 
  "method": "POST",
  "path": "/repos/{owner}/{repo}/issues",
  "operation_id": "issues/create",
  "parameters": {
    "owner": {
      "type": "string",
      "required": true,
      "location": "path",
      "description": "Repository owner"
    },
    "repo": {
      "type": "string", 
      "required": true,
      "location": "path",
      "description": "Repository name"
    },
    "title": {
      "type": "string",
      "required": true, 
      "location": "body",
      "description": "Issue title"
    },
    "body": {
      "type": "string",
      "required": false,
      "location": "body", 
      "description": "Issue description"
    }
  },
  "response_schema": {
    "type": "object",
    "properties": {
      "id": {"type": "integer"},
      "title": {"type": "string"},
      "state": {"type": "string"}
    }
  },
  "tags": ["issues"]
}
```