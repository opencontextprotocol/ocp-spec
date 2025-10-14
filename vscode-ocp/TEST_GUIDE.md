# Test Configuration for OCP VS Code Extension

## Running Tests

### Unit Tests
Run unit tests for individual components:
```bash
npm run test:unit
```

### Integration Tests
Run full VS Code extension tests:
```bash
npm test
```

### Coverage Report
Generate test coverage report:
```bash
npm run test:coverage
```

### Watch Mode
Run tests in watch mode during development:
```bash
npm run watch
```

## Test Structure

### Unit Tests
- `contextManager.test.ts` - Tests for OCP context management
- `httpInterceptor.test.ts` - Tests for HTTP request interception
- `demoCommands.test.ts` - Tests for demo command functionality

### Integration Tests
- `extension.test.ts` - End-to-end extension activation and command tests

## Test Coverage Goals

- **Context Manager**: 100% coverage of core context operations
- **HTTP Interceptor**: 95+ coverage of header generation and interception
- **Demo Commands**: 90+ coverage of command registration and execution
- **Extension Integration**: 100% coverage of activation/deactivation

## Mock Strategy

Tests use simplified mock objects for VS Code APIs to:
- Avoid complex VS Code environment setup
- Focus on OCP-specific logic
- Ensure reliable and fast test execution
- Maintain test isolation

## Continuous Integration

Tests are designed to run in CI environments with:
- No VS Code UI dependencies
- Deterministic execution
- Clear pass/fail criteria
- Comprehensive error reporting