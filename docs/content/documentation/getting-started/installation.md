---
title: Installation
weight: 1
---

Get OCP up and running in your environment with language-specific setup guides.

## Python

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install OCP Python Library

```bash
# Install from PyPI
pip install ocp-python

# Or with conda
conda install -c conda-forge ocp-python

# Or with poetry
poetry add ocp-python
```

### Verify Installation

```python
import ocp

# Test basic functionality
agent = ocp.Agent(agent_type="test")
print(f"✅ OCP Python {ocp.__version__} installed successfully")

# Test tool discovery
github = agent.discover_tools("github")
print(f"✅ Discovered {len(github.tools)} GitHub tools")
```

### Optional: Development Installation

```bash
# Clone the repository
git clone https://github.com/opencontextprotocol/ocp-python.git
cd ocp-python

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## JavaScript/TypeScript

### Prerequisites
- Node.js 16 or higher
- npm, yarn, or pnpm package manager

### Install OCP JavaScript Library

```bash
# With npm
npm install @opencontextprotocol/agent

# With yarn
yarn add @opencontextprotocol/agent

# With pnpm
pnpm add @opencontextprotocol/agent
```

### Verify Installation

```javascript
import { Agent } from '@opencontextprotocol/agent';

// Test basic functionality
const agent = new Agent({agentType: "test"});
console.log('✅ OCP JavaScript installed successfully');

// Test tool discovery
const github = await agent.discoverTools("github");
console.log(`✅ Discovered ${github.tools.length} GitHub tools`);
```

### TypeScript Setup

```bash
# Install TypeScript if not already installed
npm install -g typescript

# Create tsconfig.json
cat > tsconfig.json << EOF
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "node",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  }
}
EOF
```

## VS Code Extension

### Install from Marketplace

1. **Open VS Code**
2. **Go to Extensions** (Ctrl/Cmd + Shift + X)
3. **Search for** "Open Context Protocol"
4. **Click Install**

### Install from Command Line

```bash
# Install extension
code --install-extension opencontextprotocol.ocp-vscode

# Verify installation
code --list-extensions | grep opencontextprotocol
```

### Extension Setup

1. **Open a workspace** in VS Code
2. **Extension auto-detects** project structure
3. **Context is automatically created** from:
   - Current workspace folder
   - Git branch and repository
   - Open files and recent activity
   - Project type and framework

### Verify Extension

```typescript
// Use Command Palette (Ctrl/Cmd + Shift + P)
// Type: "OCP: Create Context"

// Or check status bar for OCP indicator
// Should show workspace context and available tools
```

## CLI Tool

### Install OCP CLI

```bash
# Install globally
pip install ocp-cli

# Or install in isolated environment
pipx install ocp-cli

# Verify installation
ocp --version
```

### CLI Setup

```bash
# Create configuration directory
mkdir -p ~/.ocp

# Initialize configuration
ocp init

# Test CLI functionality
ocp context create --user $(whoami) --type cli_test
ocp validate context ~/.ocp/context.json
```

## Environment Configuration

### API Authentication

Create a `.env` file or set environment variables:

```bash
# GitHub API access
export GITHUB_TOKEN="ghp_your_token_here"

# OpenAI API access
export OPENAI_API_KEY="sk-your_key_here"

# Stripe API access (for examples)
export STRIPE_SECRET_KEY="sk_test_your_key_here"
```

### OCP Registry Configuration

```bash
# Use community registry (default)
export OCP_REGISTRY_URL="https://registry.ocp.dev"

# Or use private registry
export OCP_REGISTRY_URL="https://internal.company.com/ocp-registry"

# Disable registry (direct URLs only)
export OCP_REGISTRY_ENABLED="false"
```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Python: Module not found
pip install --upgrade ocp-python

# Node.js: Cannot resolve module
npm install --save @opencontextprotocol/agent
```

#### Network Issues
```bash
# Registry connection problems
ocp registry status
ocp registry refresh

# Direct API access
ocp discover https://api.github.com/openapi.json
```

#### Permission Errors
```bash
# Python: Permission denied
pip install --user ocp-python

# VS Code: Extension not loading
code --disable-extensions
code --enable-extension opencontextprotocol.ocp-vscode
```

### Getting Help

- **Documentation**: [https://opencontextprotocol.org](https://opencontextprotocol.org)
- **GitHub Issues**: [https://github.com/opencontextprotocol/ocp-python/issues](https://github.com/opencontextprotocol/ocp-python/issues)
- **Community Discord**: [https://discord.gg/ocp](https://discord.gg/ocp)

## Next Steps

Now that OCP is installed, try the quick start guide:

{{< cards >}}
{{< card link="../quick-start/" title="⚡ Quick Start" subtitle="Get your first OCP agent working in 5 minutes" >}}
{{< /cards >}}

Or dive deeper into the superpowers:

{{< cards >}}
{{< card link="../context/" title="🧠 Context" subtitle="Understand persistent context across API calls" >}}
{{< card link="../tools/" title="🔧 Tool Discovery" subtitle="Learn automatic API integration" >}}
{{< /cards >}}