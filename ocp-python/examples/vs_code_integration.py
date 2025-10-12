#!/usr/bin/env python3
"""
VS Code Integration Example - OCP in IDE agents.

This demonstrates how OCP would integrate with VS Code extensions
to provide context-aware API interactions for coding assistants.
"""

import os
import sys
import json
from typing import Dict, Any, Optional, List

# Add src to path for running examples directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ocp import AgentContext, wrap_api, create_ide_agent


class VSCodeOCPIntegration:
    """
    Simulates VS Code extension integration with OCP.
    
    In a real extension, this would hook into VS Code's API to get
    workspace info, current file, and user context.
    """
    
    def __init__(self, workspace_path: str, user: str = "developer"):
        self.workspace_path = workspace_path
        self.workspace_name = os.path.basename(workspace_path)
        self.user = user
        self.context = None
        self.api_clients = {}
    
    def initialize_context(self, current_file: Optional[str] = None):
        """Initialize OCP context from VS Code workspace."""
        print("🆚 VS Code OCP Integration Starting...")
        print("=" * 45)
        
        # Create IDE-optimized context
        self.context = create_ide_agent(
            user=self.user,
            workspace=self.workspace_name,
            current_file=current_file
        )
        
        # Set initial goal
        self.context.update_goal(
            "assist_with_coding",
            "VS Code coding assistant ready to help"
        )
        
        print(f"👤 User: {self.user}")
        print(f"📁 Workspace: {self.workspace_name}")
        print(f"📄 Current File: {current_file or 'None'}")
        print(f"🎯 Goal: {self.context.current_goal}")
        print()
        
        return self.context
    
    def setup_github_integration(self, token: str):
        """Set up GitHub integration with OCP context."""
        print("🐙 Setting up GitHub integration...")
        
        self.api_clients['github'] = wrap_api(
            "https://api.github.com",
            self.context,
            auth=f"token {token}"
        )
        
        # Add GitHub API spec to context
        self.context.add_api_spec("github", "https://docs.github.com/en/rest")
        
        print("✅ GitHub client ready with OCP context")
        return self.api_clients['github']
    
    def simulate_file_change(self, new_file: str, change_description: str):
        """Simulate user changing files in VS Code."""
        print(f"📝 File changed: {new_file}")
        
        # Update context
        self.context.current_file = new_file
        self.context.add_recent_change(f"Opened {new_file}")
        self.context.add_recent_change(change_description)
        
        # Log the file change
        self.context.add_interaction(
            "file_changed",
            "vscode_event",
            f"Switched to {new_file}",
            metadata={"change": change_description}
        )
        
        print(f"  Context updated with file change")
        print(f"  Summary: {self.context.get_conversation_summary()}")
        print()
    
    def simulate_error_detection(self, error_message: str, line_number: int):
        """Simulate VS Code detecting an error."""
        print(f"❌ Error detected at line {line_number}")
        print(f"   {error_message}")
        
        # Update context with error information
        self.context.set_error_context(
            f"Line {line_number}: {error_message}",
            self.context.current_file
        )
        
        self.context.update_goal(
            "debug_error",
            f"Debugging error in {self.context.current_file}"
        )
        
        print(f"  Context updated with error information")
        print()
    
    def get_intelligent_suggestions(self):
        """Get context-aware suggestions using GitHub API."""
        if 'github' not in self.api_clients:
            print("❌ GitHub not configured")
            return []
        
        print("🧠 Getting intelligent suggestions...")
        
        github = self.api_clients['github']
        
        try:
            # Search for issues related to current context
            search_query = ""
            if self.context.error_context:
                # Extract keywords from error
                error_words = self.context.error_context.split()[:5]
                search_query = " ".join(error_words)
            else:
                # Use file extension for general search
                if self.context.current_file:
                    ext = os.path.splitext(self.context.current_file)[1]
                    search_query = f"language:{ext[1:] if ext else 'python'}"
            
            if search_query:
                response = github.get("/search/repositories", params={
                    "q": search_query,
                    "sort": "stars",
                    "per_page": 3
                })
                
                if response.status_code == 200:
                    repos = response.json()
                    suggestions = []
                    
                    print(f"✅ Found {repos['total_count']} relevant repositories:")
                    for repo in repos['items']:
                        suggestion = {
                            "type": "repository",
                            "title": repo['name'],
                            "description": repo.get('description', 'No description'),
                            "url": repo['html_url'],
                            "stars": repo['stargazers_count']
                        }
                        suggestions.append(suggestion)
                        
                        print(f"  • {repo['name']} ({repo['stargazers_count']} ⭐)")
                        print(f"    {repo.get('description', 'No description')[:60]}...")
                        print(f"    {repo['html_url']}")
                    
                    # Log this interaction
                    self.context.add_interaction(
                        "searched_repositories",
                        "GET /search/repositories",
                        f"Found {len(suggestions)} relevant repositories",
                        metadata={"suggestions": suggestions}
                    )
                    
                    print()
                    return suggestions
        
        except Exception as e:
            print(f"❌ Error getting suggestions: {e}")
        
        return []
    
    def get_context_aware_completions(self, partial_code: str):
        """Simulate getting context-aware code completions."""
        print(f"💭 Getting completions for: '{partial_code}'")
        
        # In a real implementation, this would call AI models with OCP context
        # For demo, we'll show how context influences suggestions
        
        completions = []
        
        # Use context to influence completions
        if "test" in self.context.current_file.lower() if self.context.current_file else False:
            completions = [
                "test_payment_success()",
                "test_refund_functionality()",
                "assert response.status_code == 200"
            ]
        elif "api" in partial_code.lower():
            completions = [
                "requests.get(url, headers=headers)",
                "response.json()",
                "response.status_code"
            ]
        else:
            completions = [
                "def main():",
                "if __name__ == '__main__':",
                "print(f'Debug: {variable}')"
            ]
        
        print("✅ Context-aware completions:")
        for i, completion in enumerate(completions, 1):
            print(f"  {i}. {completion}")
        
        # Log this interaction
        self.context.add_interaction(
            "provided_completions",
            "vscode_completion",
            f"Generated {len(completions)} context-aware completions",
            metadata={"partial_code": partial_code, "completions": completions}
        )
        
        print()
        return completions
    
    def get_session_analytics(self):
        """Get analytics about the OCP context session."""
        print("📊 VS Code Session Analytics")
        print("=" * 35)
        
        analytics = {
            "session_duration": (self.context.last_updated - self.context.created_at).seconds,
            "total_interactions": len(self.context.history),
            "files_worked_on": len(set([h.get('metadata', {}).get('file') for h in self.context.history if h.get('metadata', {}).get('file')])),
            "api_calls_made": len([h for h in self.context.history if 'api_call' in h['action']]),
            "errors_debugged": 1 if self.context.error_context else 0,
            "goal_changes": len([h for h in self.context.history if 'goal' in h.get('metadata', {})]),
            "context_summary": self.context.get_conversation_summary()
        }
        
        print(f"⏱️ Session Duration: {analytics['session_duration']} seconds")
        print(f"🔄 Total Interactions: {analytics['total_interactions']}")
        print(f"📁 Files Worked On: {analytics['files_worked_on']}")
        print(f"🌐 API Calls Made: {analytics['api_calls_made']}")
        print(f"🐛 Errors Debugged: {analytics['errors_debugged']}")
        print(f"🎯 Goal Changes: {analytics['goal_changes']}")
        print()
        print(f"📝 Session Summary:")
        print(f"   {analytics['context_summary']}")
        
        return analytics


def demo_vscode_workflow():
    """Demonstrate a complete VS Code workflow with OCP."""
    print("🎬 VS Code OCP Workflow Demo")
    print("=" * 50)
    
    # Initialize VS Code integration
    vscode = VSCodeOCPIntegration(
        workspace_path="/Users/developer/payment-service",
        user="alice"
    )
    
    # Step 1: Initialize context
    context = vscode.initialize_context("src/payment_processor.py")
    
    # Step 2: Set up GitHub integration
    token = os.getenv("GITHUB_TOKEN")
    if token:
        github = vscode.setup_github_integration(token)
    else:
        print("⚠️ GITHUB_TOKEN not set, skipping GitHub integration")
    
    # Step 3: Simulate file changes
    vscode.simulate_file_change(
        "test/test_payment.py", 
        "Added new test for refund functionality"
    )
    
    # Step 4: Simulate error detection
    vscode.simulate_error_detection(
        "AssertionError: Expected 200, got 500",
        45
    )
    
    # Step 5: Get intelligent suggestions (if GitHub available)
    if token:
        suggestions = vscode.get_intelligent_suggestions()
    
    # Step 6: Get context-aware completions
    completions = vscode.get_context_aware_completions("test_")
    
    # Step 7: More file work
    vscode.simulate_file_change(
        "src/api_client.py",
        "Fixed HTTP status code handling"
    )
    
    completions2 = vscode.get_context_aware_completions("api.")
    
    # Step 8: Show session analytics
    analytics = vscode.get_session_analytics()
    
    return vscode, analytics


def compare_with_mcp():
    """Show the difference between OCP and MCP for VS Code."""
    print("\n⚔️ VS Code: MCP vs OCP Comparison")
    print("=" * 45)
    
    print("🔴 Current MCP approach in VS Code:")
    print("  1. Configure multiple MCP servers in settings.json")
    print("  2. Extension spawns server processes")
    print("  3. JSON-RPC communication for each request")
    print("  4. Servers are stateless - no conversation memory")
    print("  5. Complex debugging when servers fail")
    print("  6. Server updates require extension updates")
    print()
    
    print("🟢 OCP approach in VS Code:")
    print("  1. Simple token configuration in settings.json")
    print("  2. Direct HTTP calls to APIs")
    print("  3. Context flows in standard HTTP headers")
    print("  4. Full conversation memory across interactions")
    print("  5. Standard HTTP debugging tools work")
    print("  6. API updates work immediately")
    print()
    
    print("📊 Configuration Comparison:")
    print()
    
    print("MCP Configuration (complex):")
    mcp_config = {
        "mcp.servers": {
            "github": {
                "command": "node",
                "args": ["/path/to/github-mcp-server/dist/index.js"],
                "env": {"GITHUB_TOKEN": "ghp_..."}
            },
            "filesystem": {
                "command": "node", 
                "args": ["/path/to/fs-mcp-server/dist/index.js"]
            }
        }
    }
    print(json.dumps(mcp_config, indent=2))
    
    print("\nOCP Configuration (simple):")
    ocp_config = {
        "ocp.enabled": True,
        "github.token": "ghp_...",
        "ocp.workspace.tracking": True
    }
    print(json.dumps(ocp_config, indent=2))
    
    print("\n🎯 Result: OCP is 10x simpler and infinitely more powerful!")


if __name__ == "__main__":
    print("🆚 OCP VS Code Integration Demo")
    print("This shows how OCP revolutionizes IDE agent development\n")
    
    # Run the VS Code workflow demo
    vscode, analytics = demo_vscode_workflow()
    
    # Show MCP comparison
    compare_with_mcp()
    
    print("\n" + "=" * 60)
    print("🎉 VS Code Demo Complete!")
    print("\nOCP Benefits for IDE Extensions:")
    print("✅ Zero server infrastructure required")
    print("✅ Context persists across all interactions") 
    print("✅ Standard HTTP debugging and monitoring")
    print("✅ Direct API calls = better performance")
    print("✅ Simple configuration and setup")
    print("✅ Immediate API updates without extension changes")
    print("\nThe future of IDE agents is here! 🚀")