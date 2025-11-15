---
title: Examples
weight: 6
cascade:
  type: docs
---

# Examples: OCP Superpowers in Action

Real-world examples demonstrating how OCP's four superpowers work together to create powerful agent workflows.

## The 4 Superpowers Working Together

Each example showcases multiple OCP capabilities:
- 🧠 **Context**: Persistent state across API calls
- 🔧 **Tool Discovery**: Automatic API integration  
- 🌐 **Registry**: Instant API access
- 💻 **IDE Integration**: Workspace-aware agents

## Complete Workflows

{{< cards >}}
{{< card link="debug-workflow/" title="Debug Test Failure" subtitle="Complete debugging workflow from test failure to fix deployment" >}}
{{< card link="feature-development/" title="Feature Development" subtitle="End-to-end feature development with API integration" >}}
{{< card link="deployment-pipeline/" title="Deployment Pipeline" subtitle="Automated deployment with context-aware monitoring" >}}
{{< card link="issue-triage/" title="Issue Triage" subtitle="Intelligent issue analysis with multi-API coordination" >}}
{{< /cards >}}

## Quick Examples by Superpower

### 🧠 Context Examples
{{< cards >}}
{{< card link="context-examples/" title="Context Patterns" subtitle="Common context usage patterns and evolution" >}}
{{< /cards >}}

### 🔧 Tool Discovery Examples  
{{< cards >}}
{{< card link="tool-examples/" title="API Integration" subtitle="Automatic tool generation from various APIs" >}}
{{< /cards >}}

### 🌐 Registry Examples
{{< cards >}}
{{< card link="registry-examples/" title="API Discovery" subtitle="Finding and using APIs from the community registry" >}}
{{< /cards >}}

### 💻 IDE Examples
{{< cards >}}
{{< card link="ide-examples/" title="VS Code Workflows" subtitle="Agent workflows within VS Code environment" >}}
{{< /cards >}}

## Getting Started

### 1. Basic Setup
```python
import ocp

# Create agent with workspace context
agent = ocp.Agent(
    agent_type="debugging_assistant",
    workspace="my-project",
    goal="investigate_performance_issue"
)

# Discover tools from registry (instant)
github = agent.discover_tools("github")
datadog = agent.discover_tools("datadog") 
aws = agent.discover_tools("aws")
```

### 2. Context Flows Automatically
```python
# All API calls include context automatically
issues = github.search_issues(
    q="performance slow",
    repo="my-project"
)  # Context: goal=investigate_performance_issue, workspace=my-project

metrics = datadog.query_metrics(
    query="avg:system.cpu.idle{*}",
    from_time="-1h"
)  # Context: investigating performance + previous issue search

logs = aws.filter_log_events(
    log_group_name="/aws/lambda/my-project",
    filter_pattern="ERROR"
)  # Context: performance investigation + metrics + issues
```

### 3. Multi-API Workflows
```python
# Agents coordinate across multiple APIs with shared context
workflow = agent.create_workflow([
    ("github", "search_issues"),          # Find related issues
    ("datadog", "get_performance_data"),  # Get metrics
    ("aws", "check_infrastructure"),      # Check AWS status
    ("slack", "notify_team")              # Report findings
])

results = await workflow.execute()
```

## Real-World Scenarios

### Debugging Production Issue
```python
async def debug_production_issue():
    """Complete debugging workflow with context awareness"""
    
    # 1. Agent starts with VS Code context
    agent = ocp.Agent.from_vscode()  # Gets workspace, current file, git branch
    
    # 2. Discover relevant tools
    github = agent.discover_tools("github")
    datadog = agent.discover_tools("datadog")
    pagerduty = agent.discover_tools("pagerduty")
    
    # 3. Context-aware investigation
    incidents = pagerduty.list_incidents(
        service_ids=[agent.workspace.service_id],
        since=agent.context.session_start
    )
    
    metrics = datadog.query_metrics(
        query=f"avg:error_rate{{service:{agent.workspace.name}}}",
        from_time="-2h"
    )
    
    # 4. Correlate with code changes
    recent_commits = github.list_commits(
        owner=agent.workspace.owner,
        repo=agent.workspace.name,
        since=incidents[0].created_at,
        path=agent.context.current_file
    )
    
    # 5. Generate investigation report
    return {
        "incident": incidents[0],
        "error_metrics": metrics,
        "suspicious_commits": recent_commits,
        "recommended_actions": generate_recommendations(incidents, metrics, recent_commits)
    }
```

### Feature Development Flow
```python
async def develop_payment_feature():
    """End-to-end feature development with API integration"""
    
    agent = ocp.Agent(
        workspace="ecommerce-app",
        goal="implement_stripe_integration"
    )
    
    # 1. Research existing implementations
    github = agent.discover_tools("github")
    similar_repos = github.search_repositories(
        q="stripe payment integration language:python",
        sort="stars"
    )
    
    # 2. Explore Stripe API
    stripe = agent.discover_tools("stripe")
    payment_tools = stripe.search_tools("payment")
    
    # 3. Create feature branch
    branch = github.create_branch(
        owner=agent.workspace.owner,
        repo=agent.workspace.name,
        branch=f"feature/stripe-integration-{agent.context.id}"
    )
    
    # 4. Implement with context
    implementation = {
        "payment_methods": stripe.list_payment_methods(),
        "integration_examples": extract_examples(similar_repos),
        "test_customers": stripe.create_test_customer(),
        "branch": branch
    }
    
    # 5. Create pull request with context
    pr = github.create_pull_request(
        title="Add Stripe Payment Integration",
        body=f"""
## Context
- **Goal**: {agent.context.current_goal}  
- **Research**: Analyzed {len(similar_repos)} similar implementations
- **API Tools**: {len(payment_tools)} Stripe tools available

## Implementation
{generate_implementation_summary(implementation)}
        """,
        head=branch.name,
        base="main"
    )
    
    return implementation
```

## Integration Patterns

### Error Handling with Context
```python
def handle_api_error_with_context(error, context):
    """Context-aware error handling"""
    
    error_context = {
        "error": str(error),
        "current_goal": context.current_goal,
        "api_sequence": context.get_recent_api_calls(),
        "workspace": context.workspace
    }
    
    # Log with context for better debugging
    logger.error("API error in context", extra=error_context)
    
    # Suggest recovery actions based on context
    if "authentication" in str(error).lower():
        return suggest_auth_fix(context.workspace)
    elif "rate_limit" in str(error).lower():
        return suggest_backoff_strategy(context.get_api_usage())
    else:
        return suggest_general_recovery(error_context)
```

### Cross-API Data Flow
```python
async def cross_api_workflow():
    """Data flows between APIs with persistent context"""
    
    # 1. Get user data from one API
    github_user = github.get_authenticated_user()
    
    # 2. Context automatically includes user info
    # Next API call has context about github user
    slack_profile = slack.get_user_profile(
        user=github_user.login  # Context helps map identities
    )
    
    # 3. Use combined data for personalized actions
    notification = slack.post_message(
        channel="#dev",
        text=f"🚀 {github_user.name} deployed {context.workspace} to production!"
    )
    
    # 4. Context tracks the complete interaction chain
    return {
        "github_user": github_user,
        "slack_profile": slack_profile, 
        "notification": notification,
        "interaction_chain": context.history
    }
```

## Testing with OCP

### Context-Aware Testing
```python
def test_with_context():
    """Test API workflows with context"""
    
    # Create test context
    test_context = ocp.Context(
        agent_type="test_runner",
        workspace="test-project",
        goal="integration_testing"
    )
    
    # Test with context
    api = ocp.discover_tools("github", context=test_context)
    
    # Verify context is included in requests
    with mock.patch('requests.request') as mock_request:
        api.list_repositories()
        
        # Verify OCP headers were sent
        args, kwargs = mock_request.call_args
        headers = kwargs['headers']
        assert 'OCP-Context-ID' in headers
        assert headers['OCP-Agent-Type'] == 'test_runner'
        assert 'OCP-Session' in headers
```

### Mock Registry for Testing
```python
def test_with_mock_registry():
    """Test with mock registry for isolated testing"""
    
    mock_registry = {
        "test-api": {
            "spec_url": "file://./test-api-spec.json",
            "title": "Test API",
            "tools": ["get_data", "post_data"]
        }
    }
    
    with ocp.mock_registry(mock_registry):
        api = ocp.discover_tools("test-api")
        assert len(api.tools) == 2
        assert "get_data" in [t.name for t in api.tools]
```