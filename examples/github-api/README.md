# GitHub API with OCP

This example demonstrates using the GitHub API with OCP context headers for persistent agent sessions.

## Overview

- **API Registration**: Automatically discovers GitHub API endpoints from OpenAPI specification
- **Context Tracking**: Maintains session state across multiple API interactions
- **Tool Discovery**: Finds and validates available GitHub operations
- **HTTP Client**: Context-aware requests with automatic header injection

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set GitHub Token**
   ```bash
   export GITHUB_TOKEN="ghp_your_token_here"
   ```

3. **Run Example**
   ```bash
   python main.py
   ```

## Code Structure

```python
from ocp_agent import OCPAgent, wrap_api

# Create agent with context
agent = OCPAgent(
    agent_type="api_explorer", 
    workspace="github-demo",
    agent_goal="Analyze repository activity and manage issues"
)

# Register GitHub API from OpenAPI spec
api_spec = agent.register_api(
    name="github",
    spec_url="https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.json"
)

# Create context-aware HTTP client
github_client = wrap_api(
    "https://api.github.com",
    agent.context,
    auth="token your_token_here"
)
```

## Features Demonstrated

- **OpenAPI Discovery**: Automatic tool extraction from GitHub's OpenAPI specification
- **Context Persistence**: Agent context maintained across API calls
- **Tool Validation**: Schema-based validation of API operations
- **HTTP Enhancement**: Standard HTTP clients enhanced with OCP headers
- **Session Tracking**: Persistent conversation and interaction history

## HTTP Headers

OCP adds these headers to all GitHub API requests:

```
OCP-Context-ID: ocp-12345678
OCP-Agent-Type: api_explorer  
OCP-Version: 1.0
OCP-Goal: Analyze repository activity and manage issues
OCP-Session: eyJjb250ZXh0X2lkIjoi...
```

## Requirements

- Python 3.8+
- GitHub personal access token
- Internet connection for OpenAPI spec retrieval

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