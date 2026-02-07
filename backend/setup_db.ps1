# Database setup script for Trend Intelligence Dashboard (Windows PowerShell)
# This script creates the PostgreSQL database and tables

param(
    [string]$DbUser = "trend_user",
    [string]$DbPassword = "trend_password",
    [string]$DbName = "trend_dashboard",
    [string]$DbHost = "localhost",
    [string]$DbPort = "5432",
    [string]$PostgresUser = "postgres"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Trend Intelligence Dashboard Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Host: $DbHost"
Write-Host "  Port: $DbPort"
Write-Host "  Database: $DbName"
Write-Host "  User: $DbUser"

# Check if PostgreSQL is installed and accessible
Write-Host ""
Write-Host "Checking PostgreSQL connection..." -ForegroundColor Yellow
try {
    $env:PGPASSWORD = $null
    $output = psql -h $DbHost -U $PostgresUser -tc "SELECT 1" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ PostgreSQL is running" -ForegroundColor Green
    }
    else {
        throw "Connection failed"
    }
}
catch {
    Write-Host "ERROR: Cannot connect to PostgreSQL at $($DbHost):$DbPort" -ForegroundColor Red
    Write-Host "Make sure PostgreSQL is running and you have the correct credentials" -ForegroundColor Red
    exit 1
}

# Create database user
Write-Host ""
Write-Host "Creating database user..." -ForegroundColor Yellow
$createUserSQL = @"
DO `$`$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = '$DbUser') THEN
        CREATE USER $DbUser WITH PASSWORD '$DbPassword';
        GRANT ALL PRIVILEGES ON DATABASE $DbName TO $DbUser;
    END IF;
END
`$`$;
"@

$createUserSQL | psql -h $DbHost -U $PostgresUser
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Database user created or already exists" -ForegroundColor Green
}
else {
    Write-Host "ERROR: Failed to create user" -ForegroundColor Red
    exit 1
}

# Create database
Write-Host ""
Write-Host "Creating database..." -ForegroundColor Yellow
$createDbSQL = "SELECT 'CREATE DATABASE $DbName' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DbName')\gexec"
$createDbSQL | psql -h $DbHost -U $PostgresUser
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Database created or already exists" -ForegroundColor Green
}
else {
    Write-Host "ERROR: Failed to create database" -ForegroundColor Red
    exit 1
}

# Grant privileges
Write-Host ""
Write-Host "Setting up privileges..." -ForegroundColor Yellow
$privSQL = @"
ALTER ROLE $DbUser SET client_encoding TO 'utf8';
ALTER ROLE $DbUser SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DbUser SET default_transaction_deferrable TO on;
ALTER ROLE $DbUser SET default_transaction_READ_ONLY TO off;
GRANT ALL PRIVILEGES ON DATABASE $DbName TO $DbUser;
"@

$privSQL | psql -h $DbHost -U $PostgresUser -d $DbName
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Privileges set" -ForegroundColor Green
}

# Create tables
Write-Host ""
Write-Host "Creating tables..." -ForegroundColor Yellow
psql -h $DbHost -U $PostgresUser -d $DbName -f db/schema.sql
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Tables created" -ForegroundColor Green
}
else {
    Write-Host "ERROR: Failed to create tables" -ForegroundColor Red
    exit 1
}

# Verify setup
Write-Host ""
Write-Host "Verifying setup..." -ForegroundColor Yellow
$tableCountSQL = "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'"
$tableCount = $tableCountSQL | psql -h $DbHost -U $PostgresUser -d $DbName -tc
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Created $tableCount tables" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Database connection string:" -ForegroundColor Yellow
Write-Host "postgresql://$DbUser`:$DbPassword@$DbHost`:$DbPort/$DbName"
Write-Host ""
Write-Host "Add to .env file:" -ForegroundColor Yellow
Write-Host "DATABASE_URL=postgresql://$DbUser`:$DbPassword@$DbHost`:$DbPort/$DbName"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Copy .env.example to .env"
Write-Host "2. Update DATABASE_URL with the connection string above"
Write-Host "3. Run: pip install -r requirements.txt"
Write-Host "4. Run: uvicorn app.main:app --reload"
Write-Host ""
