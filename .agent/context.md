# Open Context Protocol - Agent Context

This document captures critical project decisions, patterns, and expectations for AI agents working on this codebase.

## Project Overview

The Open Context Protocol (OCP) specification repository contains:
- Protocol specification and documentation
- Python agent library (`ocp-python/`)
- JavaScript/TypeScript agent library (`ocp-javascript/`)
- CLI tool (`cli/`)
- Registry service (`registry/`)
- Hugo-based documentation site (`site/`)

## Development Philosophy

### MVP Approach
- **Always start minimal**: Implement only what's explicitly requested
- **Incremental development**: Small, deliberate steps
- **Avoid feature creep**: Don't add unrequested functionality
- **User corrections are paramount**: When user says "too much", strip back immediately
- **NO DEPRECATIONS**: This is pre-release software. Break things. No backwards compatibility until published.
- **NO TRANSITIONAL CODE**: Remove old code completely. Don't leave breadcrumbs.

### Decision Making
- **VERIFY ALL IMPLEMENTATION PLANS**: Before implementing any significant feature or architectural decision, verify the approach with the user first
- **No assumptions about scope**: If the purpose or scope of a feature is unclear, ASK before implementing
- **Surgical fixes only**: When fixing issues, make targeted changes without expanding scope
- Follow established patterns within the project
- Maintain consistency across similar components
- Ask for clarification rather than assume requirements

## Python Project Structure Standards

### Package Organization
Both Python projects follow this established pattern:

```
project-root/
├── pyproject.toml          # Poetry configuration
├── README.md              # Project documentation
├── .python-version        # pyenv version (3.12.11)
├── poetry.lock           # Locked dependencies
└── src/
    └── package_name/     # Source package
        ├── __init__.py
        └── *.py
```

### Naming Conventions
- **Package names**: Use hyphens (e.g., `open-context-agent`, `ocp-cli`, `ocp-registry`)
- **Module names**: Use underscores matching package intent (e.g., `ocp_agent`, `ocp_cli`, `ocp_registry`)
- **PyPI package name**: `open-context-agent` (avoids conflicts with existing `ocp-*` packages on PyPI)
- **Import convention**: `from ocp_agent import OCPAgent` (short and convenient for developers)
- **Rationale**: PyPI name is unique and searchable, module name is concise for daily use

### Current Structure
- `ocp-python/src/ocp_agent/` - Core agent library (PyPI: `open-context-agent`)
- `ocp-javascript/src/` - JavaScript/TypeScript library (npm: `@opencontext/agent`)
- `cli/src/ocp_cli/` - Command-line interface
- `registry/src/ocp_registry/` - Community API registry service (FastAPI)

### Dependency Management
- **Tool**: Poetry for all Python projects
- **Python version**: 3.12.11 (specified in `.python-version`)
- **Approach**: Minimal dependencies, avoid dev/test dependencies unless specifically requested
- **Local dependencies**: Use path dependencies between related projects

## JavaScript/TypeScript Project Structure

### Package Organization
The JavaScript library follows standard npm/TypeScript patterns:

```
ocp-javascript/
├── package.json          # npm configuration
├── tsconfig.json        # TypeScript configuration
├── jest.config.js       # Jest test configuration
├── README.md           # Project documentation
├── LICENSE            # MIT license
├── .gitignore         # Git ignore patterns
├── src/               # TypeScript source
│   ├── index.ts      # Main entry point
│   ├── agent.ts      # OCPAgent implementation
│   ├── context.ts    # AgentContext implementation
│   ├── headers.ts    # Header encoding/decoding
│   ├── http_client.ts # OCPHTTPClient wrapper
│   ├── registry.ts   # Registry client
│   ├── schema_discovery.ts # OpenAPI schema parsing
│   ├── validation.ts # JSON schema validation
│   └── errors.ts     # Error hierarchy
├── tests/            # Jest tests (145 tests)
│   └── *.test.ts
└── dist/            # Compiled output (gitignored)
    ├── *.js        # Compiled JavaScript
    ├── *.d.ts      # TypeScript definitions
    └── *.js.map    # Source maps
```

### JavaScript Library Standards
- **Package name**: `@opencontext/agent` (scoped npm package)
- **Type**: ESM module (`"type": "module"`)
- **Build**: TypeScript → dist/ with declarations and source maps
- **Testing**: Jest with `@jest/globals` and ts-jest
- **TypeScript**: Strict mode enabled, proper type definitions
- **Dependencies**: Minimal (ajv for validation)
- **Node.js**: >=18.0.0 required

### Build & Test Commands
- `npm run build` - Compile TypeScript to dist/
- `npm test` - Run Jest tests
- `npm run type-check` - TypeScript type checking
- `npm run prepublishOnly` - Build + test before publishing

### Library Parity
- **Complete 1:1 feature parity** with Python library
- All 174 tests ported and passing (added storage tests)
- Same API surface: OCPAgent, AgentContext, OCPHTTPClient, OCPStorage, etc.
- Identical behavior and validation rules
- No @ts-nocheck - fully type-safe with proper Jest mock typing

### Storage & Cross-Language Compatibility
- **OCPStorage class**: Local API caching and session persistence
- **Cross-language storage schema**: snake_case JSON format for compatibility
- **Shared cache directory**: `~/.ocp/cache/apis/` and `~/.ocp/sessions/`
- **File interoperability**: Python CLI and JavaScript VS Code extension can share cached APIs and sessions
- **Storage architecture**: Per-file JSON storage, fail-safe error handling
- **Usage**: Optional caching (7-day API cache expiration), session persistence across restarts

### Dependency Management
- **Tool**: Poetry for all Python projects
- **Python version**: 3.12.11 (specified in `.python-version`)
- **Approach**: Minimal dependencies, avoid dev/test dependencies unless specifically requested
- **Local dependencies**: Use path dependencies between related projects

### Testing
- **Framework**: pytest 7.0 (matches ocp-agent library)
- **Approach**: Minimal test coverage for core functionality
- **Location**: `tests/` directory in each project
- **Run**: `poetry run pytest tests/ -v`
- **Philosophy**: Test critical paths, not exhaustive coverage

## Key Technical Decisions

### HTTP Client Design (October 26, 2025)
**Decision**: OCP libraries use their own chosen HTTP client, not wrap arbitrary clients.

**Rationale**:
- OCP's scope: Add context headers to HTTP requests
- Not a universal HTTP client wrapper
- Python uses `requests.Session()` internally
- JavaScript uses native `fetch` internally
- Users who need custom clients can use `create_ocp_headers()` directly

**Implementation**:
- `OCPHTTPClient(context)` - No http_client parameter
- `enhance_http_client(client, context)` - Deprecated, ignores client parameter
- `wrap_api(base_url, context, auth, headers)` - No http_client parameter

### Package Naming Resolution
**Problem**: Originally had naming conflict between `ocp-agent` package and `src/ocp/` module.

**Solution**: Renamed `src/ocp/` to `src/ocp_agent/` for consistency.

**Impact**: 
- Eliminates import conflicts
- Makes package/module relationship clear
- Allows CLI to potentially use `src/ocp/` if needed
- Updated CLI imports from `from ocp` to `from ocp_agent`

### CLI Architecture
- **Console script**: `ocp` command via Poetry entry point
- **Structure**: Modular command architecture
- **Features**: Context management, API testing, registry operations
- **Integration**: Uses `ocp_agent` library as dependency

### Schema Files
- **Location**: `schemas/` directory in repository root
- **Files**: `ocp-context.json`, `ocp-openapi-extensions.json`
- **Source of Truth**: Python library (`ocp-python/src/ocp_agent/validation.py`)
- **Sync Policy**: Schema files are synced FROM Python library (not vice versa)
- **Purpose**: Reference documentation, future URL publishing, third-party validation
- **Implementation**: Python library embeds schema (no runtime file loading)
- **Rationale**: Embedded schema = fast, simple, no file dependencies; schema files = documentation artifacts

### Registry Integration
- **Implementation**: OCPRegistry client in CLI
- **Functionality**: List, search, and interact with API registry
- **Architecture**: Separate client class for registry operations

## File Patterns

### Python Version Management
- All projects include `.python-version` with `3.12.11`
- Ensures consistent Python environment across pyenv users

### Poetry Configuration
- Minimal `pyproject.toml` files
- Essential metadata only
- Clear dependency specifications
- Local path dependencies for inter-project relationships

## Working Patterns

### When Starting New Work
1. Review this context document
2. Understand the MVP principle
3. Check existing patterns before implementing
4. Follow established project structure

### When User Requests Changes
1. Implement exactly what's requested
2. Don't add unrequested features
3. If user says "too much", immediately strip back
4. Ask for clarification on ambiguous requirements

### When Adding Dependencies
1. Keep minimal - only add what's needed
2. Avoid dev dependencies unless specifically requested
3. Use Poetry for all Python dependency management
4. Document rationale for new dependencies

## Common Anti-Patterns to Avoid

1. **Over-engineering**: Adding tests, linting, dev tools without request
2. **Feature creep**: Implementing related but unrequested functionality
3. **Inconsistent structure**: Deviating from established patterns
4. **Assumption-driven development**: Implementing based on assumptions rather than explicit requests

## Project-Specific Knowledge

### Registry System
- **Purpose**: Community convenience service hosted by OCP team (not end-user infrastructure)
- **Architecture**: FastAPI service with SQLite database
- **Location**: `registry/src/ocp_registry/`
- **Features**: API registration, search/discovery, OpenAPI validation, tool extraction
- **Zero Infrastructure Principle**: Optional service - OCP works fine without it, enterprises can host their own
- **Integration**: CLI uses OCPRegistry client for discovery
- **Database**: SQLite for development, production uses hosted service

### CLI Commands
- `ocp context` - Context management
- `ocp call` - API calls with OCP enhancement
- `ocp validate` - File validation
- `ocp test` - API testing
- `ocp registry` - Registry operations

### Documentation Site
- Hugo-based static site generator
- Located in `site/` directory
- Generates specification documentation

## VS Code Extension Development

## Current Status

**Extension Rebuilt Successfully** ✅
- Extension now properly wraps OCPAgent instead of reimplementing functionality
- Single OCPAgent instance created per workspace (persists across tool calls)
- All 5 OCP tools implemented: getContext, registerApi, listTools, callTool, searchTools
- VS Code configuration schema added for user, registryUrl, and apiAuth
- TypeScript compilation successful with OCPContextDict type enforcement
- Ready for testing in Extension Development Host

**Next Steps:**
1. Test extension in Extension Development Host
2. Verify autonomous tool calling works with new OCPAgent-based implementation
3. Test full workflow: register API → list tools → call tool
4. Validate OCP headers are included in API calls
5. Test authentication with apiAuth configuration
### Extension Architecture (Correct Approach)

The extension should be a **thin wrapper around OCPAgent**:

1. **Create ONE OCPAgent instance** for the workspace (persists across tools)
2. **Expose OCPAgent methods** as Language Model Tools:
   - `ocp_getContext` - Returns agent.context.toDict()
   - `ocp_registerApi` - Wraps agent.registerApi(name, specUrl, baseUrl)
   - `ocp_listTools` - Wraps agent.listTools(apiName?)
   - `ocp_callTool` - Wraps agent.callTool(toolName, parameters, apiName?)
   - `ocp_searchTools` - Wraps agent.searchTools(query, apiName?)

3. **Chat Participant** automatically passes tools to language model
4. **Agent decides** when to discover APIs, register them, and call tools

### OCP Core Understanding

**Layer 1: Context Management** (HTTP Headers)
- Context flows across API calls via OCP headers
- Works with ANY existing HTTP API today
- AgentContext manages conversation state
- OCPHTTPClient adds headers automatically

**Layer 2: Schema Discovery** (OpenAPI)
- OCPAgent loads OpenAPI specs → discovers tools
- Validates parameters, builds requests
- Optional OCPRegistry for fast API lookup
- Zero infrastructure required

**Extension's Role**:
- Provide workspace context (user, workspace, VS Code state)
- Expose OCPAgent to chat agents
- Enable autonomous API discovery and usage

### Configuration Requirements

Based on JS library review, configuration needs:

**Required**:
- Workspace information (from VS Code)
- User identifier (from git config or VS Code settings)

**Optional**:
- API authentication tokens (for wrapApi)
- Custom registry URL
- Agent goal/objective

**VS Code Settings Schema** (to implement):
```json
{
  "ocp.user": "User identifier for OCP context",
  "ocp.registryUrl": "Custom OCP registry URL",
  "ocp.apiTokens": "Object mapping API names to auth tokens"
}
```

### Extension Purpose
**For agents to use during chat conversations** - NOT for direct user interaction.

The extension provides tools that AI agents (like GitHub Copilot) can invoke during chat sessions to:
- Create and maintain OCP context across conversation
- Discover APIs from OpenAPI specs or registry
- Call discovered tools with automatic validation
- Make context-aware API requests

### Technical Implementation

**Current Structure**:
```
ocp-vscode/
├── package.json          # Extension manifest with languageModelTools
├── tsconfig.json        # TypeScript config
├── src/
│   └── extension.ts     # Main extension (needs rebuild)
└── dist/                # Compiled output
```

**Dependencies**:
- `@opencontext/agent` (local: file:../ocp-javascript)
- `vscode` (types: ^1.85.0)

**Activation**:
- Event: `onStartupFinished`
- Registers Language Model Tools
- Creates Chat Participant that passes tools to LLM

**Integration Pattern**:
```typescript
import { OCPAgent } from '@opencontext/agent';

// ONE agent instance for workspace
const agent = new OCPAgent('vscode_copilot', user, workspace, goal);

// Wrap methods as tools
vscode.lm.registerTool('ocp_registerApi', {
  invoke: async (options) => {
    const result = await agent.registerApi(...);
    return new vscode.LanguageModelToolResult([...]);
  }
});
```

### Core Features to Implement (Agent-Callable Tools)

1. **Context Access**
   - `ocp_getContext` - Returns current OCP context
   - Auto-populated from VS Code: workspace, user, files

2. **API Discovery**
   - `ocp_registerApi` - Load OpenAPI spec, discover tools
   - `ocp_listTools` - Show available tools from registered APIs
   - `ocp_searchTools` - Find tools by name/description

3. **Tool Execution**
   - `ocp_callTool` - Call discovered tool with validation
   - Context automatically included in all requests

### TypeScript Type Safety

**OCPContextDict interface** enforces OCP spec:
```typescript
export interface OCPContextDict {
  context_id: string;
  agent_type: string;
  user: string | null;
  workspace: string | null;
  current_file: string | null;
  session: Record<string, any>;
  history: Array<Record<string, any>>;
  current_goal: string | null;
  context_summary: string | null;
  error_context: string | null;
  recent_changes: string[];
  api_specs: Record<string, string>;
  created_at: string;
  last_updated: string;
}
```

**Result**: TypeScript catches schema violations at compile time

### Version Information

- **Python**: 3.12.11
- **Node.js**: >=18.0.0
- **Poetry**: Used for Python dependency management
- **npm**: Used for JavaScript dependency management
- **ocp-python (PyPI: open-context-agent)**: 0.1.0 (145 tests, 100% passing)
- **ocp-javascript (npm: @opencontext/agent)**: 0.1.0 (174 tests, 100% passing - includes storage)
- **ocp-vscode**: 0.1.0 (in development, needs rebuild)
- **CLI**: 0.1.0 (11 tests, 100% passing)
- **Registry**: 0.1.0 (11 tests, 100% passing)

**Version Policy**: All components stay at 0.1.0 until first public release. No version bumps in pre-release.

---

**Last Updated**: October 30, 2025
**Context Thread**: JavaScript library storage implementation complete - OCPStorage class added with full Python parity (174 tests passing). Cross-language storage compatibility achieved using snake_case JSON schema. Ready for VS Code extension integration.