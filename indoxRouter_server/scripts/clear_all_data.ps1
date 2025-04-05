# PowerShell script to clear all IndoxRouter data
# This script clears data from both PostgreSQL and MongoDB

Write-Host "===== Clearing IndoxRouter Data =====" -ForegroundColor Cyan

# Clear PostgreSQL data
Write-Host "`nClearing PostgreSQL data..." -ForegroundColor Yellow
$pgPassword = "postgrespassword"
$env:PGPASSWORD = $pgPassword

# Run the SQL script
try {
    psql -h localhost -p 5433 -U postgres -d indoxrouter -f "scripts/clear_data.sql"
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

try {
    # MongoDB has no easy script runner like psql, so we'll use the mongo shell 
    # if available, otherwise we can just drop all collections directly
    
    # Try using mongosh (modern MongoDB shell)
    mongosh "mongodb://localhost:27018/indoxrouter" --eval "db.getCollectionNames().forEach(function(c) { if (!c.startsWith('system.')) { db[c].drop(); } })"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "MongoDB data cleared successfully." -ForegroundColor Green
    } else {
        Write-Host "Failed to clear MongoDB data. Exit code: $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host "Error clearing MongoDB data: $_" -ForegroundColor Red
}

Write-Host "`n===== Data Clearing Complete =====" -ForegroundColor Cyan 