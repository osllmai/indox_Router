# Deployment Checklist for IndoxRouter

Use this checklist to ensure a smooth deployment of IndoxRouter to your production server.

## Server Preparation

- [ ] Verify server specifications (CPU, RAM, disk space)
- [ ] Ensure SSH access to the server (IP: 91.107.153.195, User: root)
- [ ] Install Docker and Docker Compose on the server
- [ ] Configure firewall to allow necessary ports (SSH, HTTP/HTTPS)
- [ ] Set up monitoring tools (optional)

## Database Configuration

- [ ] Ensure access to your website's PostgreSQL database
- [ ] Verify database schema includes users and API keys tables
- [ ] Test database connection from the server
- [ ] Ensure database user has appropriate permissions
- [ ] Verify database backup script works correctly
- [ ] Confirm backup cron job is properly installed

## Environment Setup

- [ ] Clone the repository to the server
- [ ] Copy the `.env.example` file to `.env`
- [ ] Configure the `.env` file with production settings:
  - [ ] Set secure `SECRET_KEY`
  - [ ] Configure `CORS_ORIGINS` with your website domain
  - [ ] Set `DATABASE_URL` to your website's database
  - [ ] Add provider API keys (OpenAI, Anthropic, etc.)
  - [ ] Configure rate limiting settings

## Deployment

- [ ] Create or update `docker-compose.yml`
- [ ] Build and start the Docker container
- [ ] Verify the server is running with health check
- [ ] Test authentication with a valid API key
- [ ] Test basic functionality (chat, embeddings, etc.)

## Security Recommendations

- [ ] Set up HTTPS with Nginx and Let's Encrypt
- [ ] Configure proper firewall rules
- [ ] Set up fail2ban for SSH protection
- [ ] Implement regular security updates
- [ ] Set up log rotation

## Client Configuration

- [ ] Update the client's `constants.py` to point to the production server
- [ ] Test the client against the production server
- [ ] Document the client configuration for users

## Monitoring and Maintenance

- [ ] Set up log monitoring
- [ ] Configure resource usage alerts
- [ ] Verify backup directories exist at `/opt/indoxrouter/backups`
- [ ] Test database backup script manually
- [ ] Document database restore procedures
- [ ] Set up automatic updates (optional)

## Final Verification

- [ ] Verify all endpoints are working correctly
- [ ] Test with real API keys from your website
- [ ] Monitor server performance under load
- [ ] Document any issues and their solutions
- [ ] Confirm backup logs are being written to `/opt/indoxrouter/logs/backup.log`
