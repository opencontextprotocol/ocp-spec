# GitHub API with OCP

This example shows how the existing GitHub API can work with OCP context with zero changes to GitHub's infrastructure.

## Key Points

1. **GitHub API doesn't need to change** - OCP context travels in HTTP headers
2. **Standard authentication** - Uses existing GitHub token auth
3. **Zero additional infrastructure** - Direct HTTP calls to api.github.com
4. **Immediate compatibility** - Works with existing GitHub API clients
5. **⚠️ Current Status**: GitHub doesn't read OCP headers yet - context is managed client-side

## How It Works Today vs Future

### **Current Reality (Phase 1)**
- GitHub API **ignores** OCP headers (which is fine!)
- Client (your agent) **manages context** locally
- Each API call includes context headers for future compatibility
- Context accumulates on the client side between calls

### **Future Enhancement (Phase 2)**  
- GitHub could optionally **read** OCP headers
- Provide **smarter responses** based on agent context
- Example: Return deployment-focused data when context shows "debugging deployment failure"

## Example: User Information Flow

### 1. Initial Request with OCP Context

```bash
curl -H "Authorization: token ghp_your_token_here" \
     -H "OCP-Context-ID: session-123" \
     -H "OCP-User: alice" \
     -H "OCP-Capabilities: https://api.github.com/.well-known/ocp-capabilities" \
     https://api.github.com/user
```

Response:
```json
{
  "login": "alice",
  "id": 12345,
  "name": "Alice Developer",
  "email": "alice@example.com"
}
```

### 2. Follow-up Request (Context Preserved)

```bash
curl -H "Authorization: token ghp_your_token_here" \
     -H "OCP-Context-ID: session-123" \
     -H "OCP-Session: eyJ1c2VyIjoiYWxpY2UiLCJoaXN0b3J5IjpbXX0=" \
     https://api.github.com/user/repos
```

The context carries forward automatically, enabling:
- Session continuity across multiple API calls
- User preference persistence
- Interaction history tracking

## Python Example

```python
import requests
import base64
import json

class GitHubOCP:
    def __init__(self, token, context_id="session-123"):
        self.token = token
        self.context = {
            "context_id": context_id,
            "user": None,
            "session": {"history": [], "state": {}},
            "auth": {"tokens": {"github": token}}
        }
        
    def _headers(self):
        return {
            "Authorization": f"token {self.token}",
            "OCP-Context-ID": self.context["context_id"],
            "OCP-Session": base64.b64encode(
                json.dumps(self.context).encode()
            ).decode(),
            "User-Agent": "OCP-GitHub-Example/1.0"
        }
    
    def get_user(self):
        response = requests.get(
            "https://api.github.com/user",
            headers=self._headers()
        )
        
        # Update context with user info
        if response.ok:
            user_data = response.json()
            self.context["user"] = user_data["login"]
            self.context["session"]["state"]["github_user"] = user_data
            
        return response.json()
    
    def get_repos(self):
        response = requests.get(
            "https://api.github.com/user/repos",
            headers=self._headers()
        )
        
        # Add to interaction history
        if response.ok:
            repos = response.json()
            self.context["session"]["history"].append({
                "role": "tool",
                "content": f"Retrieved {len(repos)} repositories",
                "timestamp": "2025-03-16T10:00:00Z"
            })
            
        return response.json()

# Usage
github = GitHubOCP("ghp_your_token")
user = github.get_user()
repos = github.get_repos()

print(f"User: {user['name']}")
print(f"Repos: {len(repos)}")
print(f"Context: {github.context['context_id']}")
```

## OpenAPI Extensions for GitHub

If GitHub wanted to formally support OCP, they could add these extensions to their OpenAPI spec:

```yaml
openapi: 3.0.0
info:
  title: GitHub API
  version: 3.0.0
  x-ocp-enabled: true
  x-ocp-context-aware: true

paths:
  /user:
    get:
      summary: Get the authenticated user
      x-ocp-context:
        provides: ["user_info", "github_login"]
        preserves: ["session_id"]
      responses:
        200:
          description: User information
          
  /user/repos:
    get:
      summary: List repositories for the authenticated user
      x-ocp-context:
        requires: ["user_info"]
        provides: ["repo_list"]
        preserves: ["session_id", "github_login"]
      responses:
        200:
          description: Repository list
```

## AI Agent Integration

```python
from openai import OpenAI
import json

class GitHubAI:
    def __init__(self, github_token, openai_key):
        self.github = GitHubOCP(github_token)
        self.client = OpenAI(api_key=openai_key)
        
    def chat_with_github(self, user_message):
        # Get current context
        context = self.github.context
        
        # Include GitHub capabilities in the conversation
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_user_repos",
                    "description": "Get the user's GitHub repositories",
                    "parameters": {"type": "object", "properties": {}}
                }
            }
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You can access GitHub API. Current user: {context.get('user', 'unknown')}"},
                {"role": "user", "content": user_message}
            ],
            tools=tools
        )
        
        # Execute tool calls with OCP context
        if response.choices[0].message.tool_calls:
            for tool_call in response.choices[0].message.tool_calls:
                if tool_call.function.name == "get_user_repos":
                    repos = self.github.get_repos()
                    return f"Found {len(repos)} repositories: {[r['name'] for r in repos[:5]]}"
        
        return response.choices[0].message.content

# Usage
ai = GitHubAI("ghp_token", "openai_key")
result = ai.chat_with_github("What repositories do I have?")
print(result)
```

## Benefits Demonstrated

1. **Zero Infrastructure**: Direct calls to api.github.com, no proxy servers
2. **Standard Auth**: Uses existing GitHub tokens
3. **Context Continuity**: Session state flows between calls
4. **Existing Tooling**: Works with curl, Postman, any HTTP client
5. **AI Integration**: Easy to use with AI agents and LLMs

## Implementation Benefits

This OCP implementation provides:

- **Zero Infrastructure**: Direct calls to api.github.com, no proxy servers
- **Standard Protocols**: Uses existing GitHub APIs with OCP context headers  
- **Simple Authentication**: Standard GitHub token authentication
- **No Maintenance**: No servers or additional infrastructure to manage

**Result**: Full GitHub API integration with persistent context and zero setup complexity.