# Multi-stage build for Hugo site
FROM hugomods/hugo:exts-0.147.4 AS builder

# Install git and Python for content generation
RUN apk add --no-cache git python3 py3-pip openssh-client

# Set working directory
WORKDIR /src

# Copy entire repo including .git folder
COPY . .

# Clone ocp-registry repo to generate registry content
RUN --mount=type=ssh \
    mkdir -p -m 0600 ~/.ssh && \
    ssh-keyscan github.com >> ~/.ssh/known_hosts && \
    git clone git@github.com:opencontextprotocol/ocp-registry.git /tmp/ocp-registry

# Install Python dependencies for content generation
RUN cd /tmp/ocp-registry && \
    pip3 install --break-system-packages pyyaml

# Generate registry content pages
RUN python3 /tmp/ocp-registry/scripts/generate-content.py \
    --registry-dir /tmp/ocp-registry/data \
    --output-dir /src/docs/content/registry

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
