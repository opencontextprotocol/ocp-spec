# Multi-stage build for Hugo site
FROM hugomods/hugo:exts-0.154.5 AS builder

# Registry version to use for content generation (git ref: tag, branch, or commit SHA)
ARG REGISTRY_VERSION=v0.8.0

# Set working directory
WORKDIR /src

# Copy entire repo
COPY . .

# Install Tailwind CSS CLI
RUN wget -q https://github.com/tailwindlabs/tailwindcss/releases/download/v4.1.18/tailwindcss-linux-x64-musl -O tailwindcss \
  && chmod +x tailwindcss \
  && ./tailwindcss --version

# Build Tailwind CSS styles
RUN ./tailwindcss \
  -i docs/assets/css/styles.css \
  -o docs/assets/css/custom.css \
  --minify

# Install Node.js dependencies
RUN cd scripts && npm install --production

# Generate registry content pages by fetching data from GitHub
# Script fetches meta.yaml and tools.json files directly from the registry repo
RUN node scripts/generate-content.js \
    docs/content/registry \
    opencontextprotocol/ocp-registry \
    ${REGISTRY_VERSION}

# Build the Hugo site from docs/ subdirectory
RUN cd docs && hugo --gc --minify

# Production stage - serve with nginx
FROM nginx:alpine

# Copy built site from builder
COPY --from=builder /src/docs/public /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
