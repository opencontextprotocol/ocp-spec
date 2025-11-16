---
title: "Context"
weight: 2
cascade:
  type: docs
---

The first OCP superpower transforms APIs from stateless endpoints into **conversational participants** in your agent workflow. Instead of losing context between calls, APIs become aware of the ongoing conversation, workspace, and goals.

## The Problem OCP Solves

**Before OCP:**
```python
# Agent loses context between calls
issues = github.get_issues()  # No context about what we're debugging
commits = github.get_commits()  # No memory of previous issue search  
files = github.get_files()     # No connection to overall goal
```

**With OCP:**
```python
# Context flows automatically across all calls
agent = OCPAgent(goal="debug_payment_failure", workspace="ecommerce-app")
issues = github.get_issues()     # Context: debugging payment in ecommerce-app
commits = github.get_commits()   # Context: previous issue search + goal
files = github.get_files()       # Context: full conversation history
```

## How Context Works

Context flows through **standard HTTP headers** - no servers, no infrastructure, no API modifications required.

### Context Headers

{{< cards >}}
{{< card link="headers/" title="HTTP Headers" subtitle="Required and optional headers for context transmission" >}}
{{< card link="schema/" title="Context Schema" subtitle="JSON structure for agent context objects" >}}
{{< card link="encoding/" title="Encoding & Compression" subtitle="Base64 encoding, compression, and size limits" >}}
{{< card link="examples/" title="Context Examples" subtitle="Real-world context usage patterns" >}}
{{< /cards >}}

## Context Levels

### Level 1: Context Awareness (Available Today)
APIs receive context headers but don't modify behavior. Your agent maintains context client-side.

```http
GET /repos/owner/project/issues HTTP/1.1
Host: api.github.com
OCP-Context-ID: ctx-debug-payment
OCP-Current-Goal: debug_payment_failure
OCP-Workspace: ecommerce-app
```

### Level 2: Context Enhancement (Future)
APIs read context and provide enhanced, context-aware responses.

```json
{
  "issues": [...],
  "ocp_context_match": {
    "relevance": "high",
    "matching_factors": ["payment", "failure", "ecommerce"],
    "suggested_next_actions": [
      "Check recent payment processor changes",
      "Review error logs in payment service"
    ]
  }
}
```

## Key Benefits

**🔄 Persistent Memory**: Context survives across API calls and sessions  
**🎯 Goal Awareness**: APIs understand what you're trying to accomplish  
**🏢 Workspace Context**: File paths, git branches, project structure flow automatically  
**📊 Interaction History**: Track conversation flow and API usage patterns  
**🔧 Zero Setup**: Works with existing APIs - no server changes required

## Next Steps

Now that you understand how context works, explore the other OCP superpowers:

{{< cards >}}
{{< card link="../tools/" title="Tool Discovery" subtitle="Learn how OCP automatically generates tools from any API" icon="cog" >}}
{{< card link="../registry/" title="Community Registry" subtitle="Discover pre-indexed APIs for instant integration" icon="collection" >}}
{{< card link="../ide/" title="IDE Integration" subtitle="Install the VS Code extension for workspace-aware agents" icon="code" >}}
{{< /cards >}}

**Ready to start?** [Get Started with Context →](headers/)