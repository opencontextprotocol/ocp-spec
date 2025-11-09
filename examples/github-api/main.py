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
from ocp import OCPAgent, AgentContext

def main():
    """
    Demo of OCP agent with GitHub API integration.
    """
    print("🚀 OCP + GitHub API Demo")
    print("=" * 40)
    
    # Create GitHub agent using generic OCP approach
    print("\n📋 Creating GitHub agent...")
    github_agent = OCPAgent(
        agent_type="api_explorer", 
        workspace="github-demo",
        agent_goal="Analyze repository activity and manage issues"
    )
    
    # Register GitHub API
    print("🔗 Registering GitHub API...")
    try:
        api_spec = github_agent.register_api(
            name="github",
            spec_url="https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.json"
        )
        print(f"✅ GitHub API registered: {api_spec.title} v{api_spec.version}")
    except Exception as e:
        print(f"⚠️  GitHub API registration failed: {e}")
        print("   (This indicates a network issue or invalid OpenAPI spec)")
        return
    
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
    
    # Demonstrate additional OCP capabilities
    print(f"\n🔧 Advanced OCP Features:")
    
    # Show context-aware HTTP client capabilities
    from ocp import wrap_api
    github_http = wrap_api(
        "https://api.github.com",
        github_agent.context,
        headers={"Authorization": f"token {os.getenv('GITHUB_TOKEN', 'your_token_here')}"}
    )
    
    print("🌐 OCP HTTP client created with context awareness")
    print("   • Automatic OCP headers added to all requests")
    print("   • Context tracking for all API interactions")
    print("   • Persistent session management")
    
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