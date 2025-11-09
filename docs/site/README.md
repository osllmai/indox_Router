# IndoxRouter Documentation Site

This directory contains the static website for IndoxRouter documentation. The site is built with MkDocs and can be served using Docker.

## Running with Docker

### Option 1: Using docker-compose (Recommended)

1. Make sure you have Docker and docker-compose installed on your system.
2. Navigate to this directory in your terminal.
3. Run the following command:

```bash
docker-compose up -d
```

4. Access the documentation at http://localhost:8080

To stop the server:

```bash
docker-compose down
```

### Option 2: Using Docker directly

1. Build the Docker image:

```bash
docker build -t indoxrouter-docs .
```

2. Run the container:

```bash
docker run -d -p 8080:80 --name indoxrouter-docs-container indoxrouter-docs
```

3. Access the documentation at http://localhost:8080

To stop the container:

```bash
docker stop indoxrouter-docs-container
docker rm indoxrouter-docs-container
```

## Production Deployment Considerations

For production deployments, consider:

1. Using a proper domain name with HTTPS
2. Setting up a reverse proxy like Nginx or Traefik
3. Implementing caching strategies
4. Using container orchestration like Kubernetes for high availability
