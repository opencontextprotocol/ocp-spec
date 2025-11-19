---
title: Documentation
---

OCP turns any API into an intelligent agent tool with persistent context.

## Core Features

{{< cards >}}
{{< card title="Tool Discovery" subtitle="Auto-generate tools from OpenAPI specs" link="tools/" icon="cog" >}}
{{< card title="HTTP Context" subtitle="Persistent state across API calls" link="context/" icon="chat" >}}
{{< card title="Marketplace" subtitle="Pre-indexed API catalog" link="registry/" icon="collection" >}}
{{< card title="IDE Integration" subtitle="Workspace-aware agents" link="ide/" icon="code" >}}
{{< /cards >}}

## How It Works

**Without OCP:** Manual API integration, no context between calls
```python
# Isolated calls
issues = github_list_issues()      # No context
commits = github_list_commits()    # No memory  
files = github_list_files()        # No connection
```

**With OCP:** Instant tools + persistent context
```python
# Context flows automatically
agent = ocp.Agent(goal="debug_payment_error", workspace="ecommerce-app")
github = agent.discover_tools("github")  # 800+ tools instantly

issues = github.search_issues(q="payment")    # Context: debugging payment
commits = github.list_commits()               # Context: previous search + goal
files = github.get_contents(path="payment/")   # Context: full history
```

## Next

Dive into the following section to begin using OCP:

{{< cards >}}
{{< card link="getting-started/" title="Getting Started" subtitle="Setup and first usage" icon="play" >}}
{{< /cards >}}