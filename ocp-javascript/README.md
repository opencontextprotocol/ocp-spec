# OCP JavaScript Library

Context-aware HTTP client framework for AI agents.

## Installation

```bash
npm install @opencontextprotocol/agent
# or with yarn
yarn add @opencontextprotocol/agent
```

## Quick Start

```typescript
import { OCPAgent, wrapApi } from '@opencontextprotocol/agent';

// Create an OCP agent
const agent = new OCPAgent(
    'api_explorer',
    undefined,
    'my-project',
    'Analyze API endpoints'
);

// Register an API from OpenAPI specification
const apiSpec = await agent.registerApi(
    'github',
    'https://api.github.com/openapi.json'
);

// Create context-aware HTTP client
const githubClient = wrapApi(
    agent.context,
    'https://api.github.com',
    { 'Authorization': 'token your_token_here' }
);

// All requests include OCP context headers
const response = await githubClient.get('/user');
```

## Core Components

- **OCPAgent**: Main agent class with API discovery and tool invocation
- **AgentContext**: Context management with persistent conversation tracking
- **OCPHTTPClient**: Context-aware HTTP client wrapper
- **OCPSchemaDiscovery**: OpenAPI specification parsing and tool extraction
- **Headers**: OCP context encoding/decoding for HTTP headers
- **Validation**: JSON schema validation for context objects

## API Reference

### OCPAgent

```typescript
const agent = new OCPAgent(agentType, user?, workspace?, agentGoal?, registryUrl?);
await agent.registerApi(name, specUrl?, baseUrl?);
agent.listTools(apiName?);
await agent.callTool(toolName, parameters);
```

### AgentContext

```typescript
const context = new AgentContext({ agent_type, user?, workspace? });
context.addInteraction(action, apiEndpoint?, result?, metadata?);
context.updateGoal(newGoal, summary?);
context.toDict();
```

### HTTP Client Functions

```typescript
import { OCPHTTPClient, wrapApi } from '@opencontextprotocol/agent';

// Create OCP-aware HTTP client
const client = new OCPHTTPClient(context);
await client.request('GET', url, options);

// Create API-specific client
const apiClient = wrapApi(context, baseUrl, headers?);
```

## Development

```bash
# Clone repository
git clone https://github.com/opencontextprotocol/specification.git
cd specification/ocp-javascript

# Install dependencies
npm install

# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Build for distribution
npm run build

# Run specific test file
npm test context.test.ts
```

## Project Structure

```
src/
├── index.ts             # Public API exports
├── agent.ts             # OCPAgent class
├── context.ts           # AgentContext class  
├── http_client.ts       # HTTP client wrappers
├── headers.ts           # Header encoding/decoding
├── schema_discovery.ts  # OpenAPI parsing
├── registry.ts          # Registry client
├── validation.ts        # JSON schema validation
└── errors.ts            # Error classes

tests/
├── agent.test.ts        # OCPAgent tests
├── context.test.ts      # AgentContext tests
├── http_client.test.ts  # HTTP client tests
├── headers.test.ts      # Header tests
├── schema_discovery.test.ts # Schema parsing tests
├── registry.test.ts     # Registry tests
└── validation.test.ts   # Validation tests
```

## TypeScript Support

This library is written in TypeScript and includes full type definitions. All exports are fully typed for excellent IDE support and type safety.

## License

MIT License - see LICENSE file.
