---
title: Quick Start
weight: 1
---

Get started with the Open Context Protocol in minutes.

## 1. Install a Client Library

{{< tabs items="Python,JavaScript" >}}

{{< tab >}}
```bash
pip install ocp-python
```
{{< /tab >}}

{{< tab >}}
```bash
npm install @ocp/client
```
{{< /tab >}}

{{< /tabs >}}

## 2. Generate Tools from OpenAPI

The core OCP feature: automatically generate callable agent tools from any OpenAPI specification.

{{< tabs items="Python,JavaScript" >}}

{{< tab >}}
```python
import ocp

# Generate tools from GitHub API
github = ocp.discover_tools("https://api.github.com/openapi.json")

# Tools are now callable functions
repos = github.list_user_repositories()
issue = github.create_issue(
    owner="myorg", 
    repo="myproject",
    title="Bug in payment flow"
)
```
{{< /tab >}}

{{< tab >}}
```javascript
import { discoverTools } from '@ocp/client';

// Generate tools from GitHub API
const github = await discoverTools("https://api.github.com/openapi.json");

// Tools are now callable functions
const repos = await github.listUserRepositories();
const issue = await github.createIssue({
    owner: "myorg",
    repo: "myproject", 
    title: "Bug in payment flow"
});
```
{{< /tab >}}

{{< /tabs >}}

## 3. Context Flows Automatically

Once you set up an agent, context persists across all API calls:

{{< tabs items="Python,JavaScript" >}}

{{< tab >}}
```python
# Create agent with goal
agent = ocp.Agent(
    agent_type="debugging_assistant",
    goal="fix_payment_validation"
)

# All subsequent API calls include context
repos = github.list_repositories()          # Context: goal=fix_payment_validation
issues = github.list_issues(repo="payments") # Context: previous call + goal
```
{{< /tab >}}

{{< tab >}}
```javascript
// Create agent with goal
const agent = new Agent({
    agentType: "debugging_assistant", 
    goal: "fix_payment_validation"
});

// All subsequent API calls include context
const repos = await github.listRepositories();         // Context: goal=fix_payment_validation  
const issues = await github.listIssues({repo: "payments"}); // Context: previous call + goal
```
{{< /tab >}}

{{< /tabs >}}

## 4. Use Community Registry (Optional)

Discover APIs quickly using the community registry:

{{< tabs items="Python,JavaScript" >}}

{{< tab >}}
```python
# Discover popular APIs by name
github = ocp.discover_tools("github")    # From registry
stripe = ocp.discover_tools("stripe")    # From registry
slack = ocp.discover_tools("slack")      # From registry

# Or from direct URLs  
custom = ocp.discover_tools("https://api.mycompany.com/openapi.json")
```
{{< /tab >}}

{{< tab >}}
```javascript
// Discover popular APIs by name
const github = await discoverTools("github");   // From registry
const stripe = await discoverTools("stripe");   // From registry
const slack = await discoverTools("slack");     // From registry

// Or from direct URLs
const custom = await discoverTools("https://api.mycompany.com/openapi.json");
```
{{< /tab >}}

{{< /tabs >}}

## What Happens Behind the Scenes

1. **Tool Discovery**: OCP parses the OpenAPI spec and generates callable functions for each API operation
2. **Context Injection**: Every API call automatically includes OCP headers with current context
3. **Context Evolution**: Context grows with each interaction, building conversation history
4. **Seamless Integration**: Works with existing APIs without requiring server changes

## Next Steps

- **[OpenAPI Tools](../openapi-tools/)**: Deep dive into automatic tool generation
- **[Examples](../examples/)**: Common implementation patterns and use cases
- **[Libraries](../../libraries/)**: Language-specific client libraries and APIs