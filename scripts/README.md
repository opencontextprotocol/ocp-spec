# Build Scripts

This directory contains scripts for building and generating content for the OCP specification site.

## Scripts

### generate-content.js

Generates Hugo markdown pages from OCP Registry API definitions.

### Usage

```bash
node scripts/generate-content.js <output_dir> [registry_repo] [registry_ref]
```

**Arguments:**
- `output_dir`: Directory where Hugo content will be generated (e.g., `docs/content/registry`)
- `registry_repo`: GitHub repository containing registry data (default: `opencontextprotocol/ocp-registry`)
- `registry_ref`: Git reference - branch, tag, or commit SHA (default: `main`)

**Examples:**

```bash
# Generate from latest main branch
node scripts/generate-content.js docs/content/registry

# Generate from specific version tag
node scripts/generate-content.js docs/content/registry opencontextprotocol/ocp-registry v0.6.0

# Generate from development branch
node scripts/generate-content.js docs/content/registry opencontextprotocol/ocp-registry develop

# Using npm script
npm run generate-content docs/content/registry
```

### How It Works

1. **Fetches API list** from GitHub using the GitHub API
2. **Downloads metadata** (`meta.yaml`) and tools (`tools.json`) for each API using GitHub raw content URLs
3. **Renders Nunjucks templates** to generate Hugo-compatible markdown files
4. **Outputs structured content**:
   - `/registry/_index.md` - Registry landing page
   - `/registry/catalog/_index.md` - API catalog with cards
   - `/registry/catalog/{api}/_index.md` - Individual API pages
   - `/registry/catalog/{api}/tools/{tool}.md` - Tool detail pages
   - `/registry/authentication/_index.md` - Authentication guide

### Dependencies

Install dependencies with npm:

```bash
npm install
```

Required packages:
- `js-yaml` - YAML parsing
- `nunjucks` - Template rendering (Jinja2-compatible)

### Templates

Templates are located in `scripts/templates/` and use Nunjucks/Jinja2 syntax:

- `api-page.md.j2` - Main API page template
- `tool-page.md.j2` - Individual tool page template
- `catalog.md.j2` - API catalog page template
- `registry-index.md.j2` - Registry landing page template
- `authentication.md.j2` - Authentication guide template

### Integration with Dockerfile

The Dockerfile uses this script during the build process:

```dockerfile
# Install Node.js and dependencies
RUN apk add --no-cache nodejs npm
COPY package.json package-lock.json* ./
RUN npm install --production

# Generate content from registry
RUN node scripts/generate-content.js \
    docs/content/registry \
    opencontextprotocol/ocp-registry \
    ${REGISTRY_VERSION}
```

This eliminates the need to clone the full registry repository during builds.

## Architecture

### Data Flow

```
GitHub Registry Repo
  └─ data/apis/{api}/
       ├─ meta.yaml      ← API metadata
       └─ tools.json     ← Generated tools
            ↓
     (Fetched via HTTPS)
            ↓
   generate-content.js
            ↓
    (Nunjucks templates)
            ↓
    Hugo Content Files
```

### Benefits of This Approach

1. **Separation of Concerns**: Registry data vs. documentation site
2. **Simplified Builds**: No need to clone entire registry repo
3. **Version Control**: Can generate from any registry version/tag
4. **Faster Builds**: Only fetches needed files (meta.yaml + tools.json)
5. **No SSH Keys**: Uses public GitHub URLs
6. **Flexible**: Can point to forks or different branches
7. **Consistent Tooling**: Pure JavaScript/Node.js like `build-schemas.js`

## build-schemas.js

Generates Hugo markdown documentation pages from JSON Schema files.

### Usage

```bash
node scripts/build-schemas.js

# Or using npm script
npm run build-schemas
```

### How It Works

1. **Reads JSON Schema files** from `schemas/` directory
2. **Formats schemas** as readable JSON with proper indentation
3. **Generates Hugo markdown pages** with frontmatter and schema content
4. **Outputs to** `docs/content/docs/specs/` directory

### Generated Files

- `context-schema.md` - OCP context object schema
- `tool-schema.md` - Tool definition schema
- `openapi-extensions-schema.md` - OpenAPI extensions schema

No external dependencies required - uses only Node.js built-ins.

## Development

To test scripts locally:

```bash
# Install dependencies (for generate-content.js)
npm install

# Generate registry content
npm run generate-content docs/content/registry

# Build schema documentation
npm run build-schemas

# Or run scripts directly
node scripts/generate-content.js docs/content/registry
node scripts/build-schemas.js

# Preview with Hugo
cd docs && hugo server
```

## Adding New Templates

1. Create a new `.md.j2` template in `scripts/templates/`
2. Add a generation function in `generate-content.js`
3. Call the function in the `main()` function
4. Test locally before committing
