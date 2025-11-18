# Development-focused Dockerfile for frontend
FROM node:20-alpine

# Install wget for health check
RUN apk add --no-cache wget

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install ALL dependencies (including devDependencies for vite)
RUN npm ci

# Ensure node_modules/.bin is in PATH
ENV PATH="/app/node_modules/.bin:$PATH"

# Copy source code (will be overridden by volume mount in docker-compose)
COPY . .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Install dependencies if node_modules doesn't exist (for volume mounts)
# Then run development server
CMD sh -c "if [ ! -d node_modules ]; then npm ci; fi && npx vite --host 0.0.0.0 --port 3000"


