# Multi-stage build for Hugo site
FROM hugomods/hugo:exts-0.147.4 AS builder

# Registry version to use for content generation (git ref: tag, branch, or commit SHA)
ARG REGISTRY_VERSION=v0.6.0

# Install git and Python for content generation
RUN apk add --no-cache git python3 py3-pip openssh-client

# Python and Poetry environment variables
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=2.2.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    POETRY_SYSTEM_GIT_CLIENT=1

# Set working directory
WORKDIR /src

# Copy entire repo including .git folder
COPY . .

# Clone ocp-registry repo to generate registry content
RUN --mount=type=ssh \
    mkdir -p -m 0600 ~/.ssh && \
    ssh-keyscan github.com >> ~/.ssh/known_hosts && \
    git clone git@github.com:opencontextprotocol/ocp-registry.git /tmp/ocp-registry && \
    cd /tmp/ocp-registry && \
    git checkout ${REGISTRY_VERSION}

# Install ocp-registry dependencies using Poetry
RUN --mount=type=ssh \
    python3 -m venv /venv && \
    /venv/bin/pip install poetry==$POETRY_VERSION && \
    cd /tmp/ocp-registry && \
    /venv/bin/poetry install --only=main --no-root

# Add both Poetry's venv and the project's venv to PATH
ENV PATH="/tmp/ocp-registry/.venv/bin:/venv/bin:$PATH"

# Generate tools.json files from OpenAPI specs
RUN cd /tmp/ocp-registry && python scripts/generate-tools.py

# Generate registry content pages
RUN python /tmp/ocp-registry/scripts/generate-content.py /src/docs/content/registry

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
