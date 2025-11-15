---
title: Specification
weight: 5
cascade:
  type: docs
---

The technical specification for the Open Context Protocol, defining the standards, formats, and compatibility requirements for OCP implementations.

**For Usage Documentation**: See the [4 Superpowers](#superpowers) sections: [Context](/context/), [Tools](/tools/), [Registry](/registry/), and [IDE Integration](/ide/).

## Protocol Overview

OCP is a **zero-infrastructure protocol** that enables persistent context sharing across HTTP API calls using standard headers, with automatic API discovery from OpenAPI specifications.

### Core Protocol Requirements

**Required Components:**
- HTTP header format for context transmission
- JSON schema for context objects  
- Base64 encoding with optional compression
- OpenAPI-based tool discovery algorithm

**Optional Components:**
- Community registry integration
- IDE extension integration
- Enhanced API responses (Level 2)

## Technical Specifications

{{< cards >}}
{{< card link="protocol/http-protocol/" title="HTTP Protocol" subtitle="Header formats, encoding rules, and transmission standards" >}}
{{< card link="protocol/context-schema/" title="Context Schema" subtitle="JSON schema definitions and validation rules" >}}
{{< card link="protocol/compatibility/" title="Compatibility Levels" subtitle="Level 1 and Level 2 API compatibility requirements" >}}
{{< card link="protocol/openapi-extensions/" title="OpenAPI Extensions" subtitle="OCP-specific OpenAPI extensions for enhanced APIs" >}}
{{< card link="protocol/security/" title="Security Model" subtitle="Privacy, validation, and security considerations" >}}
{{< /cards >}}

## Implementation Requirements

### Client Library Standards
All OCP client libraries must implement:

1. **Context Management**: Create, update, and serialize context objects
2. **HTTP Enhancement**: Automatic header injection with encoding/compression  
3. **Schema Discovery**: Parse OpenAPI specs and generate callable tools
4. **Tool Invocation**: Execute API calls with parameter validation
5. **Error Handling**: Graceful degradation when OCP features unavailable

### Testing Requirements
- **Context Serialization**: 100% test coverage for encoding/decoding
- **Tool Generation**: Deterministic naming and parameter extraction
- **HTTP Integration**: Header injection and response parsing
- **OpenAPI Parsing**: Handle malformed specifications gracefully

### Performance Standards
- **Tool Discovery**: Cache OpenAPI specifications locally
- **Context Compression**: Compress contexts >1KB before encoding
- **Memory Efficiency**: Handle large API specifications without excessive memory
- **Network Optimization**: Minimize redundant specification downloads

## Version Compatibility

### Current Version: OCP 2.0

**Breaking Changes from 1.0:**
- Agent-focused header naming (`OCP-Agent-*` prefix)
- Simplified context schema with required/optional field distinction
- Enhanced OpenAPI tool generation with deterministic naming

**Backward Compatibility:**
- OCP 1.0 headers supported in transition period
- Graceful fallback for unsupported features
- OpenAPI 2.0 specifications supported with limitations

### Future Versioning
- **Semantic Versioning**: Major.Minor.Patch format
- **Specification Stability**: Backward compatibility within major versions  
- **Implementation Guidelines**: Clear migration paths for breaking changes

## Reference Implementations

### Production Libraries
- **Python**: [`ocp-python`](https://github.com/opencontextprotocol/ocp-python) - Reference implementation
- **JavaScript**: [`ocp-javascript`](https://github.com/opencontextprotocol/ocp-javascript) - 1:1 parity with Python
- **CLI**: [`ocp-cli`](https://github.com/opencontextprotocol/ocp-cli) - Command-line tools and validation

### Validation Tools
- **Specification Validator**: Validate OCP compliance
- **Context Schema Validator**: JSON schema validation
- **OpenAPI Compatibility Checker**: Verify tool generation
- **Performance Benchmarks**: Reference performance metrics