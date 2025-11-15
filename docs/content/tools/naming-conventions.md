---
title: "Naming Conventions"
weight: 3
---

# Naming Conventions

OCP uses deterministic naming algorithms to ensure consistent, predictable function names across all generated tools. This makes agent code portable and prevents naming conflicts.

## Naming Algorithm

### 1. Operation ID Priority

If the OpenAPI operation includes an `operationId`, use it directly:

```yaml
# OpenAPI specification
paths:
  /repos/{owner}/{repo}/issues:
    post:
      operationId: createIssue  # ← Use this directly
      summary: Create an issue
```

**Generated Function Name:** `createIssue`

### 2. Method + Path Pattern

When no `operationId` is present, generate from HTTP method and path:

```
{method}_{path_segments_with_parameters}
```

**Examples:**

| HTTP Method | Path | Generated Name |
|-------------|------|----------------|
| `GET` | `/users` | `get_users` |
| `POST` | `/users` | `post_users` |
| `GET` | `/users/{id}` | `get_users_id` |
| `DELETE` | `/users/{id}` | `delete_users_id` |
| `GET` | `/repos/{owner}/{repo}` | `get_repos_owner_repo` |
| `POST` | `/repos/{owner}/{repo}/issues` | `post_repos_owner_repo_issues` |

## Path Segment Processing

### Literal Segments
Convert literal path segments to lowercase:

```
/users → users
/repositories → repositories  
/search/issues → search_issues
```

### Parameter Segments
Extract parameter names from `{parameter}` patterns:

```
/{id} → id
/{owner} → owner
/{repo} → repo
/{user_id} → user_id
```

### Special Characters
Handle special characters in paths:

```
/user-profiles → user_profiles  (hyphens → underscores)
/api/v1/users → api_v1_users   (preserve version info)
/users.json → users_json       (dots → underscores)
```

## Semantic Naming Rules

### Common HTTP Method Patterns

OCP recognizes common REST patterns and generates semantic names:

```yaml
# GET collection → list_*
GET /users → list_users
GET /repos/{owner}/{repo}/issues → list_issues

# GET single item → get_*  
GET /users/{id} → get_users_id
GET /repos/{owner}/{repo} → get_repos_owner_repo

# POST → create_*
POST /users → create_user (singular)
POST /repos/{owner}/{repo}/issues → create_issue

# PUT → update_* 
PUT /users/{id} → update_users_id
PUT /repos/{owner}/{repo} → update_repos_owner_repo

# PATCH → update_* (partial)
PATCH /users/{id} → update_users_id

# DELETE → delete_*
DELETE /users/{id} → delete_users_id
DELETE /repos/{owner}/{repo} → delete_repos_owner_repo
```

### Collection vs. Item Naming

When possible, distinguish between collection and item operations:

```python
# Collection operations (no ID parameter)
GET /users → list_users()
POST /users → create_user()

# Item operations (with ID parameter)  
GET /users/{id} → get_user()  # Note: singular
PUT /users/{id} → update_user() 
DELETE /users/{id} → delete_user()
```

## Name Collision Resolution

### Automatic Disambiguation

When naming collisions occur, OCP adds disambiguating suffixes:

```python
# Original names
GET /users → get_users
GET /users/{id} → get_users_id

# With collision (if both existed)
GET /users → get_users_list
GET /users/{id} → get_users_item
```

### Tag-Based Prefixes

Use OpenAPI tags to create namespaced names:

```yaml
paths:
  /users:
    get:
      tags: [admin]
      operationId: listUsers
  /public/users:  
    get:
      tags: [public]
      operationId: listPublicUsers
```

**Generated Names:**
- `admin_list_users`
- `public_list_users`

## Case Conventions

### Function Names
- **Python**: `snake_case` (e.g., `create_user`)
- **JavaScript**: `camelCase` (e.g., `createUser`)

```python
# Python style
def create_repository_issue():
    pass

# JavaScript style  
function createRepositoryIssue() {
    // ...
}
```

### Parameter Names
Follow the same case convention as function names:

```python
# Python
def create_issue(owner, repo, issue_title, issue_body=None):
    pass

# JavaScript
function createIssue(owner, repo, issueTitle, issueBody = null) {
    // ...
}
```

## Reserved Name Handling

### Avoid Language Keywords
```python
# Avoid Python reserved words
GET /class → get_class_info  # Not get_class
GET /import → get_import_data # Not get_import

# Avoid JavaScript reserved words  
GET /delete → get_delete_item # Not delete
GET /return → get_return_data # Not return
```

### Common Method Names
Avoid conflicts with common object methods:

```python
# Avoid conflicts
GET /toString → get_to_string  # Not toString
GET /valueOf → get_value_of   # Not valueOf
```

## Naming Examples

### GitHub API
```yaml
paths:
  /user:
    get:
      operationId: getAuthenticatedUser
  /users/{username}:
    get:
      operationId: getUser  
  /repos/{owner}/{repo}/issues:
    get:
      operationId: listIssues
    post:
      operationId: createIssue
  /repos/{owner}/{repo}/issues/{issue_number}:
    get:
      operationId: getIssue
    patch:
      operationId: updateIssue
```

**Generated Tools:**
- `getAuthenticatedUser()`
- `getUser(username)`  
- `listIssues(owner, repo)`
- `createIssue(owner, repo, title, body=None)`
- `getIssue(owner, repo, issue_number)`
- `updateIssue(owner, repo, issue_number, title=None, body=None)`

### Stripe API
```yaml
paths:
  /customers:
    get: # → list_customers
    post: # → create_customer
  /customers/{id}:
    get: # → get_customer  
    post: # → update_customer
    delete: # → delete_customer
  /payment_intents:
    post: # → create_payment_intent
  /payment_intents/{id}/confirm:
    post: # → confirm_payment_intent
```

**Generated Tools:**
- `list_customers()`
- `create_customer(email, name=None)`
- `get_customer(id)`
- `update_customer(id, email=None, name=None)`
- `delete_customer(id)`
- `create_payment_intent(amount, currency)`
- `confirm_payment_intent(id)`

## Best Practices

### For API Designers
1. **Use Operation IDs**: Provide semantic `operationId` values in your OpenAPI spec
2. **Consistent Naming**: Follow REST conventions for predictable tool names
3. **Descriptive Paths**: Use clear, descriptive path segments
4. **Tag Organization**: Use tags to organize related operations

### For Tool Users
1. **Explore Tools**: Use `list_tools()` to see all available functions
2. **Search Functions**: Use `search_tools(query)` to find specific functionality  
3. **Check Documentation**: Use `get_tool_documentation(name)` for details
4. **Type Hints**: Generated tools include full type information

```python
# Explore available tools
api = ocp.discover_tools("github")

# List all tools
print(f"Available tools: {len(api.tools)}")
for tool in api.tools:
    print(f"  {tool.name}: {tool.description}")

# Search for specific functionality
issue_tools = api.search_tools("issue")
user_tools = api.search_tools("user")

# Get detailed documentation
doc = api.get_tool_documentation("create_issue")
print(doc)
```