# OCP Community Registry

A searchable database of pre-discovered API configurations for the Open Context Protocol.

## Overview

The OCP Registry provides a centralized service where:
- API providers can register their OpenAPI specifications
- Agent developers can discover available APIs
- Community can share and validate API configurations
- Agents can quickly bootstrap with popular APIs

## Features

- **API Registration**: Submit APIs with metadata
- **Search & Discovery**: Find APIs by name, category, description
- **Validation**: Verify OpenAPI specs and endpoint availability
- **Community Curation**: Rating and validation by community

## API Endpoints

### Core Registry
- `GET /api/v1/registry` - List all registered APIs
- `GET /api/v1/registry/{name}` - Get specific API configuration
- `POST /api/v1/registry` - Register new API
- `PUT /api/v1/registry/{name}` - Update API registration
- `DELETE /api/v1/registry/{name}` - Remove API registration

### Search & Discovery
- `GET /api/v1/search?q={query}` - Search APIs by name/description
- `GET /api/v1/categories` - List available categories
- `GET /api/v1/categories/{category}` - Get APIs by category

### Validation
- `POST /api/v1/validate` - Validate OpenAPI spec and endpoint
- `GET /api/v1/registry/{name}/status` - Check API health

## Quick Start

### Using the OCP CLI (Recommended)

The registry is integrated into the OCP CLI for easy access:

```bash
# Start the registry server
cd registry/
poetry install
poetry run uvicorn registry.main:app --reload

# Use OCP CLI to interact with registry
ocp registry search github
ocp registry get github
ocp registry list --category development
ocp registry register my-api.json
```

### Using cURL (Direct API)

```bash
# Install dependencies
poetry install

# Run development server
poetry run uvicorn registry.main:app --reload

# Register an API
curl -X POST "http://localhost:8000/api/v1/registry" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "github",
    "display_name": "GitHub API",
    "description": "GitHub REST API for repository management",
    "openapi_url": "https://api.github.com/rest/openapi.json",
    "base_url": "https://api.github.com",
    "category": "development",
    "auth_type": "bearer_token"
  }'

# Search APIs
curl "http://localhost:8000/api/v1/search?q=github"

# Get API details
curl "http://localhost:8000/api/v1/registry/github"
```

## Development

```bash
# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run isort .

# Type checking
poetry run mypy registry/
```