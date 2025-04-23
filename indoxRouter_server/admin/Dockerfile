FROM node:18-alpine as builder
WORKDIR /app

# Copy package files first for better caching
COPY package.json package-lock.json ./
RUN npm ci

# Copy source and config files
COPY . .

# Debug output for troubleshooting
RUN echo "=== Listing source files ===" && \
    ls -la src/ && \
    ls -la src/components/ui/ && \
    echo "=== Vite config ===" && \
    cat vite.config.ts && \
    echo "=== tsconfig.json ===" && \
    cat tsconfig.json

# Set environment variable for API base URL
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Build the app with verbose output
RUN npm run build && \
    echo "=== Build Output ===" && \
    ls -la dist/ && \
    echo "=== Contents of dist/index.html ===" && \
    cat dist/index.html

# Use Nginx to serve the built files
FROM nginx:alpine

# Copy custom Nginx config for SPA routing
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Debug: List contents of nginx html directory
RUN echo "=== Contents of nginx html directory ===" && \
    ls -la /usr/share/nginx/html && \
    echo "=== Contents of index.html ===" && \
    cat /usr/share/nginx/html/index.html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"] 