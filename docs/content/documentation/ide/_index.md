---
title: "IDE Integration"
weight: 5
cascade:
  type: docs
---

The fourth OCP superpower brings all OCP capabilities directly into your development environment through a **drop-in VS Code extension** that empowers chat agents with context awareness, tool discovery, and API integration.

## The Problem OCP Solves

**Before OCP:**
```
Agent: "Can you check if there are any GitHub issues related to this payment error?"

Developer: *manually opens browser*
          *navigates to GitHub*
          *searches for issues*
          *copies/pastes information back to chat*
          *loses context between different tools*
```

**With OCP VS Code Extension:**
```
Agent: "Let me check GitHub issues for payment errors in your current workspace"

Extension: *automatically creates context from workspace*
           *discovers GitHub API tools*
           *searches issues with workspace context*
           *provides results with full context awareness*
```

## How IDE Integration Works

The OCP VS Code extension provides seamless integration that transforms any AI chat agent into a workspace-aware, API-enabled assistant.

### Integration Components

{{< cards >}}
{{< card link="vscode-extension/" title="VS Code Extension" subtitle="Installation, setup, and core features of the OCP extension" >}}
{{< card link="workspace-context/" title="Workspace Context" subtitle="How the extension captures and maintains workspace state" >}}
{{< card link="agent-integration/" title="Agent Integration" subtitle="How chat agents use OCP capabilities in VS Code" >}}
{{< card link="api-configuration/" title="API Configuration" subtitle="Setting up authentication and API access" >}}
{{< card link="workflow-examples/" title="Workflow Examples" subtitle="Real-world examples of agents using OCP in IDEs" >}}
{{< /cards >}}

## Quick Start

### 1. Install Extension
```bash
# Install from VS Code marketplace
ext install opencontextprotocol.ocp-vscode

# Or install from command line
code --install-extension opencontextprotocol.ocp-vscode
```

### 2. Automatic Context Creation
The extension automatically creates OCP context from your workspace:

```json
{
  "contextId": "ctx_vscode_abc123",
  "agentType": "vscode_copilot",
  "user": "alice",
  "workspace": "ecommerce-backend",
  "workspacePath": "/Users/alice/projects/ecommerce-backend",
  "gitBranch": "fix-payment-error",
  "currentGoal": "Working on branch: fix-payment-error",
  "currentFile": "payment_validator.py",
  "workspaceContext": {
    "projectType": "python_web_app",
    "framework": "django",
    "recentFiles": [
      "payment_validator.py",
      "test_payment_validation.py",
      "models/payment.py"
    ]
  }
}
```

### 3. Agent Commands Available
Once installed, agents can use these commands:

| Command | Purpose | Example Usage |
|---------|---------|---------------|
| `ocp.createContext` | Create context from workspace | Get current project state |
| `ocp.discoverApis` | Find relevant APIs for project | Discover GitHub/AWS tools |
| `ocp.makeApiCall` | Execute API calls with context | Search issues, deploy code |
| `ocp.updateContext` | Update agent goal/context | Change focus to different task |

## Workspace Context Capture

### Automatic Detection
The extension automatically captures:

```python
# Project structure
workspace_context = {
    "project_type": detect_project_type(),      # python, node, etc.
    "framework": detect_framework(),            # django, react, etc.
    "git_branch": get_current_branch(),         # current branch
    "recent_files": get_recent_files(),         # recently edited files
    "open_files": get_open_files(),             # currently open tabs
    "current_file": get_active_file(),          # focused file
    "cursor_position": get_cursor_position(),   # line/column
    "selection": get_current_selection(),       # selected text
}
```

### Smart Context Updates
Context automatically updates as you work:

```python
# File changes update context
on_file_change(file_path):
    context.add_file_activity(file_path)
    context.update_current_file(file_path)

# Git operations update context  
on_git_branch_change(branch):
    context.update_git_branch(branch)
    context.update_goal(f"Working on branch: {branch}")

# Test runs update context
on_test_execution(results):
    context.add_test_results(results)
    if results.failed:
        context.update_goal("Fix failing tests")
```

## Agent Workflow Examples

### 1. Debug Test Failure
```typescript
// Agent workflow using OCP in VS Code
async function debugTestFailure() {
    // 1. Get workspace context
    const context = await vscode.commands.executeCommand('ocp.createContext');
    
    // 2. Discover relevant APIs
    const github = await ocp.discoverTools('github');
    
    // 3. Search for similar issues with workspace context
    const issues = await github.searchIssues({
        q: `repo:${context.workspace} ${context.currentFile} test failure`,
        sort: 'updated',
        order: 'desc'
    });
    
    // 4. Analyze recent commits
    const commits = await github.listCommits({
        owner: context.gitOwner,
        repo: context.workspace,
        path: context.currentFile
    });
    
    return {
        similarIssues: issues.items,
        recentChanges: commits,
        recommendations: generateRecommendations(issues, commits, context)
    };
}
```

### 2. Deploy with Context
```typescript
async function deployWithContext() {
    // 1. Get current workspace state
    const context = await vscode.commands.executeCommand('ocp.createContext');
    
    // 2. Discover deployment tools
    const aws = await ocp.discoverTools('aws');
    const github = await ocp.discoverTools('github');
    
    // 3. Check deployment status with context
    const deployment = await aws.describeServices({
        cluster: `${context.workspace}-cluster`,
        serviceName: context.workspace
    });
    
    // 4. Create deployment record
    const release = await github.createRelease({
        owner: context.gitOwner,
        repo: context.workspace,
        tag_name: `v${context.version}`,
        name: `Release ${context.version}`,
        body: `Deployed from branch: ${context.gitBranch}\nFiles: ${context.recentFiles.join(', ')}`
    });
    
    return { deployment, release };
}
```

### 3. Code Review with Context
```typescript
async function contextAwareCodeReview() {
    const context = await vscode.commands.executeCommand('ocp.createContext');
    const github = await ocp.discoverTools('github');
    
    // Get PR context
    const pulls = await github.listPullRequests({
        owner: context.gitOwner,
        repo: context.workspace,
        head: `${context.gitOwner}:${context.gitBranch}`,
        state: 'open'
    });
    
    if (pulls.length === 0) {
        // Create PR with context
        return await github.createPullRequest({
            owner: context.gitOwner,
            repo: context.workspace,
            title: `Fix: ${context.currentGoal}`,
            body: `
## Context
- **Branch**: ${context.gitBranch}
- **Files Modified**: ${context.recentFiles.join(', ')}
- **Goal**: ${context.currentGoal}

## Changes
${generateChangeDescription(context)}
            `,
            head: context.gitBranch,
            base: 'main'
        });
    }
    
    return pulls[0];
}
```

## Multi-Agent Coordination

### Shared Context
Multiple agents can share context in the same workspace:

```typescript
// Agent A: Code analysis
const context = await ocp.createContext();
context.addInsight("Found performance bottleneck in payment_validator.py:45");

// Agent B: Issue tracking  
const github = await ocp.discoverTools('github');
const issue = await github.createIssue({
    title: "Performance issue in payment validation",
    body: `Context: ${context.currentGoal}\nFile: ${context.currentFile}\nLine: 45`
});

// Agent C: Documentation
context.addTask("Document performance fix in README");
```

### Workflow Orchestration
```typescript
class OCPWorkflow {
    async runDeploymentWorkflow() {
        const context = await this.createContext();
        
        // Step 1: Run tests
        await this.runTests(context);
        
        // Step 2: Build
        await this.buildProject(context);
        
        // Step 3: Deploy
        await this.deploy(context);
        
        // Step 4: Notify team
        await this.notifyDeployment(context);
    }
}
```

## Configuration & Setup

### API Authentication
```json
{
    "ocp.apis": {
        "github": {
            "authentication": {
                "type": "bearer",
                "token": "${GITHUB_TOKEN}"
            }
        },
        "aws": {
            "authentication": {
                "type": "aws_credentials",
                "profile": "default"
            }
        },
        "stripe": {
            "authentication": {
                "type": "bearer", 
                "token": "${STRIPE_SECRET_KEY}"
            }
        }
    }
}
```

### Workspace Settings
```json
{
    "ocp.workspace": {
        "auto_context": true,
        "context_refresh_interval": 30000,
        "include_git_info": true,
        "include_recent_files": true,
        "max_context_history": 50
    }
}
```

## Cross-Agent Compatibility

The extension works with any AI agent or chat interface:

### GitHub Copilot
```typescript
// Copilot can use OCP commands
await vscode.commands.executeCommand('ocp.createContext');
```

### Cursor AI
```typescript
// Cursor integration
const context = await cursor.ocp.getContext();
```

### Custom Agents
```typescript
// Custom agent integration
class MyAgent {
    async initialize() {
        this.ocp = await import('@opencontextprotocol/vscode');
        this.context = await this.ocp.createContext();
    }
}
```

## Key Benefits

**🔄 Automatic Context**: Workspace state flows to agents without manual setup  
**🛠️ Instant Tools**: Any API becomes immediately available to agents  
**🎯 Goal Awareness**: Agents understand what you're working on  
**📁 File Context**: Current files, recent changes, git branch all included  
**🤝 Multi-Agent**: Multiple agents can coordinate using shared context  
**⚡ Zero Config**: Drop-in installation with automatic workspace detection

## Next Steps

Now that you understand IDE integration, explore the foundational OCP superpowers:

{{< cards >}}
{{< card link="../context/" title="🧠 Context" subtitle="Understand how workspace context is captured and used" >}}
{{< card link="../tools/" title="🔧 Tool Discovery" subtitle="See how APIs become instantly available in your IDE" >}}
{{< card link="../registry/" title="🌐 Community Registry" subtitle="Browse thousands of APIs from within VS Code" >}}
{{< /cards >}}

**Ready to install?** [Get the VS Code Extension →](vscode-extension/)