.PHONY: schemas build dev serve clean

# Generate schema documentation from JSON schemas
schemas:
	@echo "Generating schema documentation..."
	@node build_schemas.js

# Build the Hugo site
build: schemas
	@echo "Building Hugo site..."
	@cd docs && hugo --gc --minify

# Development server
dev: build
	@echo "Starting development server..."
	@echo "Site available at http://localhost:1313"
	@echo "Press Ctrl+C to stop"
	@cd docs/public && python3 -m http.server 1313

# Alias for dev
serve: dev

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	@rm -f docs/content/docs/specs/*-schema.md
	@rm -rf docs/public/

# Help
help:
	@echo "Available commands:"
	@echo "  schemas  - Generate schema documentation from JSON schemas"
	@echo "  build    - Build complete site (schemas + Hugo)"
	@echo "  dev      - Build and start development server"
	@echo "  serve    - Alias for dev"
	@echo "  clean    - Clean generated files"
	@echo "  help     - Show this help"