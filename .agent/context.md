# Open Context Protocol - Agent Context

This document captures critical project decisions, patterns, and expectations for AI agents working on this codebase.

## Project Overview

The Open Context Protocol (OCP) specification repository contains:
- Protocol specification and documentation
- Python agent library (`ocp-python/`)
- CLI tool (`cli/`)
- Hugo-based documentation site (`site/`)

## Development Philosophy

### MVP Approach
- **Always start minimal**: Implement only what's explicitly requested
- **Incremental development**: Small, deliberate steps
- **Avoid feature creep**: Don't add unrequested functionality
- **User corrections are paramount**: When user says "too much", strip back immediately

### Decision Making
- Follow established patterns within the project
- Maintain consistency across similar components
- Ask for clarification rather than assume requirements

## Python Project Structure Standards

### Package Organization
Both Python projects follow this established pattern:

```
project-root/
├── pyproject.toml          # Poetry configuration
├── README.md              # Project documentation
├── .python-version        # pyenv version (3.12.11)
├── poetry.lock           # Locked dependencies
└── src/
    └── package_name/     # Source package
        ├── __init__.py
        └── *.py
```

### Naming Conventions
- **Package names**: Use hyphens (e.g., `open-context-agent`, `ocp-cli`, `ocp-registry`)
- **Module names**: Use underscores matching package intent (e.g., `ocp_agent`, `ocp_cli`, `ocp_registry`)
- **PyPI package name**: `open-context-agent` (avoids conflicts with existing `ocp-*` packages on PyPI)
- **Import convention**: `from ocp_agent import OCPAgent` (short and convenient for developers)
- **Rationale**: PyPI name is unique and searchable, module name is concise for daily use

### Current Structure
- `ocp-python/src/ocp_agent/` - Core agent library (PyPI: `open-context-agent`)
- `cli/src/ocp_cli/` - Command-line interface
- `registry/src/ocp_registry/` - Community API registry service (FastAPI)

### Dependency Management
- **Tool**: Poetry for all Python projects
- **Python version**: 3.12.11 (specified in `.python-version`)
- **Approach**: Minimal dependencies, avoid dev/test dependencies unless specifically requested
- **Local dependencies**: Use path dependencies between related projects

### Testing
- **Framework**: pytest 7.0 (matches ocp-agent library)
- **Approach**: Minimal test coverage for core functionality
- **Location**: `tests/` directory in each project
- **Run**: `poetry run pytest tests/ -v`
- **Philosophy**: Test critical paths, not exhaustive coverage

## Key Technical Decisions

### Package Naming Resolution
**Problem**: Originally had naming conflict between `ocp-agent` package and `src/ocp/` module.

**Solution**: Renamed `src/ocp/` to `src/ocp_agent/` for consistency.

**Impact**: 
- Eliminates import conflicts
- Makes package/module relationship clear
- Allows CLI to potentially use `src/ocp/` if needed
- Updated CLI imports from `from ocp` to `from ocp_agent`

### CLI Architecture
- **Console script**: `ocp` command via Poetry entry point
- **Structure**: Modular command architecture
- **Features**: Context management, API testing, registry operations
- **Integration**: Uses `ocp_agent` library as dependency

### Registry Integration
- **Implementation**: OCPRegistry client in CLI
- **Functionality**: List, search, and interact with API registry
- **Architecture**: Separate client class for registry operations

## File Patterns

### Python Version Management
- All projects include `.python-version` with `3.12.11`
- Ensures consistent Python environment across pyenv users

### Poetry Configuration
- Minimal `pyproject.toml` files
- Essential metadata only
- Clear dependency specifications
- Local path dependencies for inter-project relationships

## Working Patterns

### When Starting New Work
1. Review this context document
2. Understand the MVP principle
3. Check existing patterns before implementing
4. Follow established project structure

### When User Requests Changes
1. Implement exactly what's requested
2. Don't add unrequested features
3. If user says "too much", immediately strip back
4. Ask for clarification on ambiguous requirements

### When Adding Dependencies
1. Keep minimal - only add what's needed
2. Avoid dev dependencies unless specifically requested
3. Use Poetry for all Python dependency management
4. Document rationale for new dependencies

## Common Anti-Patterns to Avoid

1. **Over-engineering**: Adding tests, linting, dev tools without request
2. **Feature creep**: Implementing related but unrequested functionality
3. **Inconsistent structure**: Deviating from established patterns
4. **Assumption-driven development**: Implementing based on assumptions rather than explicit requests

## Project-Specific Knowledge

### Registry System
- **Purpose**: Community convenience service hosted by OCP team (not end-user infrastructure)
- **Architecture**: FastAPI service with SQLite database
- **Location**: `registry/src/ocp_registry/`
- **Features**: API registration, search/discovery, OpenAPI validation, tool extraction
- **Zero Infrastructure Principle**: Optional service - OCP works fine without it, enterprises can host their own
- **Integration**: CLI uses OCPRegistry client for discovery
- **Database**: SQLite for development, production uses hosted service

### CLI Commands
- `ocp context` - Context management
- `ocp call` - API calls with OCP enhancement
- `ocp validate` - File validation
- `ocp test` - API testing
- `ocp registry` - Registry operations

### Documentation Site
- Hugo-based static site generator
- Located in `site/` directory
- Generates specification documentation

## Version Information

- **Python**: 3.12.11
- **Poetry**: Used for dependency management
- **ocp-python (PyPI: open-context-agent)**: 0.1.0
- **CLI Version**: 0.2.0
- **Registry Version**: 0.1.0

---

**Last Updated**: October 26, 2025
**Context Thread**: Package naming for PyPI publication - renamed to `open-context-agent` to avoid conflicts