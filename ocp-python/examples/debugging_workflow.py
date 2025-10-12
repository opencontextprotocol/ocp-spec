#!/usr/bin/env python3
"""
Debugging Workflow Example - Multi-step debugging with OCP context.

This example shows the "MCP vs OCP" difference in action:
- MCP: Multiple stateless servers, no conversation memory
- OCP: Context flows through each API call, building agent intelligence
"""

import os
import sys
import time
from typing import Optional, Dict, Any

# Add src to path for running examples directly  
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ocp import AgentContext, wrap_api, create_debug_agent


class DebugWorkflow:
    """
    Multi-step debugging workflow demonstrating OCP context accumulation.
    
    This simulates a real IDE debugging scenario where an agent helps
    a developer debug a failing test by gathering context across multiple APIs.
    """
    
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.context = None
        self.github = None
    
    def start_debug_session(self, error_message: str, file_path: str, workspace: str = "payment-service"):
        """Start a new debugging session with initial error context."""
        print("🐛 Starting Debug Session")
        print("=" * 40)
        
        # Create debug-optimized context
        self.context = create_debug_agent(
            error=error_message,
            file_path=file_path,
            workspace=workspace
        )
        
        # Set up GitHub client with context
        self.github = wrap_api(
            "https://api.github.com",
            self.context,
            auth=f"token {self.github_token}"
        )
        
        print(f"🎯 Goal: {self.context.current_goal}")
        print(f"📁 Workspace: {workspace}")
        print(f"📄 File: {file_path}")
        print(f"❌ Error: {error_message}")
        print()
        
        return self.context
    
    def step1_search_similar_issues(self, search_terms: str):
        """Step 1: Search for similar issues (with context)."""
        print("1️⃣ Searching for similar issues...")
        
        try:
            response = self.github.get("/search/issues", params={
                "q": f"{search_terms} repo:stripe/stripe-python OR repo:psf/requests",
                "per_page": 5,
                "sort": "updated"
            })
            
            if response.status_code == 200:
                issues = response.json()
                print(f"✅ Found {issues['total_count']} related issues")
                
                relevant_issues = []
                for issue in issues['items'][:3]:
                    print(f"  • #{issue['number']}: {issue['title']}")
                    print(f"    {issue['html_url']}")
                    print(f"    State: {issue['state']} | Comments: {issue['comments']}")
                    
                    relevant_issues.append({
                        "number": issue['number'],
                        "title": issue['title'], 
                        "url": issue['html_url'],
                        "state": issue['state']
                    })
                
                # Update context with findings
                self.context.add_interaction(
                    "searched_similar_issues",
                    "GET /search/issues",
                    f"Found {len(relevant_issues)} relevant issues",
                    metadata={"issues": relevant_issues}
                )
                
                # Update goal based on findings
                if relevant_issues:
                    self.context.update_goal(
                        "debug_with_community_insights",
                        f"Found {len(relevant_issues)} similar issues to investigate"
                    )
                
                print()
                return relevant_issues
            else:
                print(f"❌ GitHub API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error searching issues: {e}")
            return []
    
    def step2_analyze_recent_commits(self, repo_owner: str, repo_name: str):
        """Step 2: Analyze recent commits for related changes."""
        print("2️⃣ Analyzing recent commits...")
        
        try:
            # Get recent commits
            response = self.github.get(f"/repos/{repo_owner}/{repo_name}/commits", params={
                "per_page": 10,
                "since": "2024-01-01T00:00:00Z"  # Recent commits
            })
            
            if response.status_code == 200:
                commits = response.json()
                print(f"✅ Retrieved {len(commits)} recent commits")
                
                # Look for payment-related commits
                payment_commits = []
                for commit in commits:
                    message = commit['commit']['message'].lower()
                    if any(keyword in message for keyword in ['payment', 'refund', 'test', 'fix']):
                        print(f"  • {commit['sha'][:7]}: {commit['commit']['message'][:60]}...")
                        print(f"    Author: {commit['commit']['author']['name']}")
                        print(f"    Date: {commit['commit']['author']['date'][:10]}")
                        
                        payment_commits.append({
                            "sha": commit['sha'][:7],
                            "message": commit['commit']['message'], 
                            "author": commit['commit']['author']['name'],
                            "date": commit['commit']['author']['date']
                        })
                
                # Update context with commit analysis
                self.context.add_interaction(
                    "analyzed_recent_commits",
                    f"GET /repos/{repo_owner}/{repo_name}/commits",
                    f"Found {len(payment_commits)} relevant commits",
                    metadata={"commits": payment_commits}
                )
                
                if payment_commits:
                    # Add recent changes to context
                    for commit in payment_commits[:3]:
                        self.context.add_recent_change(f"{commit['sha']}: {commit['message'][:50]}")
                
                print()
                return payment_commits
            else:
                print(f"❌ GitHub API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error analyzing commits: {e}")
            return []
    
    def step3_check_test_files(self, repo_owner: str, repo_name: str):
        """Step 3: Examine test files for patterns."""
        print("3️⃣ Checking test file patterns...")
        
        try:
            # Search for test files
            response = self.github.get("/search/code", params={
                "q": f"test payment refund filename:test repo:{repo_owner}/{repo_name}",
                "per_page": 5
            })
            
            if response.status_code == 200:
                results = response.json()
                print(f"✅ Found {results['total_count']} test files")
                
                test_files = []
                for item in results['items']:
                    print(f"  • {item['name']}: {item['path']}")
                    print(f"    {item['html_url']}")
                    
                    test_files.append({
                        "name": item['name'],
                        "path": item['path'],
                        "url": item['html_url']
                    })
                
                # Update context
                self.context.add_interaction(
                    "examined_test_files", 
                    "GET /search/code",
                    f"Found {len(test_files)} relevant test files",
                    metadata={"test_files": test_files}
                )
                
                print()
                return test_files
            else:
                print(f"❌ GitHub API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error checking test files: {e}")
            return []
    
    def step4_generate_solution(self):
        """Step 4: Generate solution based on accumulated context."""
        print("4️⃣ Generating solution from accumulated context...")
        
        # Analyze all the context we've gathered
        solution_context = {
            "original_error": self.context.error_context,
            "file": self.context.current_file,
            "workspace": self.context.workspace,
            "interactions": len(self.context.history),
            "recent_changes": self.context.recent_changes,
            "conversation_summary": self.context.get_conversation_summary()
        }
        
        print("📊 Context Analysis:")
        print(f"  • Original error: {solution_context['original_error']}")
        print(f"  • File being debugged: {solution_context['file']}")
        print(f"  • API interactions: {solution_context['interactions']}")
        print(f"  • Recent changes tracked: {len(solution_context['recent_changes'])}")
        print()
        
        # Generate solution based on context
        solutions = [
            "1. Check recent payment processor changes for breaking changes",
            "2. Verify test environment configuration matches production",
            "3. Review similar GitHub issues for community solutions",
            "4. Examine test file patterns for assertion mismatches",
            "5. Check API response format changes in recent commits"
        ]
        
        print("💡 Suggested debugging steps:")
        for solution in solutions:
            print(f"  {solution}")
        
        # Final context update
        self.context.add_interaction(
            "generated_solution",
            "internal_analysis",
            "Generated 5 debugging steps from context",
            metadata={"solutions": solutions, "context_used": solution_context}
        )
        
        self.context.update_goal(
            "solution_provided",
            "Debugging steps generated from accumulated context"
        )
        
        print()
        return solutions
    
    def get_session_summary(self):
        """Get a complete summary of the debugging session."""
        print("📋 Debug Session Summary")
        print("=" * 40)
        
        print(f"🎯 Final Goal: {self.context.current_goal}")
        print(f"📈 Total Interactions: {len(self.context.history)}")
        print(f"🔄 Recent Changes Tracked: {len(self.context.recent_changes)}")
        print(f"⏱️ Session Duration: {(self.context.last_updated - self.context.created_at).seconds} seconds")
        print()
        
        print("🗂️ Interaction Timeline:")
        for i, interaction in enumerate(self.context.history, 1):
            timestamp = interaction['timestamp'][11:19]  # Just time part
            print(f"  {i}. {timestamp} - {interaction['action']}")
            print(f"     {interaction.get('api_endpoint', 'internal')} -> {interaction.get('result', 'completed')}")
        
        print()
        print(f"📝 Context Summary: {self.context.get_conversation_summary()}")
        
        return self.context.to_dict()


def demo_mcp_vs_ocp():
    """
    Demonstrate the difference between MCP and OCP approaches.
    """
    print("⚔️ MCP vs OCP Debugging Comparison")
    print("=" * 50)
    
    print("🔴 MCP Approach:")
    print("  1. Agent calls GitHub MCP server (stateless)")
    print("  2. MCP server makes API call, returns generic results")
    print("  3. Agent calls filesystem MCP server (no context from step 1)")
    print("  4. Agent calls GitHub MCP server again (no memory of previous calls)")
    print("  5. User must repeat context at each step")
    print()
    
    print("🟢 OCP Approach:")
    print("  1. Agent makes direct GitHub API call with context headers")
    print("  2. Context accumulates automatically in agent memory")
    print("  3. Next API call includes previous context + new information")
    print("  4. Each subsequent call becomes more intelligent")
    print("  5. Agent builds complete picture of debugging session")
    print()
    
    print("🎯 Key Difference: OCP agents get smarter with each interaction!")
    print()


if __name__ == "__main__":
    print("🔧 OCP Debugging Workflow Demo")
    print("This shows how OCP context makes debugging workflows intelligent\n")
    
    # Show MCP vs OCP comparison first
    demo_mcp_vs_ocp()
    
    # Check for GitHub token
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ Please set GITHUB_TOKEN environment variable to run the demo")
        print("   You can get a token at: https://github.com/settings/tokens")
        sys.exit(1)
    
    # Run the debugging workflow
    workflow = DebugWorkflow(github_token)
    
    # Start debug session
    context = workflow.start_debug_session(
        error_message="AssertionError: Expected 200, got 500 in test_payment_refund",
        file_path="test_payment.py",
        workspace="payment-service"
    )
    
    # Execute debugging steps
    print("🚀 Executing multi-step debugging workflow...\n")
    
    issues = workflow.step1_search_similar_issues("payment test failure 500 error")
    time.sleep(1)  # Be nice to GitHub API
    
    commits = workflow.step2_analyze_recent_commits("stripe", "stripe-python")
    time.sleep(1)
    
    test_files = workflow.step3_check_test_files("stripe", "stripe-python") 
    time.sleep(1)
    
    solutions = workflow.step4_generate_solution()
    
    # Show final summary
    summary = workflow.get_session_summary()
    
    print("\n" + "=" * 60)
    print("🎉 Debugging Workflow Complete!")
    print("\nOCP Benefits Demonstrated:")
    print("✅ Context flows automatically between API calls")
    print("✅ Agent builds intelligence with each interaction")
    print("✅ No stateless MCP servers to manage")
    print("✅ Direct API calls with accumulated context")
    print("✅ Complete debugging session memory")
    print("\nThis is how AI debugging should work! 🚀")