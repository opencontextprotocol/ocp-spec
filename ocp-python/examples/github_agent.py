#!/usr/bin/env python3
"""
GitHub Agent Example - Demonstrates OCP with GitHub API.

Shows how OCP enables intelligent GitHub interactions by providing
agent context that helps GitHub understand what the agent is working on.
"""

import os
import sys
from typing import Optional

# Add src to path for running examples directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ocp import AgentContext, wrap_api


def create_github_client(token: str, context: AgentContext):
    """Create an OCP-enabled GitHub API client."""
    return wrap_api(
        "https://api.github.com",
        context,
        auth=f"token {token}"
    )


def demo_debug_workflow():
    """
    Demonstrate debugging workflow with OCP context.
    
    This shows how agent context makes GitHub API responses more intelligent.
    """
    print("🔍 GitHub Debug Assistant Demo")
    print("=" * 50)
    
    # Get GitHub token
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ Please set GITHUB_TOKEN environment variable")
        return
    
    # Create debugging context
    context = AgentContext(
        agent_type="debug_assistant",
        user="developer",
        workspace="payment-service",
        current_file="test_payment.py"
    )
    
    # Set up the debugging scenario
    context.set_error_context(
        "AssertionError: Expected 200, got 500 in test_payment_refund",
        "test_payment.py"
    )
    context.add_recent_change("Modified payment_processor.py")
    context.update_goal("debug_test_failure", "Payment refund test failing with 500 error")
    
    # Create GitHub client
    github = create_github_client(token, context)
    
    print(f"📋 Context Summary: {context.get_conversation_summary()}")
    print()
    
    # Search for related issues - OCP context helps GitHub understand what we need
    print("🔎 Searching for related issues...")
    try:
        response = github.get("/search/issues", params={
            "q": "payment test failure refund 500 error",
            "per_page": 3
        })
        
        if response.status_code == 200:
            issues = response.json()
            print(f"✅ Found {issues['total_count']} related issues")
            
            for issue in issues['items'][:3]:
                print(f"  • #{issue['number']}: {issue['title']}")
                print(f"    {issue['html_url']}")
            
            # Log this interaction
            context.add_interaction(
                "searched_issues",
                "GET /search/issues", 
                f"Found {issues['total_count']} results"
            )
        else:
            print(f"❌ GitHub API error: {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Get repository info - context helps identify the right repo
    print("📊 Getting repository information...")
    try:
        response = github.get("/user/repos", params={
            "type": "owner",
            "sort": "updated",
            "per_page": 5
        })
        
        if response.status_code == 200:
            repos = response.json()
            print(f"✅ Found {len(repos)} recent repositories")
            
            for repo in repos:
                print(f"  • {repo['name']} - {repo.get('description', 'No description')}")
                
            context.add_interaction(
                "listed_repos",
                "GET /user/repos",
                f"Retrieved {len(repos)} repositories"
            )
        else:
            print(f"❌ GitHub API error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("🎯 Demo completed! Context history:")
    for i, interaction in enumerate(context.history, 1):
        print(f"  {i}. {interaction['action']} -> {interaction.get('result', 'N/A')}")
    
    return context


def demo_issue_creation():
    """
    Demonstrate creating a GitHub issue with rich OCP context.
    """
    print("\n🆕 Creating Issue with OCP Context")
    print("=" * 50)
    
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ Please set GITHUB_TOKEN environment variable")
        return
    
    # Create context with debugging information
    context = AgentContext(
        agent_type="debug_assistant",
        user="developer",
        workspace="ocp-demo",
        current_file="test_payment.py"
    )
    
    context.set_error_context("Payment refund test failing", "test_payment.py")
    context.update_goal("create_bug_report", "Document the payment test failure")
    
    github = create_github_client(token, context)
    
    # In a real scenario, you'd create this in your actual repo
    # For demo purposes, we'll just show the API call structure
    issue_data = {
        "title": "Payment refund test failing with 500 error",
        "body": f"""
## Bug Report

**Context from OCP Agent:**
- Agent Type: {context.agent_type}
- Workspace: {context.workspace}
- File: {context.current_file}
- Goal: {context.current_goal}

**Error Details:**
{context.error_context}

**Recent Changes:**
{', '.join(context.recent_changes) if context.recent_changes else 'None'}

**Agent Summary:**
{context.get_conversation_summary()}

This issue was created by an OCP-enabled agent with full context about the debugging session.
        """.strip(),
        "labels": ["bug", "payment", "test-failure"]
    }
    
    print("📝 Issue would be created with this data:")
    print(f"Title: {issue_data['title']}")
    print(f"Body preview: {issue_data['body'][:200]}...")
    print(f"Labels: {issue_data['labels']}")
    
    # Add to context history
    context.add_interaction(
        "prepared_issue",
        "POST /repos/{owner}/{repo}/issues",
        "Issue data prepared with full context"
    )
    
    print("\n✅ Issue creation prepared with rich OCP context!")
    return context


def demo_context_persistence():
    """
    Demonstrate how OCP context persists across multiple API calls.
    """
    print("\n🔄 Context Persistence Demo")
    print("=" * 50)
    
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("❌ Please set GITHUB_TOKEN environment variable")
        return
    
    # Start with basic context
    context = AgentContext(
        agent_type="ide_copilot",
        user="developer",
        workspace="my-project"
    )
    
    github = create_github_client(token, context)
    
    print("📋 Initial context:")
    print(f"  Goal: {context.current_goal or 'None'}")
    print(f"  History: {len(context.history)} interactions")
    print()
    
    # First interaction - check user info
    print("1️⃣ Getting user information...")
    try:
        response = github.get("/user")
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ Logged in as: {user_data.get('login', 'Unknown')}")
            
            # Update context based on response
            context.update_goal("explore_github_api", f"Working with {user_data.get('login')} account")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"  Updated context - Goal: {context.current_goal}")
    print(f"  History: {len(context.history)} interactions")
    print()
    
    # Second interaction - this call now has context from the first
    print("2️⃣ Searching repositories (with context from previous call)...")
    try:
        response = github.get("/search/repositories", params={
            "q": "python",
            "per_page": 3
        })
        if response.status_code == 200:
            repos = response.json()
            print(f"✅ Found {repos['total_count']} Python repositories")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"  Updated context - History: {len(context.history)} interactions")
    print()
    
    # Third interaction - even more context accumulated
    print("3️⃣ Getting notifications (with accumulated context)...")
    try:
        response = github.get("/notifications", params={"per_page": 5})
        if response.status_code == 200:
            notifications = response.json()
            print(f"✅ Retrieved {len(notifications)} notifications")
        elif response.status_code == 401:
            print("ℹ️ Notifications require additional permissions")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("🎯 Context Persistence Summary:")
    print(f"  Final goal: {context.current_goal}")
    print(f"  Total interactions: {len(context.history)}")
    print(f"  Context summary: {context.get_conversation_summary()}")
    
    print("\n📜 Interaction History:")
    for i, interaction in enumerate(context.history, 1):
        print(f"  {i}. {interaction['timestamp'][:19]} - {interaction['action']}")
        print(f"     {interaction.get('api_endpoint', 'N/A')} -> {interaction.get('result', 'N/A')}")
    
    return context


if __name__ == "__main__":
    print("🚀 OCP GitHub Agent Demo")
    print("This demonstrates how OCP enables intelligent GitHub API interactions\n")
    
    # Run all demos
    debug_context = demo_debug_workflow()
    issue_context = demo_issue_creation()
    persist_context = demo_context_persistence()
    
    print("\n" + "=" * 60)
    print("🎉 Demo Complete!")
    print("\nKey Benefits Demonstrated:")
    print("✅ Agent context flows automatically in HTTP headers")
    print("✅ No server setup required - direct API calls")
    print("✅ Context persists across multiple interactions")
    print("✅ Rich debugging information included in requests")
    print("✅ Standard GitHub API enhanced with agent intelligence")
    print("\nThis is the future of AI agent context sharing! 🚀")