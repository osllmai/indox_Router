# PowerShell script to clear all IndoxRouter data using Docker
# This script clears data from both PostgreSQL and MongoDB containers

Write-Host "===== Clearing IndoxRouter Data (Docker) =====" -ForegroundColor Cyan

# Clear PostgreSQL data
Write-Host "`nClearing PostgreSQL data..." -ForegroundColor Yellow

# SQL command to clear all tables
$pgSqlCommand = @"
SET session_replication_role = 'replica';
TRUNCATE TABLE api_requests;
TRUNCATE TABLE api_keys;
TRUNCATE TABLE billing_transactions;
TRUNCATE TABLE usage_daily_summary;
TRUNCATE TABLE user_subscriptions;
TRUNCATE TABLE users;
SET session_replication_role = 'origin';
"@

try {
    # Execute SQL command in the PostgreSQL container
    docker exec indoxrouter-postgres psql -U postgres -d indoxrouter -c "$pgSqlCommand"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "PostgreSQL data cleared successfully." -ForegroundColor Green
    } else {
        Write-Host "Failed to clear PostgreSQL data. Exit code: $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host "Error clearing PostgreSQL data: $_" -ForegroundColor Red
}

# Clear MongoDB data
Write-Host "`nClearing MongoDB data..." -ForegroundColor Yellow

# MongoDB command to clear all collections
$mongoCommand = @"
db.getCollectionNames().forEach(function(c) { 
    if (!c.startsWith('system.')) { 
        db[c].drop(); 
        print('Dropped collection: ' + c);
    } 
});
print('MongoDB data cleared successfully');
"@

try {
    # Execute MongoDB command in the MongoDB container
    docker exec indoxrouter-mongodb mongosh --quiet "mongodb://localhost:27017/indoxrouter" --eval "$mongoCommand"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "MongoDB data cleared successfully." -ForegroundColor Green
    } else {
        Write-Host "Failed to clear MongoDB data. Exit code: $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host "Error clearing MongoDB data: $_" -ForegroundColor Red
}

Write-Host "`n===== Data Clearing Complete =====" -ForegroundColor Cyan 