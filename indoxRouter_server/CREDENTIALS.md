# IndoxRouter Server Credentials

**IMPORTANT: Keep this file secure and do not commit it to version control!**

## Server Details

- **IP Address**: 91.107.153.195
- **SSH Access**: `ssh root@91.107.153.195`
- **SSH Password**: `mkqMHKMbem4WLNTbfNKV`

## Database Credentials

### PostgreSQL

- **User**: `indoxrouter_admin`
- **Password**: `Ejpp4gjm2i4Vgnf+abcdoeWrTlSxeSwo`
- **Database**: `indoxrouter`
- **Port**: `5432` (inside Docker), `15432` (host mapping)
- **Connection URL**: `postgresql://indoxrouter_admin:Ejpp4gjm2i4Vgnf+abcdoeWrTlSxeSwo@indoxrouter-postgres:5432/indoxrouter`

### MongoDB

- **User**: `indoxrouter_admin`
- **Password**: `/vLiS2JYfb8wm52lsow+hURaI6aa+k+I`
- **Database**: `indoxrouter`
- **Port**: `27017` (inside Docker), `27018` (host mapping)
- **Connection URL**: `mongodb://indoxrouter_admin:/vLiS2JYfb8wm52lsow+hURaI6aa+k+I@indoxrouter-mongodb:27017/indoxrouter?authSource=admin`

### Redis

- **Password**: `Ejpp4gjm2i4Vgnf+abcdoeWrTlSxeSwo`
- **Port**: `6379` (inside Docker), `6380` (host mapping)

## Application Secrets

- **SECRET_KEY**: `1ddd977e43c006e6c02a28e18d13fa9a4530762a36d6d579ac5004cc18a4bd90`

## API Provider Keys

Remember to update these in the .env file after deployment:

- **OPENAI_API_KEY**: `your_openai_key_here`
- **ANTHROPIC_API_KEY**: `your_anthropic_key_here`
- **COHERE_API_KEY**: `your_cohere_key_here`
- **GOOGLE_API_KEY**: `your_google_key_here`
- **MISTRAL_API_KEY**: `your_mistral_key_here`

## Database Backups

- **Backup Directory**: `/opt/indoxrouter/backups`
- **Schedule**: Daily at 2:00 AM
- **Retention**: 14 days (older backups are automatically deleted)
- **Backup Formats**:
  - PostgreSQL: SQL dump (gzipped)
  - MongoDB: Archive format (gzipped)
  - Redis: RDB files
- **Manual Backup**: Run `bash /opt/indoxrouter/scripts/backup_databases.sh` to create a manual backup
- **Logs**: Backup logs are stored in `/opt/indoxrouter/logs/backup.log`

## How to Access Databases Locally (If Needed)

### PostgreSQL

```bash
# Access PostgreSQL from host
psql -h localhost -p 15432 -U indoxrouter_admin -d indoxrouter
# Password: Ejpp4gjm2i4Vgnf+abcdoeWrTlSxeSwo
```

### MongoDB

```bash
# Access MongoDB from host
mongosh mongodb://indoxrouter_admin:/vLiS2JYfb8wm52lsow+hURaI6aa+k+I@localhost:27018/indoxrouter?authSource=admin
```

### Redis

```bash
# Access Redis from host
redis-cli -h localhost -p 6380 -a Ejpp4gjm2i4Vgnf+abcdoeWrTlSxeSwo
```

## Accessing Application

- **HTTP**: `http://91.107.153.195`
- **API Endpoint**: `http://91.107.153.195:8000`
