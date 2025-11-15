---
title: Getting Started
weight: 1
cascade:
  type: docs
---

Welcome to the **Open Context Protocol** - the revolutionary way to turn any API into an intelligent agent tool with persistent context.

## The 4 Superpowers

OCP transforms agent-API interactions through four breakthrough capabilities that work together:

{{< hextra/feature-grid >}}
{{< hextra/feature-card title="🧠 Context" subtitle="APIs become conversational participants with persistent memory across calls" link="/context/" >}}
{{< hextra/feature-card title="🔧 Tool Discovery" subtitle="Instant tool generation from any OpenAPI specification - zero manual work" link="/tools/" >}}
{{< hextra/feature-card title="🌐 Registry" subtitle="Pre-indexed API catalog searchable by users and agents" link="/registry/" >}}
{{< hextra/feature-card title="💻 IDE Integration" subtitle="Drop-in VS Code extension for workspace-aware agents" link="/ide/" >}}
{{< /hextra/feature-grid >}}

## What Makes OCP Revolutionary?

### ❌ **The Old Way**
```python
# Manual integration hell
def github_create_issue(owner, repo, title):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"title": title}
    response = requests.post(f"https://api.github.com/repos/{owner}/{repo}/issues", 
                           headers=headers, json=data)
    return response.json()

# Context lost between calls  
issues = github_list_issues()      # No context
commits = github_list_commits()    # No memory
files = github_list_files()        # No connection
```

### ✅ **The OCP Way**
```python
# Instant tool discovery + persistent context
agent = ocp.Agent(goal="debug_payment_error", workspace="ecommerce-app")
github = agent.discover_tools("github")  # 800+ tools instantly

# Context flows automatically across all calls
issues = github.search_issues(q="payment")    # Context: debugging payment in ecommerce-app
commits = github.list_commits()               # Context: previous search + goal  
files = github.get_contents(path="payment/")  # Context: full conversation history
```

## Quick Setup

{{< tabs items="Python,JavaScript,VS Code" >}}

{{< tab >}}
```bash
pip install ocp-python
```

```python
import ocp

agent = ocp.Agent(workspace="my-project")
github = agent.discover_tools("github")
print(f"✅ {len(github.tools)} tools ready!")
```
{{< /tab >}}

{{< tab >}}
```bash
npm install @opencontextprotocol/agent
```

```javascript
import { Agent } from '@opencontextprotocol/agent';

const agent = new Agent({workspace: "my-project"});
const github = await agent.discoverTools("github");
console.log(`✅ ${github.tools.length} tools ready!`);
```
{{< /tab >}}

{{< tab >}}
```bash
ext install opencontextprotocol.ocp-vscode
```

Open VS Code → Extension detects workspace → Agents get instant context + API access
{{< /tab >}}

{{< /tabs >}}

## Your Learning Path

Choose your starting point based on what you want to accomplish:

{{< cards >}}
{{< card link="installation/" title="📦 Installation" subtitle="Set up OCP in your environment" >}}
{{< card link="quick-start/" title="⚡ Quick Start" subtitle="Working example in 5 minutes" >}}
{{< card link="learning-paths/" title="🎓 Learning Paths" subtitle="Guided journey by user type" >}}
{{< /cards >}}

## Next Steps

**Ready to see OCP in action?** → [⚡ Quick Start](quick-start/)  
**Want to understand the foundation?** → [🧠 Context](/context/)  
**Need to set up your environment first?** → [📦 Installation](installation/)

---

{{< callout type="info" >}}
**💡 Pro Tip**: The 4 superpowers are most powerful when used together. Context makes your tools smarter, Registry makes discovery instant, and IDE Integration brings everything into your workflow.
{{< /callout >}}