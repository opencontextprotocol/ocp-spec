"""
GitHub API Integration with OCP

Demonstrates OCP's core capabilities:
- Automatic API discovery from OpenAPI specs
- Tool validation and invocation
- Persistent context management
- Zero infrastructure required

Shows how OCP enables context-aware API interactions with
simple setup and persistent context across interactions.
"""

import os
from ocp import OCPAgent, create_github_agent

def main():
    """
    Demo of OCP agent with GitHub API integration.
    """
    print("🚀 OCP + GitHub API Demo")
    print("=" * 40)
    
    # Option 1: Use convenience function
    print("\n📋 Creating GitHub agent...")
    github_agent = create_github_agent()
    github_agent.update_goal("Analyze repository activity and manage issues")
    
    # List discovered tools
    tools = github_agent.list_tools("github")
    print(f"🔧 Discovered {len(tools)} GitHub API tools")
    
    # Search for repository tools
    repo_tools = github_agent.search_tools("repository")
    print(f"📁 Found {len(repo_tools)} repository-related tools:")
    for tool in repo_tools[:5]:  # Show first 5
        print(f"   • {tool.name}: {tool.description[:50]}...")
    
    # Search for issue tools
    issue_tools = github_agent.search_tools("issue")
    print(f"🎫 Found {len(issue_tools)} issue-related tools:")
    for tool in issue_tools[:3]:  # Show first 3
        print(f"   • {tool.name}: {tool.description[:50]}...")
    
    # Show tool documentation
    if repo_tools:
        print(f"\n📖 Documentation for '{repo_tools[0].name}':")
        doc = github_agent.get_tool_documentation(repo_tools[0].name)
        print(doc[:300] + "..." if len(doc) > 300 else doc)
    
    # Show context tracking
    print(f"\n🧠 Agent Context:")
    print(f"   Session ID: {github_agent.context.context_id}")
    print(f"   Goal: {github_agent.context.current_goal}")
    print(f"   Interactions: {len(github_agent.context.history)}")
    
    # Option 2: Manual agent setup
    print(f"\n🔧 Manual API Registration Demo:")
    custom_agent = OCPAgent(
        agent_type="api_explorer",
        workspace="demo-project",
        agent_goal="Explore GitHub API capabilities"
    )
    
    # Register API manually
    try:
        api_spec = custom_agent.register_api(
            name="github_manual",
            spec_url="https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.json"
        )
        print(f"✅ Registered GitHub API:")
        print(f"   Title: {api_spec.title}")
        print(f"   Version: {api_spec.version}")
        print(f"   Tools: {len(api_spec.tools)}")
        
    except Exception as e:
        print(f"⚠️  API registration failed: {e}")
        print("   (This indicates a network issue or invalid OpenAPI spec)")
    
    # Demonstrate context persistence
    print(f"\n📈 Context Evolution:")
    for i, interaction in enumerate(github_agent.context.history):
        print(f"   {i+1}. {interaction['action']}: {interaction['result']}")
    
    print(f"\n✨ OCP Advantages Demonstrated:")
    print(f"   • Zero infrastructure setup")
    print(f"   • Automatic API discovery")
    print(f"   • Persistent context tracking") 
    print(f"   • Context-aware API interactions")
    print(f"   • Works with any OpenAPI spec")

if __name__ == "__main__":
    main()