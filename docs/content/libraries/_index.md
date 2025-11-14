---
title: Libraries
weight: 2
cascade:
  type: docs
---

Official OCP client libraries for different programming languages.

## Core Requirements

All OCP libraries must provide:

1. **Context Management**: Create, update, and inject OCP context headers
2. **Schema Discovery**: Parse OpenAPI specs and generate callable tools  
3. **Tool Invocation**: Execute API operations with automatic context injection
4. **Parameter Validation**: Validate tool parameters against OpenAPI schemas

## Available Libraries

{{< cards >}}
{{< card link="python/" title="Python" subtitle="Complete implementation with async support" >}}
{{< card link="javascript/" title="JavaScript/TypeScript" subtitle="Node.js and browser support" >}}
{{< /cards >}}

## Library Design Philosophy

**Protocol-Only Specification**: OCP specifies the HTTP protocol layer only. Libraries implement context management and tool generation while following these principles:

### Testing Standards

All libraries must include comprehensive test coverage:

- **Context Management**: 100% coverage for context creation, updates, and serialization
- **Schema Discovery**: Deterministic tool name generation and OpenAPI parsing
- **HTTP Enhancement**: Header encoding/decoding with compression and error handling  
- **Agent Orchestration**: Complete workflow testing from API registration to tool execution

### Performance Requirements

- **Fast Tool Discovery**: Cache OpenAPI specifications locally
- **Efficient Context**: Compress context objects before transmission
- **Memory Management**: Handle large API specifications without excessive memory usage
- **Error Resilience**: Graceful degradation when OCP features are unavailable

## Getting Started

Choose your preferred language and follow the library-specific documentation for installation and usage examples.