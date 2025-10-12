import requests
import base64
import json
from datetime import datetime
from typing import Dict, List, Optional

class OCPContext:
    """OCP Context manager for GitHub API integration."""
    
    def __init__(self, context_id: str = None, user: str = None):
        self.context = {
            "context_id": context_id or f"github-session-{datetime.now().isoformat()}",
            "user": user,
            "api_specs": ["https://api.github.com/rest/openapi.json"],
            "session": {
                "history": [],
                "state": {}
            },
            "auth": {"tokens": {}},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def to_headers(self) -> Dict[str, str]:
        """Convert context to HTTP headers."""
        self.context["updated_at"] = datetime.now().isoformat()
        
        encoded_session = base64.b64encode(
            json.dumps(self.context).encode()
        ).decode()
        
        return {
            "OCP-Context-ID": self.context["context_id"],
            "OCP-Session": encoded_session,
            "OCP-User": self.context.get("user", ""),
            "OCP-API-Specs": ",".join(self.context["api_specs"])
        }
    
    def add_interaction(self, role: str, content: str):
        """Add interaction to history."""
        self.context["session"]["history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })


class GitHubOCP:
    """GitHub API client with OCP context support."""
    
    def __init__(self, token: str, context: OCPContext = None):
        self.token = token
        self.context = context or OCPContext()
        self.context.context["auth"]["tokens"]["github"] = token
        self.base_url = "https://api.github.com"
    
    def _headers(self) -> Dict[str, str]:
        """Get headers including auth and OCP context."""
        headers = {
            "Authorization": f"token {self.token}",
            "User-Agent": "OCP-GitHub-Example/1.0",
            "Accept": "application/vnd.github.v3+json"
        }
        headers.update(self.context.to_headers())
        return headers
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request with OCP context."""
        url = f"{self.base_url}{endpoint}"
        return requests.request(method, url, headers=self._headers(), **kwargs)
    
    def get_user(self) -> Dict:
        """Get authenticated user information."""
        response = self._make_request("GET", "/user")
        
        if response.ok:
            user_data = response.json()
            self.context.context["user"] = user_data["login"]
            self.context.context["session"]["state"]["github_user"] = user_data
            self.context.add_interaction("tool", f"Retrieved user info for {user_data['login']}")
            
        return response.json()
    
    def get_repos(self, per_page: int = 30) -> List[Dict]:
        """Get user repositories."""
        response = self._make_request("GET", "/user/repos", params={"per_page": per_page})
        
        if response.ok:
            repos = response.json()
            self.context.context["session"]["state"]["repo_count"] = len(repos)
            self.context.add_interaction("tool", f"Retrieved {len(repos)} repositories")
            
        return response.json()
    
    def get_repo(self, owner: str, repo: str) -> Dict:
        """Get specific repository information."""
        response = self._make_request("GET", f"/repos/{owner}/{repo}")
        
        if response.ok:
            repo_data = response.json()
            self.context.add_interaction("tool", f"Retrieved repository {owner}/{repo}")
            
        return response.json()
    
    def create_issue(self, owner: str, repo: str, title: str, body: str = "") -> Dict:
        """Create a new issue."""
        data = {"title": title, "body": body}
        response = self._make_request("POST", f"/repos/{owner}/{repo}/issues", json=data)
        
        if response.ok:
            issue = response.json()
            self.context.add_interaction("tool", f"Created issue #{issue['number']} in {owner}/{repo}")
            
        return response.json()
    
    def search_repos(self, query: str, sort: str = "stars") -> Dict:
        """Search repositories."""
        params = {"q": query, "sort": sort}
        response = self._make_request("GET", "/search/repositories", params=params)
        
        if response.ok:
            results = response.json()
            self.context.add_interaction("tool", f"Searched repositories: {query} ({results['total_count']} results)")
            
        return response.json()


def demo_github_ocp():
    """Demo GitHub API with OCP context."""
    
    # Initialize with token (you'll need a real GitHub token)
    token = "ghp_your_token_here"  # Replace with real token
    context = OCPContext(user="demo-user")
    github = GitHubOCP(token, context)
    
    print("=== GitHub API with OCP Demo ===\n")
    
    # Get user info
    print("1. Getting user information...")
    user = github.get_user()
    print(f"   User: {user.get('name', 'N/A')} (@{user.get('login', 'N/A')})")
    print(f"   Public repos: {user.get('public_repos', 'N/A')}")
    
    # Get repositories
    print("\n2. Getting repositories...")
    repos = github.get_repos(per_page=5)
    print(f"   Found {len(repos)} repositories:")
    for repo in repos[:3]:
        print(f"   - {repo['name']} ({repo['stargazers_count']} stars)")
    
    # Show context state
    print("\n3. Current OCP Context:")
    print(f"   Context ID: {context.context['context_id']}")
    print(f"   User: {context.context['user']}")
    print(f"   Interactions: {len(context.context['session']['history'])}")
    print(f"   Capabilities: {context.context['capabilities']}")
    
    # Show interaction history
    print("\n4. Interaction History:")
    for i, interaction in enumerate(context.context['session']['history']):
        print(f"   {i+1}. [{interaction['role']}] {interaction['content']}")
    
    return github, context


if __name__ == "__main__":
    # Run the demo
    try:
        github_client, ocp_context = demo_github_ocp()
        print("\n✅ Demo completed successfully!")
        print(f"Final context: {ocp_context.context['context_id']}")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Make sure to set a valid GitHub token in the code!")