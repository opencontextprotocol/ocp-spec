# OCP CLI

A command-line interface for Open Context Protocol operations using the OCP Python library. Provides context management, API testing, and registry integration with zero infrastructure requirements.

## Installation

### Production Use

1. **Install Dependencies**:
   ```bash
   pip install -r cli/requirements.txt
   ```

2. **Add CLI to PATH**:
   ```bash
   # Option 1: Symlink to /usr/local/bin
   sudo ln -s /path/to/specification/cli/ocp /usr/local/bin/ocp

   # Option 2: Add to your shell profile
   echo 'export PATH="/path/to/specification/cli:$PATH"' >> ~/.bashrc
   ```

### Development Use

For development with the local OCP Python library:

1. **Use the development wrapper**:
   ```bash
   cd cli
   ./ocp-dev --help
   ```

   The `ocp-dev` script automatically sets `PYTHONPATH` to use the local `../ocp-python/src` library.

2. **Or manually set PYTHONPATH**:
   ```bash
   PYTHONPATH=../ocp-python/src python ocp --help
   ```

## Features

### Registry Integration
- Uses the OCP Python library's `OCPRegistry` for fast API discovery
- Seamless integration with community registry for pre-discovered APIs
- Intelligent fallback to direct OpenAPI specification parsing
- Helpful error messages with API suggestions

### Context Management
- Create and manage OCP contexts for AI agents
- Track workspace, goals, and interaction history
- Persistent context storage in `~/.ocp/context.json`

### API Testing
- Make OCP-enhanced HTTP requests with context headers
- Automatic OpenAPI spec discovery and tool extraction
- Registry-first API lookup for improved performance

## Usage

### Context Management

```bash
# Create new context
ocp context create --user alice --type ide_copilot --goal "debug tests" --workspace "payment-service"

# Show current context
ocp context show
```

### API Testing

```bash
# Make OCP-enhanced API call
ocp call GET https://api.github.com/user --auth "token ghp_xxx"

# Test API with OpenAPI spec
ocp test api https://api.github.com --spec https://api.github.com/rest/openapi.json --auth "token ghp_xxx"
```

### Registry Operations

```bash
# List all APIs in registry
ocp registry list

# Search for APIs
ocp registry search github
ocp registry search "payment apis"

# Get detailed information about an API
ocp registry get github

# List available categories
ocp registry categories

# Show registry statistics
ocp registry stats

# Register a new API from JSON file
ocp registry register my-api.json

# Validate an API specification
ocp registry validate https://api.github.com/rest/openapi.json --base-url https://api.github.com

# Use custom registry URL
ocp registry --url https://registry.example.com list
```

### Validation

```bash
# Validate context file
ocp validate context my-context.json
```

## Features

- **Uses OCP Library**: Built on the official OCP Python library (no code duplication)
- **Context Management**: Create, view, and manage OCP contexts  
- **API Testing**: Test APIs with OCP context headers
- **Schema Discovery**: Automatic tool discovery from OpenAPI specs
- **Registry Operations**: Search, register, and validate APIs
- **Validation**: Validate context files and API specifications

## Examples

```bash
# Complete workflow
ocp context create --user alice --type debugging_assistant --goal "fix payment tests" --workspace "payment-service"
ocp call GET https://api.github.com/search/issues --auth "token ghp_xxx" --data '{"q":"payment test failure"}'
ocp test api https://api.github.com --spec https://api.github.com/rest/openapi.json
ocp registry search github
ocp validate context ~/.ocp/context.json
```

The CLI stores context in `~/.ocp/context.json` and automatically applies OCP headers to API calls using the official OCP Python library.