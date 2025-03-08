# Railway Deployment Guide for indoxRouter Testing

This guide explains how to deploy the indoxRouter application to Railway for testing purposes, including setting up a PostgreSQL database for user information and API keys.

## Prerequisites

- A [Railway](https://railway.app/) account
- [Railway CLI](https://docs.railway.app/develop/cli) installed (optional, but recommended)
- Git installed on your local machine

## Deployment Steps

### 1. Prepare Your Repository

Make sure your repository includes:

- Dockerfile
- railway.json
- All necessary application files

### 2. Deploy to Railway Using the Web Interface

1. Log in to your [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account if not already connected
5. Select your indoxRouter repository
6. Railway will automatically detect the Dockerfile and deploy your application

### 3. Add a PostgreSQL Database

1. In your project dashboard, click "New"
2. Select "Database" → "PostgreSQL"
3. Wait for the database to be provisioned

### 4. Link the Database to Your Application

1. Go to your application service in the Railway dashboard
2. Click on "Variables"
3. Railway automatically adds the `DATABASE_URL` variable to your application
4. Add the following additional variables:
   - `INDOXROUTER_API_KEY`: Your indoxRouter API key

### 5. Deploy Using Railway CLI (Alternative Method)

If you prefer using the CLI:

```bash
# Login to Railway
railway login

# Initialize a new project
railway init

# Link to an existing project (if you already created one via the web interface)
railway link

# Add the PostgreSQL plugin
railway add

# Deploy your application
railway up
```

## Testing Your Deployment

Once deployed, Railway will provide you with a public URL for your application. You can use this URL to test your indoxRouter API.

### Test User Credentials

The database is initialized with a test user:

- Username: `testuser`
- Password: `test123`
- API Key: `test_indoxrouter_key_12345`

### Example API Request

```bash
curl -X POST https://your-railway-url.railway.app/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_indoxrouter_key_12345" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello, world!"}]
  }'
```

## Monitoring and Logs

1. In the Railway dashboard, click on your application service
2. Click on "Logs" to view the application logs
3. You can also monitor the database by clicking on the PostgreSQL service

## Scaling and Production Considerations

For production use, consider:

1. Setting up proper authentication and user management
2. Implementing rate limiting
3. Adding monitoring and alerting
4. Setting up backups for the database
5. Using a custom domain with HTTPS

## Cleaning Up

To delete your test deployment:

1. Go to your project in the Railway dashboard
2. Click on "Settings"
3. Scroll down and click "Delete Project"
