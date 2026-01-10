# Multi-stage build for Hugo site
FROM hugomods/hugo:exts-0.147.4 AS builder

# Registry version to use for content generation (git ref: tag, branch, or commit SHA)
ARG REGISTRY_VERSION=v0.8.0

# Install Node.js for content generation
RUN apk add --no-cache nodejs npm

# Set working directory
WORKDIR /src

# Copy entire repo
COPY . .

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

# Copy custom nginx config (if needed)
# COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
