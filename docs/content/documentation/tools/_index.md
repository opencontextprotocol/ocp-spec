---
title: "Tool Discovery"
weight: 3
cascade:
  type: docs
---

The second OCP superpower eliminates manual API integration forever. Point to any OpenAPI specification and instantly get **callable agent tools** with parameter validation, request building, and response parsing.

## The Problem OCP Solves

**Before OCP:**
```python
# Manual integration for every API
def github_create_issue(owner, repo, title, body=None):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    headers = {"Authorization": f"Bearer {token}"}
    data = {"title": title}
    if body:
        data["body"] = body
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def stripe_create_customer(email, name=None):
    # Another manual integration...
    
# Repeat for hundreds of APIs...
```

**With OCP:**
```python
# Instant tool generation from OpenAPI specs
github = ocp.discover_tools("https://api.github.com/openapi.json")
stripe = ocp.discover_tools("stripe")  # From registry

# Tools are now callable with validation
issue = github.create_issue(owner="myorg", repo="project", title="Bug report")
customer = stripe.create_customer(email="alice@example.com")
```

## How Tool Discovery Works

OCP's schema discovery engine automatically parses OpenAPI specifications and generates callable tools with full parameter validation.

### Discovery Components

{{< cards >}}
{{< card link="openapi-parsing/" title="OpenAPI Parsing" subtitle="How OCP processes OpenAPI specifications into tools" >}}
{{< card link="tool-generation/" title="Tool Generation" subtitle="Converting operations into callable functions" >}}
{{< card link="naming-conventions/" title="Naming Conventions" subtitle="Deterministic tool naming and organization" >}}
{{< card link="parameter-validation/" title="Parameter Validation" subtitle="Automatic validation against OpenAPI schemas" >}}
{{< card link="response-handling/" title="Response Handling" subtitle="Response parsing and schema validation" >}}
{{< /cards >}}

## Quick Start

### From URL
```python
import ocp

# Point to any OpenAPI spec
api = ocp.discover_tools("https://api.github.com/openapi.json")

# List available tools
print(f"Discovered {len(api.tools)} tools")
for tool in api.tools[:5]:
    print(f"  {tool.name}: {tool.description}")
```

### From Registry
```python
# Use pre-indexed APIs (faster)
github = ocp.discover_tools("github")
stripe = ocp.discover_tools("stripe")
slack = ocp.discover_tools("slack")

# Tools are immediately available
repos = github.list_user_repositories()
```

### Search & Filter Tools
```python
# Search for specific functionality
payment_tools = stripe.search_tools("payment")
issue_tools = github.search_tools("issue")
user_tools = github.get_tools_by_tag("users")
```

## Tool Structure

Every discovered tool includes:

```python
@dataclass
class OCPTool:
    name: str                    # Deterministic function name
    description: str             # Human-readable description
    method: str                  # HTTP method (GET, POST, etc.)
    path: str                    # API endpoint path
    parameters: Dict[str, Any]   # Parameter schema with validation
    response_schema: Dict[str, Any]  # Expected response structure
    operation_id: Optional[str]  # Original OpenAPI operation ID
    tags: List[str]              # OpenAPI tags for organization
```

## Tool Generation Flow

1. **Fetch OpenAPI Spec** → Download and cache specification
2. **Parse Operations** → Extract HTTP operations from paths
3. **Generate Names** → Create deterministic function names
4. **Extract Parameters** → Parse query, path, and body parameters
5. **Build Tools** → Create callable functions with validation
6. **Cache Results** → Store for future use

## Integration Examples

### GitHub API
```python
# Discover GitHub tools
github = ocp.discover_tools("github")

# List repositories
repos = github.list_user_repositories()

# Create an issue with validation
issue = github.create_issue(
    owner="myorg",           # Required
    repo="myproject",        # Required  
    title="Bug in payment",  # Required
    body="Payment fails...", # Optional
    labels=["bug", "urgent"] # Optional
)

# Get issue with type safety
issue_detail = github.get_issue(owner="myorg", repo="myproject", issue_number=123)
```

### Stripe API  
```python
# Discover Stripe tools
stripe = ocp.discover_tools("stripe")

# Create customer
customer = stripe.create_customer(
    email="alice@example.com",
    name="Alice Johnson"
)

# Create payment intent
payment = stripe.create_payment_intent(
    amount=2000,  # $20.00
    currency="usd",
    customer=customer.id
)
```

## Key Benefits

**🚀 Zero Manual Integration**: Any OpenAPI spec becomes instant tools  
**✅ Automatic Validation**: Parameters validated against schemas  
**📚 Self-Documenting**: Tools include descriptions and examples  
**🎯 Deterministic Naming**: Consistent function names across APIs  
**⚡ Fast Discovery**: Registry provides pre-cached specifications  
**🔧 Type Safety**: Full parameter and response validation

## Next Steps

Now that you understand tool discovery, explore how it works with other OCP superpowers:

{{< cards >}}
{{< card link="../context/" title="Context" subtitle="See how context flows through your generated tools" icon="chat" >}}
{{< card link="../registry/" title="Community Registry" subtitle="Discover thousands of pre-indexed APIs instantly" icon="collection" >}}
{{< card link="../ide/" title="IDE Integration" subtitle="Use tools directly in your VS Code workflow" icon="code" >}}
{{< /cards >}}

**Ready to generate tools?** [Start with OpenAPI Parsing →](openapi-parsing/)