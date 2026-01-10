# Contributing to OCP Specification

Thank you for your interest in contributing to the Open Context Protocol specification! This guide will help you contribute to the documentation, schemas, and website.

## Types of Contributions

### 1. Documentation Improvements

Found a typo, unclear explanation, or missing information? Documentation improvements are always welcome.

**Location:** `docs/content/`
- `docs/` - Getting started and implementation guides
- `blog/` - Blog posts and announcements
- `registry/` - Registry catalog pages (auto-generated, see below)

**How to contribute:**
1. Fork the repository
2. Edit markdown files in `docs/content/`
3. Test locally: `cd docs && hugo server`
4. Submit a pull request

### 2. Schema Updates

The JSON schemas define the structure of OCP context objects, tools, and OpenAPI extensions.

**Location:** `schemas/`
- `ocp-context.json` - Context object schema
- `ocp-tool.json` - Tool definition schema
- `ocp-openapi-extensions.json` - OpenAPI extension schema

**How to contribute:**
1. Edit schema JSON files
2. Update schema documentation: `make schemas`
3. Verify changes in `docs/content/docs/specs/`
4. Test with example data
5. Submit a pull request

### 3. Specification Changes

Proposing changes to the protocol itself? These require broader discussion.

**Process:**
1. Open an issue describing the proposed change
2. Discuss rationale and impact with maintainers
3. If approved, submit PR with:
   - Schema updates
   - Documentation updates
   - Example implementations

### 4. Website Improvements

Enhancements to the Hugo site, theme customizations, or styling.

**Location:** `docs/`
- `hugo.yaml` - Site configuration
- `assets/` - CSS and JavaScript
- `layouts/` - Hugo template overrides
- `static/` - Static assets (images, icons)

**Testing:**
```bash
cd docs
hugo server -D
```

### 5. Build Scripts

Improvements to content generation or schema building scripts.

**Location:** `scripts/`
- `generate-content.js` - Generates registry catalog pages
- `build-schemas.js` - Generates schema documentation
- `templates/` - Nunjucks templates for content generation

**Testing:**
```bash
cd scripts
npm install

# Test content generation
node generate-content.js ../docs/content/registry

# Test schema generation
node build-schemas.js
```

## Registry Catalog Content

The registry catalog pages (`docs/content/registry/catalog/`) are **auto-generated** from the [ocp-registry](https://github.com/opencontextprotocol/ocp-registry) repository.

**Do NOT edit these files directly.** Instead:
- To add/update APIs: Contribute to [ocp-registry](https://github.com/opencontextprotocol/ocp-registry)
- To change templates: Edit `scripts/templates/*.j2`
- To regenerate content: `node scripts/generate-content.js docs/content/registry`

## Development Setup

### Prerequisites

- Node.js 18+ (for build scripts)
- Hugo 0.147.0+ (for site building)
- Docker (optional, for testing builds)

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/opencontextprotocol/ocp-spec.git
cd ocp-spec
```

2. Install dependencies:
```bash
cd scripts
npm install
```

3. Run Hugo development server:
```bash
cd ../docs
hugo server -D
```

4. Visit http://localhost:1313

### Testing Docker Build

```bash
docker build -t ocp-spec:test .
docker run -p 8080:80 ocp-spec:test
```

Visit http://localhost:8080

## Pull Request Guidelines

### Before Submitting

- [ ] Test changes locally
- [ ] Run `make schemas` if you modified schema files
- [ ] Verify all links work
- [ ] Check for typos and formatting
- [ ] Update relevant documentation

### PR Description

Include:
- **What**: Brief description of changes
- **Why**: Reason for the change
- **Testing**: How you tested the changes
- **Screenshots**: For visual changes

### Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged
4. Changes deploy automatically via GitHub Actions

## Style Guidelines

### Markdown

- Use headings hierarchically (h1 → h2 → h3)
- Include code language in fenced code blocks
- Use relative links for internal pages
- Keep lines under 120 characters when possible

### Code Examples

Include complete, runnable examples:

```python
from ocp_agent import OCPAgent

# Create agent
agent = OCPAgent()

# Register API
agent.register_api("github")
```

### Commit Messages

Follow conventional commits:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Formatting, no code change
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance tasks

Example: `docs: clarify tool discovery process`

## Questions?

- Open an issue: https://github.com/opencontextprotocol/ocp-spec/issues
- Check existing issues and PRs
- Review the [specification](https://opencontextprotocol.io/docs/specs/)

Thank you for contributing to OCP!
