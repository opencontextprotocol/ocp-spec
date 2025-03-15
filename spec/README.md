# Lean Context Protocol Specification `draft`

> 🚧 **Work in Progress**  
> This specification is in early development and subject to change. Feedback and contributions are welcome!  

  * [1. Overview](#1-overview)
    * [What is LCP?](#what-is-lcp)
    * [Why LCP?](#why-lcp)
  * [2. Core Concepts](#2-core-concepts)
    * [2.1 Context Objects](#21-context-objects)
    * [2.2 Stateless vs. Stateful Context](#22-stateless-vs-stateful-context)
  * [3. Transport Mechanisms](#3-transport-mechanisms)
    * [3.1 HTTP Headers (Default)](#31-http-headers-default)
    * [3.2 Inline JSON (For Direct Model Calls)](#32-inline-json-for-direct-model-calls)
    * [3.3 WebSockets / gRPC (For Streaming Context)](#33-websockets--grpc-for-streaming-context)
  * [4. Context Storage (Optional)](#4-context-storage-optional)
    * [4.1 External Storage API](#41-external-storage-api)
    * [4.2 Fetching Stored Context](#42-fetching-stored-context)
  * [5. Function Calls (Alternative to MCP Tools)](#5-function-calls-alternative-to-mcp-tools)
    * [5.1 Calling a Function with Context](#51-calling-a-function-with-context)
    * [5.2 Response Example](#52-response-example)
  * [6. LCP vs. MCP](#6-lcp-vs-mcp)
  * [7. Roadmap](#7-roadmap)

## 1. Overview

### What is LCP?

Lean Context Protocol (LCP) is a lightweight, zero-infrastructure protocol for managing and exchanging AI model context across applications. Unlike MCP (Model Context Protocol), LCP is designed to be stateless by default, supports multiple transport mechanisms, and eliminates the need for dedicated servers per integration.

### Why LCP?

MCP introduces unnecessary complexity by enforcing a rigid client-server model, requiring dedicated infrastructure to manage context. LCP takes a different approach by:

- Embedding context in API calls instead of requiring a persistent server.
- Supporting multiple transport methods (HTTP headers, WebSockets, gRPC, etc.).
- Allowing optional external storage for long-lived sessions when needed.
- Simplifying function calls instead of treating tools, prompts, and sampling as separate entities.

## 2. Core Concepts

LCP is built on a few simple concepts:

### 2.1 Context Objects

The Context Object is a self-contained data structure that enables applications to track conversation history, user preferences, and relevant state across interactions.

```json
{
  "context_id": "123e4567-e89b-12d3-a456-426614174000",
  "session": {
    "user_id": "user-123",
    "history": [
      {"role": "user", "message": "Summarize this document."},
      {"role": "assistant", "message": "Here's a summary..."}
    ]
  },
  "expires": "2025-03-15T12:00:00Z",
  "signature": "base64-encoded-signature"
}
```

### 2.2 Stateless vs. Stateful Context

- Stateless (Default) → The entire context is passed in every request.
- Stateful (Optional) → Context can be stored externally and referenced via a `context_id`.

## 3. Transport Mechanisms

LCP does not enforce a single transport method. Instead, it supports multiple options:

### 3.1 HTTP Headers (Default)

Most API-based implementations can pass context in request headers:

```shell
POST /generate
Authorization: Bearer YOUR-API-KEY
LCP-Context: eyJjb250ZXh0X2lkIjoiMTIz... (Base64-encoded JSON)
Content-Type: application/json
```

- Pros: Works with existing AI APIs (OpenAI, Claude, etc.).
- Cons: Limited by header size (~8 KB for most servers).

### 3.2 Inline JSON (For Direct Model Calls)

For LLMs that accept structured JSON, context can be embedded in requests:

```json
{
  "model": "gpt-4",
  "context": {
    "context_id": "abc123",
    "history": [
      {"role": "user", "message": "How do I install LCP?"},
      {"role": "assistant", "message": "LCP is a lightweight protocol..."}
    ]
  },
  "prompt": "Tell me more about LCP."
}
```

- Pros: Works with local LLMs, API-based models.
- Cons: Larger payload size.

### 3.3 WebSockets / gRPC (For Streaming Context)

LCP can also be passed as metadata in WebSockets or gRPC calls.

```json
{
  "event": "message",
  "context": { "context_id": "abc123", "history": [...] },
  "message": "Tell me more about LCP."
}
```

- Pros: Ideal for chatbot applications with real-time interactions.
- Cons: Requires long-lived connections.

## 4. Context Storage (Optional)

LCP is stateless by default, but for long-lived interactions, context can be stored externally.

### 4.1 External Storage API

Servers can offer a context storage API:

```http
POST /context/store
Authorization: Bearer YOUR-API-KEY
Content-Type: application/json

{
  "context_id": "123e4567",
  "session": {
    "user_id": "user-123",
    "history": [...]
  },
  "expires": "2025-03-15T12:00:00Z"
}
```

### 4.2 Fetching Stored Context

Clients can retrieve context when needed:

```http
GET /context/123e4567
Authorization: Bearer YOUR-API-KEY

{
  "context_id": "123e4567",
  "session": { "history": [...] }
}
```

- Pros: Works well for long-running AI agents.
- Cons: Requires external storage (S3, Redis, Firestore, etc.).


## 5. Function Calls (Alternative to MCP Tools)

MCP treats tools and function calls as separate entities, but LCP merges them into one standard mechanism.

### 5.1 Calling a Function with Context

```json
{
  "context": { "context_id": "abc123", "history": [...] },
  "tool": "weather.get_forecast",
  "parameters": { "city": "New York" }
}
```

### 5.2 Response Example

```json
{
  "context_id": "abc123",
  "result": {
    "temperature": "72°F",
    "conditions": "Sunny"
  }
}
```

- Pros: More flexible than MCP’s rigid tool registry.
- Cons: Requires API-level integration.

## 6. LCP vs. MCP

| Feature | MCP (Model Context Protocol) | LCP (Lean Context Protocol) |
|---------|------------------------------|-----------------------------|
| Requires a dedicated server? | `✅ Yes` | `❌ No` |
| Supports stateless context passing? | `❌ No` | `✅ Yes` |
| Uses standard API headers? | `❌ No` | `✅ Yes` |
| Storage requirement? | `✅ Required` | `❌ Optional` |
| Supports OpenAI, Claude, Mistral? | `❌ No` | `✅ Yes` |
| Complex transport system? | `✅ Yes` | `❌ No` |

## 7. Roadmap

🚀 MVP Release (Q2 2025)

- Publish draft spec for LCP
- Release Go & TypeScript SDKs
- Launch GitHub Discussions for feedback

🔄 Iteration (Q3 2025)

- Expand transport support (gRPC, WebSockets)
- Build example integrations with OpenAI, Claude, Mistral
- Release LCP storage APIs

⚡ Future Plans

- Define security best practices for context validation
- Formalize LCP governance & versioning