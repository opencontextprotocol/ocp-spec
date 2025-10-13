# OCP VS Code Extension

A demonstration extension showcasing the **Open Context Protocol (OCP)** vs **Model Context Protocol (MCP)** for AI agent context management.

## 🚀 What is OCP?

**Open Context Protocol (OCP)** is a revolutionary approach to AI agent context management that provides:

- **Zero Infrastructure**: No servers, no complex setup
- **Automatic Context Discovery**: Intelligent workspace and file tracking
- **HTTP Header Enhancement**: Seamless context injection into API calls
- **Language Agnostic**: Works with any AI service or HTTP API
- **Developer Friendly**: Instant setup, automatic maintenance

## 🆚 OCP vs MCP Comparison

| Feature | OCP | MCP |
|---------|-----|-----|
| **Setup Time** | 1 minute | 1+ hours |
| **Infrastructure** | None required | Requires servers |
| **Context Management** | Automatic | Manual |
| **API Integration** | HTTP headers | Custom protocols |
| **Maintenance** | Zero | Ongoing server management |
| **Language Support** | Any HTTP client | Client library required |

## 🎯 Key Features

### Automatic Context Tracking
- **Workspace Detection**: Automatically tracks current workspace and project
- **File Context**: Monitors active file and recent changes
- **Error Tracking**: Captures error states for debugging context
- **Session Memory**: Maintains interaction history and user goals

### HTTP Request Enhancement
- **OCP Headers**: Automatically adds rich context headers to outgoing requests
- **Zero Configuration**: Works with any HTTP client or API
- **Context Injection**: Seamless integration with existing workflows

### Interactive Demonstrations
- **Live Context Viewer**: See your current OCP context in real-time
- **API Simulation**: Test how OCP headers enhance API calls
- **Setup Comparison**: Interactive demo showing OCP vs MCP complexity
- **Context Memory**: Demonstrate persistent context across interactions

## 📦 Installation

1. Install the extension from VS Code marketplace (coming soon)
2. Or build from source:
   ```bash
   git clone [repository]
   cd vscode-ocp
   npm install
   npm run compile
   ```

## 🔧 Commands

Access via Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`):

- **`OCP: Show Context Status`** - View current context state
- **`OCP: Demonstrate Context Memory`** - See persistent context in action
- **`OCP: Compare with MCP`** - Side-by-side setup comparison
- **`OCP: Simulate API Call`** - Test API integration with OCP headers
- **`OCP: Show Setup Comparison`** - Interactive setup complexity demo
- **`OCP: Generate Context Report`** - Create detailed context report
- **`OCP: Demo Workflow`** - Complete OCP demonstration workflow

## ⚙️ Configuration

Configure OCP behavior in VS Code settings:

```json
{
  "ocp.enabled": true,
  "ocp.agentType": "ide_copilot",
  "ocp.debug": false,
  "ocp.autostart": true
}
```

### Settings Reference

- **`ocp.enabled`**: Enable/disable OCP context tracking (default: `true`)
- **`ocp.agentType`**: Agent type identifier (default: `"ide_copilot"`)
- **`ocp.debug`**: Enable debug logging (default: `false`)
- **`ocp.autostart`**: Start context tracking on activation (default: `true`)

## 🧠 How It Works

### Context Collection
OCP automatically tracks:
1. **Current workspace** and project structure
2. **Active file** and recent modifications
3. **User goals** and current objectives
4. **Error states** and debugging context
5. **Interaction history** and session metrics

### HTTP Enhancement
When enabled, OCP intercepts outgoing HTTP requests and adds context headers:

```http
X-OCP-Context-ID: ocp-abc123def
X-OCP-Agent-Type: ide_copilot
X-OCP-User: developer
X-OCP-Workspace: my-project
X-OCP-Current-File: src/main.py
X-OCP-Goal: implement-auth-system
X-OCP-Recent-Changes: added-login-form;fixed-validation
X-OCP-Session-Duration: 15m
X-OCP-Interaction-Count: 7
X-OCP-Context-Summary: file:main.py|changes:2|last:code_edit
```

### AI Agent Integration
AI agents can read these headers to understand:
- **What you're working on** - current file, workspace, recent changes
- **Your current goal** - what you're trying to accomplish
- **Session context** - interaction history and patterns
- **Error states** - debugging context and issues
- **Development flow** - recent activity and patterns

## 🔮 Why OCP Wins

### Zero Infrastructure Advantage
- **MCP**: Requires server setup, endpoint configuration, authentication
- **OCP**: Works immediately with any HTTP API

### Automatic Context Discovery
- **MCP**: Manual context passing in each request
- **OCP**: Intelligent workspace tracking and automatic injection

### Universal Compatibility
- **MCP**: Requires client library for each language
- **OCP**: Works with any HTTP client in any language

### Developer Experience
- **MCP**: Complex setup, ongoing maintenance
- **OCP**: Install extension, start coding

## 🛠️ Development

### Building the Extension

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch mode for development
npm run watch

# Package extension
npm run package
```

### Project Structure

```
vscode-ocp/
├── src/
│   ├── extension.ts          # Main extension entry point
│   ├── contextManager.ts     # OCP context tracking
│   ├── httpInterceptor.ts    # HTTP request enhancement
│   └── demoCommands.ts       # Interactive demonstrations
├── package.json              # Extension manifest
├── tsconfig.json            # TypeScript configuration
└── README.md                # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Related Projects

- [OCP Python Library](../ocp-python/) - Reference implementation
- [OCP Specification](../docs/) - Protocol specification
- [OCP Examples](../examples/) - Usage examples

## 🚀 Getting Started

1. Install the extension
2. Open any workspace
3. Run `OCP: Demo Workflow` to see the complete demonstration
4. Try `OCP: Show Context Status` to see your current context
5. Use `OCP: Compare with MCP` to understand the advantages

**Welcome to the future of zero-infrastructure AI agent context management! 🎉**