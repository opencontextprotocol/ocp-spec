# OCP VS Code Extension - Development Context

## Project Status: Phase 2 - Extension Foundation (CRITICAL REALIGNMENT NEEDED)

### Current State (2025-10-28)
**What Works:**
- ✅ Extension activates successfully
- ✅ Chat Participant (`@ocp`) passes tools to language model automatically
- ✅ Agent can autonomously call tools
- ✅ Basic tool: `ocp_createContext` returns OCP-compliant context
- ✅ TypeScript types enforce OCP schema (`OCPContextDict`)
- ✅ Both libraries at v0.1.0, 145 tests each, 100% passing

**What's Wrong (CRITICAL):**
- ❌ We've been REIMPLEMENTING the JS library instead of USING it!
- ❌ Current tools create new AgentContext instances per call (no state persistence)
- ❌ Missing the core OCP Agent functionality (registerApi, listTools, callTool)
- ❌ No configuration for API auth tokens

## What We Built (BUT INCORRECTLY)
- **Extension Location**: `ocp-vscode/` in the specification repo
- **Version**: 0.1.0
- **Purpose**: Provides tools for AI agents during chat (NOT user-facing UI)
- **Dependencies**: Uses local `@opencontext/agent` library from `../ocp-javascript`
- **Implementation**: Uses `vscode.lm.registerTool()` + Chat Participant
- **Problem**: Only wraps HTTP client, not the OCPAgent class!

## OCP Core Architecture (From Spec Review)

### What OCP Actually Is:
**Two Independent Layers:**
1. **Context Management** - HTTP headers carry agent state across API calls (works with ANY API today)
2. **Schema Discovery** - Load OpenAPI specs, discover tools, validate params, make calls

### The JavaScript Library Provides:
- **OCPAgent** - Main agent class with ALL the functionality we need:
  - `registerApi(name, specUrl?, baseUrl?)` - Load OpenAPI spec OR registry lookup
  - `listTools(apiName?)` - List available tools
  - `callTool(toolName, params, apiName?)` - Call with validation
  - `searchTools(query, apiName?)` - Find tools by description
  - Maintains state across calls
  - Persistent AgentContext

- **OCPHTTPClient** - Context-aware HTTP wrapper
  - Injects OCP headers automatically  
  - `wrapApi(context, baseUrl, authHeaders?)` - Create API-specific client with auth

- **AgentContext** - Context management
- **OCPSchemaDiscovery** - OpenAPI parsing
- **OCPRegistry** - Community API registry

### What Extension Should Actually Do:
1. **Create ONE OCPAgent instance** for the workspace
2. **Wrap its methods** as thin VS Code Language Model Tools:
   - `ocp_registerApi` → `agent.registerApi()`
   - `ocp_listTools` → `agent.listTools()`  
   - `ocp_callTool` → `agent.callTool()`
   - `ocp_getContext` → `agent.context.toDict()`
3. **Pass auth from VS Code settings** to OCPAgent/wrapApi

## Authentication Support in JS Library

```typescript
// wrapApi accepts auth headers
export function wrapApi(
    context: AgentContext, 
    baseUrl: string, 
    authHeaders?: Record<string, string>  // ← Auth goes here
): OCPHTTPClient
```

**Common patterns:**
```typescript
// GitHub
wrapApi(context, 'https://api.github.com', {
    'Authorization': 'Bearer ghp_xxxxx'
})

// Custom API
wrapApi(context, 'https://api.example.com', {
    'Authorization': 'Bearer token',
    'X-API-Key': 'key'
})
```

## VS Code Extension Configuration Schema (NEEDED)

```json
{
  "ocp.enabled": true,
  "ocp.registryUrl": "https://registry.opencontextprotocol.org",
  "ocp.apis": {
    "github": {
      "token": "ghp_xxxxxxxxxxxx",
      "authType": "Bearer"
    },
    "custom-api": {
      "token": "my-token",
      "authType": "ApiKey",
      "headerName": "X-API-Key"
    }
  }
}
```

## Current Implementation (WRONG ARCHITECTURE)

### Tool: `ocp_createContext` ❌ CREATES NEW CONTEXT PER CALL
```typescript
// WRONG - no state persistence
const createContextTool = vscode.lm.registerTool('ocp_createContext', {
  invoke: async () => {
    const agentContext = new AgentContext({...}); // ← New every time!
    return agentContext.toDict();
  }
});
```

### Tool: `ocp_callApi` ❌ CREATES NEW CONTEXT PER CALL
```typescript
// WRONG - no state persistence
const callApiTool = vscode.lm.registerTool('ocp_callApi', {
  invoke: async (params) => {
    const agentContext = new AgentContext({...}); // ← New every time!
    const client = new OCPHTTPClient(agentContext);
    return await client.request(...);
  }
});
```

**Problems:**
- Creates new context each call (no persistence)
- Only wraps HTTP client (missing API discovery)
- No auth token support
- Doesn't use OCPAgent class at all

## Correct Architecture (TO IMPLEMENT)

### Create ONE OCPAgent Instance
```typescript
let workspaceAgent: OCPAgent | undefined;

export function activate(context: vscode.ExtensionContext) {
  // Get workspace info
  const workspace = vscode.workspace.workspaceFolders?.[0]?.name || 'unknown';
  const user = process.env.USER || 'unknown';
  
  // Create ONE agent instance
  workspaceAgent = new OCPAgent('vscode_copilot', user, workspace);
  
  // Register tools that wrap agent methods
  registerTools(context, workspaceAgent);
}
```

### Wrap OCPAgent Methods as Tools
```typescript
// ✅ CORRECT - wraps agent.registerApi()
const registerApiTool = vscode.lm.registerTool('ocp_registerApi', {
  invoke: async (params: { name: string, specUrl?: string, baseUrl?: string }) => {
    const spec = await workspaceAgent!.registerApi(
      params.name,
      params.specUrl,
      params.baseUrl
    );
    return new vscode.LanguageModelToolResult([
      new vscode.LanguageModelTextPart(JSON.stringify(spec))
    ]);
  }
});

// ✅ CORRECT - wraps agent.listTools()
const listToolsTool = vscode.lm.registerTool('ocp_listTools', {
  invoke: async (params: { apiName?: string }) => {
    const tools = workspaceAgent!.listTools(params.apiName);
    return new vscode.LanguageModelToolResult([
      new vscode.LanguageModelTextPart(JSON.stringify(tools))
    ]);
  }
});

// ✅ CORRECT - wraps agent.callTool()
const callToolTool = vscode.lm.registerTool('ocp_callTool', {
  invoke: async (params: { toolName: string, parameters: any, apiName?: string }) => {
    const response = await workspaceAgent!.callTool(
      params.toolName,
      params.parameters,
      params.apiName
    );
    return new vscode.LanguageModelToolResult([
      new vscode.LanguageModelTextPart(JSON.stringify(response))
    ]);
  }
});
```

## Next Steps (BEFORE CODING)

### 1. Design Configuration Schema
- [ ] Review VS Code configuration API
- [ ] Design `ocp.*` settings schema
- [ ] Support for multiple API auth configs
- [ ] Default registry URL setting
- [ ] Enable/disable toggle

### 2. Refactor Extension to Use OCPAgent
- [ ] Import OCPAgent from @opencontext/agent
- [ ] Create ONE workspace-scoped OCPAgent instance
- [ ] Store it in extension context (persists across activations)
- [ ] Read auth tokens from VS Code settings
- [ ] Pass auth to wrapApi when registering APIs

### 3. Implement Core OCP Tools
- [ ] `ocp_registerApi(name, specUrl?, baseUrl?)` - Wraps agent.registerApi()
- [ ] `ocp_listTools(apiName?)` - Wraps agent.listTools()
- [ ] `ocp_callTool(toolName, parameters, apiName?)` - Wraps agent.callTool()
- [ ] `ocp_searchTools(query, apiName?)` - Wraps agent.searchTools()
- [ ] `ocp_getContext()` - Returns agent.context.toDict()

### 4. Update package.json Tool Definitions
- [ ] Add schemas for all 5 tools
- [ ] Include proper parameter types
- [ ] Update display names and descriptions

## Key Architectural Decisions

**✅ CORRECT Approach:**
- ONE OCPAgent instance per workspace
- State persists across tool calls
- Tools are thin wrappers around OCPAgent methods
- Auth comes from VS Code settings
- Extension uses the library, doesn't reimplement it

**❌ WRONG Approach (What We Did):**
- Creating new AgentContext per tool call
- No state persistence
- Reimplementing HTTP client logic
- No auth configuration support

## Testing Plan

1. **Configuration Test**
   - Set API tokens in VS Code settings
   - Verify they're read correctly

2. **Register API Test**
   ```
   @ocp Register the GitHub API from https://api.github.com/rest/openapi.json
   ```
   - Should discover tools and return count

3. **List Tools Test**
   ```
   @ocp What tools are available from GitHub?
   ```
   - Should show discovered tools

4. **Call Tool Test**
   ```
   @ocp List my GitHub repositories
   ```
   - Agent should autonomously:
     1. Call ocp_listTools to find "listUserRepos"  
     2. Call ocp_callTool with the tool name
     3. Get repos with OCP context headers

5. **Context Persistence Test**
   - Multiple tool calls should share same context
   - Interaction history should accumulate

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│         VS Code Extension               │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │   Chat Participant (@ocp)         │ │
│  │   - Passes tools to LLM           │ │
│  │   - Handles tool invocations      │ │
│  └──────────┬────────────────────────┘ │
│             │                           │
│  ┌──────────▼────────────────────────┐ │
│  │   Language Model Tools            │ │
│  │   - ocp_registerApi               │ │
│  │   - ocp_listTools                 │ │
│  │   - ocp_callTool                  │ │
│  │   - ocp_searchTools               │ │
│  │   - ocp_getContext                │ │
│  └──────────┬────────────────────────┘ │
│             │ (thin wrappers)          │
│  ┌──────────▼────────────────────────┐ │
│  │   OCPAgent (from JS library)      │ │
│  │   - ONE instance per workspace    │ │
│  │   - Persistent state              │ │
│  │   - Manages registered APIs       │ │
│  │   - Validates parameters          │ │
│  └──────────┬────────────────────────┘ │
│             │                           │
│  ┌──────────▼────────────────────────┐ │
│  │   OCPHTTPClient                   │ │
│  │   - Injects OCP headers           │ │
│  │   - Handles auth from settings    │ │
│  └──────────┬────────────────────────┘ │
└─────────────┼─────────────────────────┘
              │
              │ HTTP + OCP Headers
              ▼
     ┌────────────────────┐
     │   External APIs    │
     │   - GitHub         │
     │   - Custom APIs    │
     └────────────────────┘
```

## Files Structure

```
ocp-vscode/
├── package.json          - Extension manifest with tool definitions
├── src/
│   ├── extension.ts      - Main activation, OCPAgent instance creation
│   ├── config.ts         - Configuration schema and reading (NEW)
│   └── tools/            - Tool implementations (NEW)
│       ├── registerApi.ts
│       ├── listTools.ts
│       ├── callTool.ts
│       ├── searchTools.ts
│       └── getContext.ts
└── .agent/
    └── context.md        - This file
```

## Critical Reminders

1. **Don't Reimplement** - The JS library has everything we need
2. **ONE Agent Instance** - Per workspace, persistent state
3. **Configuration First** - Need settings schema for auth tokens
4. **Thin Wrappers** - Tools just call agent methods
5. **Review Spec Frequently** - Stay aligned with OCP goals
6. **Test Autonomously** - Agent should call tools without manual intervention

## Resources

- Spec: `/SPECIFICATION.md`
- Roadmap: `/ROADMAP.md`  
- JS Library: `/ocp-javascript/`
- JS Tests: `/ocp-javascript/tests/agent.test.ts` (see usage patterns)


**Returns (as JSON string):**
```json
{
  "status": 200,
  "statusText": "OK",
  "ok": true,
  "headers": { /* response headers */ },
  "data": { /* parsed response data */ },
  "text": "raw response text"
}
```

## Testing Instructions

1. Extension is running in Extension Development Host (separate window)
2. You need to chat with agent FROM that window to test commands
3. Call `ocp.createContext` command to test

## Code Details

### Key Files:
- `src/extension.ts` - Main extension logic
- `package.json` - Extension manifest with command definitions
- Uses `AgentContext` from `@opencontext/agent` library

### Constructor Note:
JavaScript library uses object params, not positional:
```typescript
new AgentContext({
  agent_type: 'vscode_copilot',
  user: userName,
  workspace: workspaceName
})
```

### Method Names:
JavaScript uses camelCase (not snake_case like Python):
- `updateGoal()` not `update_goal()`
- `toDict()` not `to_dict()`

## Next Steps After Testing
1. Verify command works and returns proper context
2. Add more commands (API calling, environment queries)
3. Test incrementally as we add features
4. Package and validate before publishing libraries

## Libraries Status
- **ocp-python**: 0.1.0 - 145 tests passing ✓
- **ocp-javascript**: 0.1.0 - 145 tests passing ✓
- Both ready for distribution after extension validates them
