FROM node:18-alpine as builder
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code and configuration files
COPY . .

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

# Create a custom mime.types file
RUN echo "types {" > /etc/nginx/mime.types && \
    echo "    application/javascript    js;" >> /etc/nginx/mime.types && \
    echo "    text/css                  css;" >> /etc/nginx/mime.types && \
    echo "}" >> /etc/nginx/mime.types

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"] 