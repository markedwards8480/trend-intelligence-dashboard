#!/bin/bash

# Database setup script for Trend Intelligence Dashboard
# This script creates the PostgreSQL database and tables

set -e  # Exit on error

echo "=========================================="
echo "Trend Intelligence Dashboard Setup"
echo "=========================================="

# Configuration
DB_USER="${DB_USER:-trend_user}"
DB_PASSWORD="${DB_PASSWORD:-trend_password}"
DB_NAME="${DB_NAME:-trend_dashboard}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"

echo "Configuration:"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"

# Check if PostgreSQL is running
echo ""
echo "Checking PostgreSQL connection..."
if ! psql -h "$DB_HOST" -U "$POSTGRES_USER" -tc "SELECT 1" > /dev/null 2>&1; then
    echo "ERROR: Cannot connect to PostgreSQL at $DB_HOST:$DB_PORT"
    echo "Make sure PostgreSQL is running and you have the correct credentials"
    exit 1
fi
echo "✓ PostgreSQL is running"

# Create database user
echo ""
echo "Creating database user..."
psql -h "$DB_HOST" -U "$POSTGRES_USER" <<EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_user WHERE usename = '$DB_USER') THEN
        CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
        GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
    END IF;
END
\$\$;
EOF
echo "✓ Database user created or already exists"

# Create database
echo ""
echo "Creating database..."
psql -h "$DB_HOST" -U "$POSTGRES_USER" <<EOF
SELECT 'CREATE DATABASE $DB_NAME' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec
EOF
echo "✓ Database created or already exists"

# Grant privileges
echo ""
echo "Setting up privileges..."
psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$DB_NAME" <<EOF
ALTER ROLE $DB_USER SET client_encoding TO 'utf8';
ALTER ROLE $DB_USER SET default_transaction_isolation TO 'read committed';
ALTER ROLE $DB_USER SET default_transaction_deferrable TO on;
ALTER ROLE $DB_USER SET default_transaction_READ_ONLY TO off;
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF
echo "✓ Privileges set"

# Create tables
echo ""
echo "Creating tables..."
psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$DB_NAME" -f db/schema.sql
echo "✓ Tables created"

# Verify setup
echo ""
echo "Verifying setup..."
TABLE_COUNT=$(psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$DB_NAME" -tc \
    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'")
echo "✓ Created $TABLE_COUNT tables"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Database connection string:"
echo "postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
echo ""
echo "Add to .env file:"
echo "DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env"
echo "2. Update DATABASE_URL with the connection string above"
echo "3. Run: pip install -r requirements.txt"
echo "4. Run: uvicorn app.main:app --reload"
echo ""
