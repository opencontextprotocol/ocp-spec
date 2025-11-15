---
title: "Community Registry"
weight: 3
cascade:
  type: docs
---

The third OCP superpower eliminates the need to find and configure OpenAPI specifications. The community registry provides **pre-indexed APIs** that are searchable by both users and agents for instant tool discovery.

## The Problem OCP Solves

**Before OCP:**
```python
# Manual API discovery and configuration
# 1. Find the right API
# 2. Locate OpenAPI specification
# 3. Figure out authentication
# 4. Debug specification issues

github_spec = "https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.json"
stripe_spec = "https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json"

# Hope these URLs still work...
tools = ocp.discover_tools(github_spec)
```

**With OCP Registry:**
```python
# Instant discovery by name
github = ocp.discover_tools("github")    # Instant
stripe = ocp.discover_tools("stripe")    # No URLs needed
slack = ocp.discover_tools("slack")      # Pre-verified specs

# Or search for APIs
payment_apis = ocp.search_apis("payment")
auth_apis = ocp.search_apis("authentication")
```

## How the Registry Works

The community registry provides a curated, searchable database of API specifications with metadata, examples, and verification status.

### Registry Components

{{< cards >}}
{{< card link="api-catalog/" title="API Catalog" subtitle="Browse and discover available APIs by category and functionality" >}}
{{< card link="search-discovery/" title="Search & Discovery" subtitle="Powerful search capabilities for finding the right APIs" >}}
{{< card link="pre-indexing/" title="Pre-indexing" subtitle="How APIs are cached and optimized for instant access" >}}
{{< card link="contributing/" title="Contributing APIs" subtitle="How to add new APIs to the community registry" >}}
{{< card link="registry-api/" title="Registry API" subtitle="Programmatic access to registry data and search" >}}
{{< /cards >}}

## Quick Start

### Search for APIs
```python
import ocp

# Search by functionality
results = ocp.search_apis("payment")
# Returns: [
#   {"name": "stripe", "description": "Online payment processing", "category": "payments"},
#   {"name": "paypal", "description": "Digital payments platform", "category": "payments"},
#   {"name": "square", "description": "Payment processing for businesses", "category": "payments"}
# ]

# Search by category
dev_tools = ocp.search_apis(category="developer-tools")
communication = ocp.search_apis(category="communication")
```

### Instant Tool Discovery
```python
# Pre-cached, verified specifications
github = ocp.discover_tools("github")      # GitHub REST API
stripe = ocp.discover_tools("stripe")      # Stripe API
slack = ocp.discover_tools("slack")        # Slack Web API
twilio = ocp.discover_tools("twilio")      # Twilio API
openai = ocp.discover_tools("openai")      # OpenAI API

# Tools are immediately available
repos = github.list_user_repositories()
customer = stripe.create_customer(email="alice@example.com")
message = slack.post_message(channel="#general", text="Hello!")
```

### Browse by Category
```python
# Get all APIs in a category
payment_apis = ocp.get_apis_by_category("payments")
developer_apis = ocp.get_apis_by_category("developer-tools")
communication_apis = ocp.get_apis_by_category("communication")

# Discover tools for all APIs in category
for api_info in payment_apis:
    api_tools = ocp.discover_tools(api_info["name"])
    print(f"{api_info['name']}: {len(api_tools.tools)} tools")
```

## Registry Benefits

### 🚀 Instant Access
- **No URL hunting**: Find APIs by name or functionality
- **Pre-cached specs**: Zero download time for popular APIs
- **Verified quality**: Community-tested OpenAPI specifications

### 🔍 Powerful Discovery
- **Text search**: Find APIs by description, functionality, or keywords
- **Category browsing**: Explore APIs by use case (payments, communication, etc.)
- **Similarity search**: Find alternatives to known APIs

### ✅ Quality Assurance
- **Verified specs**: OpenAPI specifications tested for completeness
- **Tool validation**: Generated tools verified to work correctly
- **Community feedback**: Ratings and reviews from developers

### 📊 Rich Metadata
- **Usage examples**: Sample code for common operations
- **Authentication guides**: Setup instructions for each API
- **Rate limits**: Known limitations and best practices

## Registry Structure

### API Entry Format
```json
{
  "name": "github",
  "title": "GitHub REST API",
  "description": "GitHub's REST API for repository management and automation",
  "category": "developer-tools",
  "subcategory": "version-control",
  "version": "1.1.4",
  "spec_url": "https://api.github.com/openapi.json",
  "base_url": "https://api.github.com",
  "documentation_url": "https://docs.github.com/en/rest",
  "authentication": {
    "types": ["bearer", "oauth"],
    "required": true,
    "docs": "https://docs.github.com/en/authentication"
  },
  "popularity": {
    "downloads": 150000,
    "rating": 4.8,
    "reviews": 1205
  },
  "metadata": {
    "tool_count": 847,
    "last_updated": "2025-11-15T10:00:00Z",
    "verified": true,
    "examples_available": true
  },
  "tags": ["git", "repository", "ci-cd", "collaboration", "open-source"]
}
```

### Category Organization
```
developer-tools/
├── version-control/     (github, gitlab, bitbucket)
├── ci-cd/              (jenkins, travis-ci, github-actions)
├── monitoring/         (datadog, newrelic, sentry)
└── testing/            (browserstack, sauce-labs)

communication/
├── messaging/          (slack, discord, teams)
├── email/             (sendgrid, mailgun, ses)
└── video/             (zoom, twilio-video)

payments/
├── processors/        (stripe, paypal, square)
├── crypto/           (coinbase, binance)
└── banking/          (plaid, yodlee)

cloud/
├── aws/              (aws-ec2, aws-s3, aws-lambda)
├── azure/            (azure-compute, azure-storage)
└── gcp/              (gcp-compute, gcp-storage)
```

## Registry API

### Search Operations
```python
# Text search across all fields
results = ocp.registry.search("payment processing")

# Category filtering
payment_apis = ocp.registry.search("", category="payments")

# Advanced filtering
enterprise_apis = ocp.registry.search("", 
    category="enterprise",
    verified=True,
    min_rating=4.0
)
```

### API Metadata
```python
# Get detailed API information
api_info = ocp.registry.get_api("github")

# Get specification directly
spec = ocp.registry.get_spec("github")

# Get usage examples
examples = ocp.registry.get_examples("github")
```

### Discovery Integration
```python
# Registry-aware discovery
def discover_tools_smart(query):
    """Discover tools with fallback to registry"""
    
    # Try as registry name first
    if ocp.registry.has_api(query):
        return ocp.discover_tools(query)
    
    # Try as URL
    if query.startswith("http"):
        return ocp.discover_tools_from_url(query)
    
    # Search registry
    results = ocp.registry.search(query)
    if results:
        return ocp.discover_tools(results[0]["name"])
    
    raise ValueError(f"No API found for: {query}")
```

## Registry Configuration

### Default Registry
```python
# Use official community registry (default)
ocp.set_registry("https://registry.ocp.dev")

# Check registry status
status = ocp.registry.health()
print(f"Registry: {status['name']} ({status['api_count']} APIs)")
```

### Private Registry
```python
# Use private company registry
ocp.set_registry("https://api-registry.company.com")

# Multiple registries
ocp.add_registry("https://registry.ocp.dev")         # Community
ocp.add_registry("https://internal.company.com")    # Internal

# Search across all registries
results = ocp.search_apis("payment", search_all=True)
```

### Offline Mode
```python
# Disable registry (direct URLs only)
ocp.disable_registry()

# Use cached registry data only
ocp.set_registry_mode("offline")
```

## Key Benefits

**⚡ Instant Discovery**: No URL hunting or specification debugging  
**🔍 Smart Search**: Find APIs by functionality, not just name  
**✅ Quality Verified**: Community-tested and validated specifications  
**📚 Rich Metadata**: Authentication, examples, and usage guides included  
**🌍 Community Driven**: Collaborative API catalog maintained by developers  
**🏢 Enterprise Ready**: Support for private registries and offline usage

## Next Steps

Now that you understand the registry, see how it integrates with other OCP superpowers:

{{< cards >}}
{{< card link="/tools/" title="🔧 Tool Discovery" subtitle="See how registry accelerates tool generation" >}}
{{< card link="/context/" title="🧠 Context" subtitle="Learn how context enhances API interactions" >}}
{{< card link="/ide/" title="💻 IDE Integration" subtitle="Use registry APIs directly in your development workflow" >}}
{{< /cards >}}

**Ready to explore APIs?** [Browse the API Catalog →](api-catalog/)