# Dockerfile for the admin panel

# Stage 1: build the application
FROM node:18-alpine AS builder
WORKDIR /app

# Install Git to allow commit info capture and other tooling
RUN apk add --no-cache git

# Install dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy the rest of the source code
COPY . .

# Allow passing the API base URL at build time
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

# Build the production bundle
RUN npm run build

# Stage 2: serve the built files with Nginx
FROM nginx:alpine

# Copy build output to Nginx's public directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80 for incoming traffic
EXPOSE 80

# Run Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]