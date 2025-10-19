# OCP CLI

A standalone command-line interface for Open Context Protocol operations including context management, API testing, and registry operations.

## Installation

Add the CLI to your PATH:

```bash
# Option 1: Symlink to /usr/local/bin
sudo ln -s /path/to/specification/cli/ocp /usr/local/bin/ocp

# Option 2: Add to your shell profile
echo 'export PATH="/path/to/specification/cli:$PATH"' >> ~/.bashrc
```

## Usage

### Context Management

```bash
# Create new context
ocp context create --user alice --type ide_copilot --goal "debug tests"

# Show current context
ocp context show
ocp context show --format yaml
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

### API Testing

```bash
# Make OCP-enhanced API call
ocp call GET https://api.github.com/user --auth "token ghp_xxx"

# Test API with OpenAPI spec
ocp test api https://api.github.com --spec https://api.github.com/rest/openapi.json --auth "token ghp_xxx"
```

### Validation

```bash
# Validate context file
ocp validate context my-context.json
```

## Features

- **Context Management**: Create, view, and manage OCP contexts
- **API Testing**: Test APIs with OCP context headers
- **Validation**: Validate context files and API responses
- **Zero Dependencies**: Pure Python with minimal requirements
- **Standalone**: No imports from examples or other projects

## Examples

```bash
# Complete workflow
ocp context create --user alice --type debugging_assistant --goal "fix payment tests"
ocp call GET https://api.github.com/search/issues --auth "token ghp_xxx" --data '{"q":"payment test failure"}'
ocp validate context ~/.ocp/context.json
```

The CLI stores context in `~/.ocp/context.json` and automatically applies OCP headers to API calls.