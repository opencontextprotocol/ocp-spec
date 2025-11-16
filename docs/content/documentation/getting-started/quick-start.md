---
title: Quick Start
weight: 2
---

Get OCP running in 5 minutes and experience all 4 superpowers in action.

## Prerequisites

{{< tabs items="Python,JavaScript,VS Code" >}}

{{< tab >}}
```bash
# Ensure Python 3.8+ and pip are installed
python --version  # 3.8+
pip --version

# Install OCP
pip install ocp-python
```
{{< /tab >}}

{{< tab >}}
```bash
# Ensure Node.js 16+ and npm are installed
node --version    # 16+
npm --version

# Install OCP
npm install @opencontextprotocol/agent
```
{{< /tab >}}

{{< tab >}}
```bash
# Install VS Code extension
code --install-extension opencontextprotocol.ocp-vscode

# Or install from marketplace
# Search for "Open Context Protocol"
```
{{< /tab >}}

{{< /tabs >}}

## 5-Minute Demo: All 4 Superpowers

Let's build an AI agent that uses GitHub APIs with full context awareness. This example showcases all OCP superpowers working together.

### Step 1: Create Your Agent

{{< tabs items="Python,JavaScript" >}}

{{< tab >}}
```python
#!/usr/bin/env python3
import ocp
import json

# Create an OCP-aware agent
agent = ocp.Agent(
    agent_type="github_assistant",
    user="demo_user",
    session_id="quickstart_session"
)

print(f"✅ Agent created with context: {agent.context.session_id}")
```
{{< /tab >}}

{{< tab >}}
```javascript
import { Agent } from '@opencontextprotocol/agent';

// Create an OCP-aware agent
const agent = new Agent({
    agentType: "github_assistant",
    user: "demo_user",
    sessionId: "quickstart_session"
});

console.log(`✅ Agent created with context: ${agent.context.sessionId}`);
```
{{< /tab >}}

{{< /tabs >}}

### Step 2: 🧠 Context Superpower

Let's add some context about our current task:

{{< tabs items="Python,JavaScript" >}}

{{< tab >}}
```python
# Add context about our task
agent.context.add_data("task", {
    "goal": "Find popular JavaScript testing libraries",
    "repositories_to_check": ["jest", "vitest", "cypress"],
    "criteria": "stars > 1000 AND updated_in_last_year"
})

# Context persists across all API calls
print("🧠 Context established:", json.dumps(agent.context.data, indent=2))
```
{{< /tab >}}

{{< tab >}}
```javascript
// Add context about our task
agent.context.addData("task", {
    goal: "Find popular JavaScript testing libraries",
    repositoriesToCheck: ["jest", "vitest", "cypress"],
    criteria: "stars > 1000 AND updated_in_last_year"
});

// Context persists across all API calls
console.log("🧠 Context established:", JSON.stringify(agent.context.data, null, 2));
```
{{< /tab >}}

{{< /tabs >}}

### Step 3: 🔧 Tool Discovery Superpower

Discover GitHub APIs automatically - no manual integration needed:

{{< tabs items="Python,JavaScript" >}}

{{< tab >}}
```python
# Automatically discover GitHub's API
github = agent.discover_tools("github")

# OCP parsed the OpenAPI spec and created tools
print(f"🔧 Discovered {len(github.tools)} GitHub tools:")
for tool in github.tools[:5]:  # Show first 5
    print(f"  • {tool.name}: {tool.description}")
    
# Tools understand OCP context automatically
repos_tool = github.get_tool("repos_get")
search_tool = github.get_tool("search_repositories")
```
{{< /tab >}}

{{< tab >}}
```javascript
// Automatically discover GitHub's API
const github = await agent.discoverTools("github");

// OCP parsed the OpenAPI spec and created tools
console.log(`🔧 Discovered ${github.tools.length} GitHub tools:`);
github.tools.slice(0, 5).forEach(tool => {
    console.log(`  • ${tool.name}: ${tool.description}`);
});

// Tools understand OCP context automatically
const reposTool = github.getTool("repos_get");
const searchTool = github.getTool("search_repositories");
```
{{< /tab >}}

{{< /tabs >}}

### Step 4: 🌐 Registry Superpower

Use the community registry to find pre-indexed APIs:

{{< tabs items="Python,JavaScript" >}}

{{< tab >}}
```python
# Search registry for more APIs
registry_results = agent.search_registry("testing", category="development")

print("🌐 Found APIs in registry:")
for api in registry_results[:3]:
    print(f"  • {api['name']}: {api['description']}")
    print(f"    Categories: {', '.join(api['categories'])}")
    
# Pre-validated and indexed for instant discovery
```
{{< /tab >}}

{{< tab >}}
```javascript
// Search registry for more APIs
const registryResults = await agent.searchRegistry("testing", {category: "development"});

console.log("🌐 Found APIs in registry:");
registryResults.slice(0, 3).forEach(api => {
    console.log(`  • ${api.name}: ${api.description}`);
    console.log(`    Categories: ${api.categories.join(', ')}`);
});

// Pre-validated and indexed for instant discovery
```
{{< /tab >}}

{{< /tabs >}}

### Step 5: 💻 IDE Integration Superpower

If you have the VS Code extension installed, your workspace context is automatically included:

{{< tabs items="Python,JavaScript" >}}

{{< tab >}}
```python
# VS Code extension automatically adds workspace context
if agent.context.workspace:
    print("💻 VS Code workspace detected:")
    print(f"  Project: {agent.context.workspace.get('project_name')}")
    print(f"  Files: {len(agent.context.workspace.get('files', []))}")
    print(f"  Git branch: {agent.context.workspace.get('git_branch')}")
```
{{< /tab >}}

{{< tab >}}
```javascript
// VS Code extension automatically adds workspace context
if (agent.context.workspace) {
    console.log("💻 VS Code workspace detected:");
    console.log(`  Project: ${agent.context.workspace.projectName}`);
    console.log(`  Files: ${agent.context.workspace.files?.length || 0}`);
    console.log(`  Git branch: ${agent.context.workspace.gitBranch}`);
}
```
{{< /tab >}}

{{< /tabs >}}

### Step 6: Put It All Together

Now let's use the tools with full context awareness:

{{< tabs items="Python,JavaScript" >}}

{{< tab >}}
```python
# Search for repositories with full context
async def find_testing_libraries():
    # Context is automatically included in all API calls
    results = await search_tool.call({
        "q": "language:javascript testing framework stars:>1000",
        "sort": "stars",
        "per_page": 5
    })
    
    libraries = []
    for repo in results["items"]:
        # Get detailed info with context preserved
        details = await repos_tool.call({
            "owner": repo["owner"]["login"],
            "repo": repo["name"]
        })
        
        libraries.append({
            "name": details["name"],
            "description": details["description"],
            "stars": details["stargazers_count"],
            "updated": details["updated_at"],
            "context_session": agent.context.session_id  # Context included!
        })
    
    return libraries

# Run the search
import asyncio
libraries = asyncio.run(find_testing_libraries())

print("🎉 Results (with context):")
for lib in libraries:
    print(f"  • {lib['name']}: ⭐{lib['stars']:,} stars")
    print(f"    Session: {lib['context_session']}")
```
{{< /tab >}}

{{< tab >}}
```javascript
// Search for repositories with full context
async function findTestingLibraries() {
    // Context is automatically included in all API calls
    const results = await searchTool.call({
        q: "language:javascript testing framework stars:>1000",
        sort: "stars",
        per_page: 5
    });
    
    const libraries = [];
    for (const repo of results.items) {
        // Get detailed info with context preserved
        const details = await reposTool.call({
            owner: repo.owner.login,
            repo: repo.name
        });
        
        libraries.push({
            name: details.name,
            description: details.description,
            stars: details.stargazers_count,
            updated: details.updated_at,
            contextSession: agent.context.sessionId  // Context included!
        });
    }
    
    return libraries;
}

// Run the search
const libraries = await findTestingLibraries();

console.log("🎉 Results (with context):");
libraries.forEach(lib => {
    console.log(`  • ${lib.name}: ⭐${lib.stars.toLocaleString()} stars`);
    console.log(`    Session: ${lib.contextSession}`);
});
```
{{< /tab >}}

{{< /tabs >}}

## What Just Happened?

You just experienced all 4 OCP superpowers:

1. **🧠 Context**: Your task information was preserved across all API calls
2. **🔧 Tool Discovery**: GitHub's API was automatically parsed and made available  
3. **🌐 Registry**: You searched a community catalog of pre-indexed APIs
4. **💻 IDE Integration**: Your workspace context was automatically included (if using VS Code)

## Key Benefits You Just Saw

- **Zero Setup**: No manual API integration or SDK installation
- **Automatic Context**: Your agent's state persists across all tool calls
- **Instant Discovery**: Any OpenAPI-compliant API becomes usable immediately
- **Workspace Awareness**: Your development environment is part of the context

## Next Steps

Now that you've seen OCP in action, explore each superpower in detail:

{{< cards >}}
{{< card link="../context/" title="🧠 Master Context" subtitle="Learn advanced context patterns and persistence" >}}
{{< card link="../tools/" title="🔧 Advanced Tool Discovery" subtitle="Custom naming, validation, and OpenAPI extensions" >}}
{{< card link="../registry/" title="🌐 Registry Deep Dive" subtitle="Publishing APIs and private registries" >}}
{{< card link="../ide/" title="💻 IDE Workflows" subtitle="Multi-agent coordination and workspace patterns" >}}
{{< /cards >}}

Or check out real-world examples:

{{< cards >}}
{{< card link="../examples/" title="📋 Examples" subtitle="Complete projects using OCP" >}}
{{< card link="../learning-paths/" title="📚 Learning Paths" subtitle="Guided paths by your role and goals" >}}
{{< /cards >}}

## Troubleshooting

### Common Quick Start Issues

#### Missing Authentication
```bash
# GitHub requires a token for API access
export GITHUB_TOKEN="ghp_your_token_here"

# Get token at: https://github.com/settings/tokens
```

#### Tool Discovery Fails
```python
# Check if the API URL is accessible
agent.validate_api_url("https://api.github.com")

# Or use direct OpenAPI spec
github = agent.discover_tools("https://api.github.com/openapi.json")
```

#### Context Not Persisting
```python
# Ensure session ID is consistent
agent = ocp.Agent(session_id="my_persistent_session")

# Check context data
print(agent.context.to_dict())
```

Need help? Check our [troubleshooting guide](/troubleshooting/) or ask in the [community discord](https://discord.gg/ocp).