# Deployment Guide

This guide explains how to deploy IndoxRouter Server in different environments.

## Docker Deployment

The recommended way to deploy IndoxRouter is using Docker and Docker Compose.

### Prerequisites

- Docker and Docker Compose installed
- Git (for cloning the repository)
- A server with at least 2GB RAM
- Provider API keys for the models you want to use

### Deployment Steps

1. Clone the repository:

```bash
git clone https://github.com/yourusername/indoxrouter.git
cd indoxrouter
```

2. Create a production environment file:

```bash
cp production.env .env
```

3. Edit the `.env` file to set your provider API keys and other configuration:

```bash
nano .env
```

4. Build and start the Docker containers:

```bash
docker-compose up -d
```

This will start the following containers:

- `indoxrouter-server`: The FastAPI application
- `indoxrouter-postgres`: PostgreSQL database
- `indoxrouter-mongo`: MongoDB database

5. Create an initial user account:

```bash
docker-compose exec indoxrouter-server python -m scripts.create_user --username admin --password secure_password --email admin@example.com --credits 1000
```

6. Verify the deployment is working:

```bash
curl http://localhost:8000/api/v1/health
```

### Docker Compose Configuration

The `docker-compose.yml` file defines the services and their configuration:

```yaml
version: "3.8"

services:
  indoxrouter-server:
    build: .
    image: indoxrouter-server
    container_name: indoxrouter-server
    restart: unless-stopped
    ports:
      - "8000:8000"
    depends_on:
      - indoxrouter-postgres
      - indoxrouter-mongo
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs

  indoxrouter-postgres:
    image: postgres:15
    container_name: indoxrouter-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: indoxrouter
    volumes:
      - indoxrouter-postgres-data:/var/lib/postgresql/data

  indoxrouter-mongo:
    image: mongo:6
    container_name: indoxrouter-mongo
    restart: unless-stopped
    volumes:
      - indoxrouter-mongo-data:/data/db

volumes:
  indoxrouter-postgres-data:
  indoxrouter-mongo-data:
```

## Kubernetes Deployment

For production deployments with high availability, Kubernetes is recommended.

### Prerequisites

- Kubernetes cluster
- kubectl configured
- Helm (optional)

### Kubernetes Manifests

The repository includes Kubernetes manifests in the `kubernetes/` directory:

- `server-deployment.yaml`: Deployment for the server
- `postgres-statefulset.yaml`: StatefulSet for PostgreSQL
- `mongo-statefulset.yaml`: StatefulSet for MongoDB
- `configmap.yaml`: ConfigMap for environment variables
- `secret.yaml`: Secret for sensitive configuration
- `service.yaml`: Services for networking
- `ingress.yaml`: Ingress for external access

### Deployment Steps

1. Create the namespace:

```bash
kubectl create namespace indoxrouter
```

2. Create the secrets (replace with your actual API keys):

```bash
kubectl create secret generic indoxrouter-secrets \
  --namespace indoxrouter \
  --from-literal=OPENAI_API_KEY=sk-... \
  --from-literal=MISTRAL_API_KEY=... \
  --from-literal=SECRET_KEY=... \
  --from-literal=POSTGRES_PASSWORD=...
```

3. Deploy the manifests:

```bash
kubectl apply -f kubernetes/
```

4. Wait for the pods to start:

```bash
kubectl get pods -n indoxrouter -w
```

5. Create an initial user:

```bash
kubectl exec -it deployment/indoxrouter-server -n indoxrouter -- python -m scripts.create_user --username admin --password secure_password --email admin@example.com --credits 1000
```

## Scaling

IndoxRouter can be scaled both vertically and horizontally.

### Vertical Scaling

Increase resources for the containers in `docker-compose.yml`:

```yaml
indoxrouter-server:
  # ...
  deploy:
    resources:
      limits:
        cpus: "2"
        memory: 4G
      reservations:
        cpus: "1"
        memory: 2G
```

Or in Kubernetes:

```yaml
resources:
  requests:
    memory: "2Gi"
    cpu: "1"
  limits:
    memory: "4Gi"
    cpu: "2"
```

### Horizontal Scaling

For horizontal scaling, increase the replica count in Kubernetes:

```bash
kubectl scale deployment indoxrouter-server -n indoxrouter --replicas=3
```

## Database Backups

### PostgreSQL Backups

1. Create a backup:

```bash
docker-compose exec indoxrouter-postgres pg_dump -U postgres indoxrouter > backup.sql
```

2. Restore from backup:

```bash
cat backup.sql | docker-compose exec -T indoxrouter-postgres psql -U postgres -d indoxrouter
```

### MongoDB Backups

1. Create a backup:

```bash
docker-compose exec indoxrouter-mongo mongodump --out /dump
docker cp indoxrouter-mongo:/dump ./mongo-backup
```

2. Restore from backup:

```bash
docker cp ./mongo-backup indoxrouter-mongo:/dump
docker-compose exec indoxrouter-mongo mongorestore /dump
```

## Monitoring

IndoxRouter can be monitored using standard tools:

- **Logging**: Logs are stored in the `logs/` directory
- **Health Checks**: The `/api/v1/health` endpoint provides status information
- **Prometheus Metrics**: Available at `/metrics` when enabled
- **Grafana Dashboard**: A sample dashboard is provided in `monitoring/grafana/`

## Troubleshooting

### Common Issues

1. **Database connection failures**:

   - Verify the database containers are running
   - Check database connection strings in `.env`
   - Verify network connectivity between containers

2. **API key authentication failures**:

   - Verify the API keys in the database
   - Check authentication headers in the client

3. **Provider API errors**:
   - Verify provider API keys in `.env`
   - Check provider service status

### Viewing Logs

```bash
# View server logs
docker-compose logs -f indoxrouter-server

# View PostgreSQL logs
docker-compose logs -f indoxrouter-postgres

# View MongoDB logs
docker-compose logs -f indoxrouter-mongo
```

### Restarting Services

```bash
# Restart all services
docker-compose restart

# Restart just the server
docker-compose restart indoxrouter-server
```
