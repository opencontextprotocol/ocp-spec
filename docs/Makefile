.PHONY: schemas build dev serve clean

# Generate schema documentation from JSON schemas
schemas:
	@echo "Generating schema documentation..."
	@node generate-schema-docs.js

# Build the Hugo site (with fresh schemas)
build: schemas
	@echo "Building Hugo site..."
	@hugo

# Development server (with fresh schemas)
dev: schemas
	@echo "Starting Hugo development server..."
	@hugo server --buildDrafts --disableFastRender

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
	@echo "  build    - Build the Hugo site"
	@echo "  dev      - Start Hugo development server"
	@echo "  serve    - Alias for dev"
	@echo "  clean    - Clean generated files"
	@echo "  help     - Show this help"