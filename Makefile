.PHONY: schemas build dev serve clean

# Install Node.js dependencies
npm:
	@echo "Installing Node.js dependencies..."
	@cd scripts && npm install

# Build CSS with Tailwind
css:
	@echo "Building CSS..."
	@cd docs && tailwindcss -o ./assets/css/custom.css

# Generate schema documentation
schemas:
	@echo "Generating schema documentation..."
	@node scripts/build-schemas.js

# Generate registry content
registry:
	@echo "Generating registry content..."
	@node scripts/generate-content.js

# Build the Hugo site
build: npm css schemas registry
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
	@rm -f docs/assets/css/custom.css
	@rm -f docs/content/docs/specs/*-schema.md
	@rm -f docs/.hugo_build.lock
	@rm -rf docs/content/docs/registry/
	@rm -rf docs/public/

# Help
help:
	@echo "Available commands:"
	@echo "  css      - Build CSS with Tailwind"
	@echo "  schemas  - Generate schema documentation from JSON schemas"
	@echo "  registry - Generate registry content"
	@echo "  build    - Build complete site (schemas + Hugo)"
	@echo "  dev      - Build and start development server"
	@echo "  serve    - Alias for dev"
	@echo "  clean    - Clean generated files"
	@echo "  help     - Show this help"