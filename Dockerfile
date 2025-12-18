# Multi-stage build for Hugo site
FROM hugomods/hugo:exts-0.147.4 AS builder

# Install git for enableGitInfo
RUN apk add --no-cache git

# Set working directory
WORKDIR /src

# Copy entire repo including .git folder
COPY . .

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
