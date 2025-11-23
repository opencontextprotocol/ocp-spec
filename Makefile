.PHONY: schemas versions build dev serve clean

# Generate schema documentation from JSON schemas
schemas:
	@echo "Generating schema documentation..."
	@node build_schemas.js

# Build all site versions using build.sh
versions: schemas
	@echo "Building all site versions..."
	@./build_versions.sh "http://localhost:1313"

# Build the Hugo site (with fresh schemas and versions)
build: versions
	@echo "Hugo build completed via versions target"

# Development server (with fresh schemas and versions)
dev: versions
	@echo "Starting Hugo development server..."
	@cd docs && hugo server --buildDrafts --disableFastRender

# Alias for dev
serve: dev

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@rm -f content/documentation/specification/*-schema.md
	@rm -rf public/

# Help
help:
	@echo "Available commands:"
	@echo "  schemas  - Generate schema documentation from JSON schemas"
	@echo "  versions - Build all site versions using build.sh"
	@echo "  build    - Build complete site (schemas + versions)"
	@echo "  dev      - Start Hugo development server with all versions"
	@echo "  serve    - Alias for dev"
	@echo "  clean    - Clean generated files"
	@echo "  help     - Show this help"