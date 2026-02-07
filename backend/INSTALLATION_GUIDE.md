# Installation Guide

Complete step-by-step installation instructions for the Trend Intelligence Dashboard backend.

## System Requirements

- Python 3.11 or higher
- PostgreSQL 12 or higher
- Redis 6.0+ (optional, for Celery tasks)
- 2GB RAM minimum
- 500MB disk space minimum

## Installation Methods

Choose one of the following installation methods:

---

## Method 1: Docker Compose (Recommended for Development)

Easiest way to get started with all services running.

### Prerequisites
- Docker
- Docker Compose

### Steps

1. **Navigate to backend directory**
   ```bash
   cd trend-intelligence-dashboard/backend
   ```

2. **Start services**
   ```bash
   docker-compose up -d
   ```

3. **Verify services**
   ```bash
   docker-compose ps
   ```
   All three services (postgres, redis, api) should show "healthy" status.

4. **Test API**
   ```bash
   curl http://localhost:8000/health
   ```

5. **Access API documentation**
   - Open http://localhost:8000/docs in your browser

6. **Stop services**
   ```bash
   docker-compose down
   ```

### Useful Docker Commands

```bash
# View logs
docker-compose logs -f api

# Connect to database inside container
docker-compose exec postgres psql -U trend_user -d trend_dashboard

# Rebuild images after code changes
docker-compose up -d --build

# Clean up everything
docker-compose down -v
```

---

## Method 2: Local Development Setup

For development with local services.

### Step 1: Install PostgreSQL

**macOS (Homebrew)**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows**
- Download from https://www.postgresql.org/download/windows/
- Run installer and follow setup wizard
- Note: PostgreSQL runs as a service

### Step 2: Create Database and User

**Using the setup script (Recommended)**

On macOS/Linux:
```bash
cd backend
chmod +x setup_db.sh
./setup_db.sh
```

On Windows PowerShell:
```powershell
cd backend
.\setup_db.ps1
```

**Manual setup (Optional)**

Connect to PostgreSQL:
```bash
psql -U postgres
```

Run these commands:
```sql
CREATE DATABASE trend_dashboard;
CREATE USER trend_user WITH PASSWORD 'trend_password';
ALTER ROLE trend_user SET client_encoding TO 'utf8';
ALTER ROLE trend_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE trend_user SET default_transaction_deferrable TO on;
ALTER ROLE trend_user SET default_transaction_READ_ONLY TO off;
GRANT ALL PRIVILEGES ON DATABASE trend_dashboard TO trend_user;
\c trend_dashboard
\i schema.sql
\q
```

### Step 3: Setup Python Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Step 5: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings (use defaults for local development)
# nano .env  or  code .env  or  open -t .env
```

Default `.env` values (good for local development):
```
DATABASE_URL=postgresql://trend_user:trend_password@localhost:5432/trend_dashboard
REDIS_URL=redis://localhost:6379
USE_MOCK_AI=True
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","http://localhost:8000"]
```

### Step 6: Install Redis (Optional but Recommended)

**macOS**
```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian**
```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
```

**Windows**
- Use Windows Subsystem for Linux (WSL)
- Or Docker: `docker run -d -p 6379:6379 redis:7-alpine`

### Step 7: Start the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at: http://localhost:8000

Access documentation at: http://localhost:8000/docs

To stop: Press `Ctrl+C`

---

## Method 3: Production Deployment (Railway/Heroku)

For deploying to production platforms.

### Prerequisites
- Git repository (GitHub, GitLab, etc.)
- Railway.app account (or similar platform)
- PostgreSQL database (provided by platform)

### Deployment Steps

See the platform-specific guides below.

---

## Verification Checklist

After installation, verify everything works:

### 1. Database Connection
```bash
# Test connection
psql -U trend_user -d trend_dashboard -c "SELECT 1"
```

### 2. API Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "app": "Trend Intelligence Dashboard", "version": "1.0.0"}
```

### 3. API Documentation
Open http://localhost:8000/docs - should show Swagger UI with all endpoints

### 4. Submit a Test Trend
```bash
curl -X POST http://localhost:8000/api/trends/submit \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://instagram.com/p/test123",
    "source_platform": "instagram",
    "submitted_by": "test_user"
  }'
```

Should return a trend object with analysis.

### 5. Database Tables
```bash
psql -U trend_user -d trend_dashboard -c "\dt"
```

Should list 5 tables:
- mood_boards
- monitoring_targets
- trend_items
- trend_metrics_history
- trending_hashtags

---

## Troubleshooting

### PostgreSQL Issues

**Connection refused**
```bash
# Check if PostgreSQL is running
psql -U postgres -c "SELECT 1"

# If not running, start it
# macOS: brew services start postgresql@15
# Linux: sudo systemctl start postgresql
# Windows: Check Services app
```

**Password authentication failed**
- Verify DATABASE_URL in .env
- Check username and password
- Reset password: `ALTER USER trend_user PASSWORD 'newpassword';`

**Database doesn't exist**
```bash
# Create it
createdb -U postgres trend_dashboard
```

### Python Issues

**Python version too old**
```bash
python3 --version  # Must be 3.11+
# Update Python if needed
```

**ModuleNotFoundError**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Virtual environment not activated**
```bash
# Activate it (you should see (venv) in your prompt)
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows
```

### Port Already in Use

**Port 8000 is in use**
```bash
# Use different port
uvicorn app.main:app --reload --port 8001

# Or kill the process using port 8000
# Linux/macOS:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### API Errors

**Database tables don't exist**
- Solution: Run `db/schema.sql` again
  ```bash
  psql -U trend_user -d trend_dashboard -f db/schema.sql
  ```

**CORS errors from frontend**
- Add frontend URL to CORS_ORIGINS in .env
  ```
  CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","http://yourfrontend.com"]
  ```

---

## Upgrading Dependencies

When dependencies need updates:

```bash
# Update pip
pip install --upgrade pip

# Update all packages
pip install -r requirements.txt --upgrade

# Update specific package
pip install --upgrade fastapi

# Generate updated requirements
pip freeze > requirements.txt
```

---

## Development Tools Setup

### IDE Configuration

**VS Code**
1. Install "Python" extension
2. Install "SQLTools" for database management
3. Set Python interpreter to `venv/bin/python`
4. Use format on save with Black

**PyCharm**
1. Create project and point to this directory
2. Set Python interpreter to `venv/bin/python`
3. Mark `app` directory as Sources Root

### Code Formatting

Install development tools:
```bash
pip install black flake8 isort mypy
```

Format code:
```bash
black app/
isort app/
```

Check style:
```bash
flake8 app/
mypy app/
```

---

## Next Steps

1. **Review API Documentation**: http://localhost:8000/docs
2. **Read API Examples**: See API_EXAMPLES.md
3. **Setup Frontend**: Build frontend that calls these endpoints
4. **Configure Real Claude AI**: (Optional) Set CLAUDE_API_KEY for production
5. **Deploy**: Choose a hosting platform and deploy

---

## Support

For issues:
1. Check the troubleshooting section above
2. Review server logs: `docker-compose logs -f api`
3. Check database: `psql -U trend_user -d trend_dashboard`
4. Review FastAPI documentation: https://fastapi.tiangolo.com/

---

## Quick Reference

### Common Commands

```bash
# Start development server
uvicorn app.main:app --reload

# Run tests
pytest

# Format code
black app/ && isort app/

# Check database
psql -U trend_user -d trend_dashboard

# Connect to Redis
redis-cli

# View Docker logs
docker-compose logs -f api

# Rebuild Docker
docker-compose up -d --build
```

### Environment Variables

```bash
# .env file contents
DATABASE_URL=postgresql://user:password@host:5432/database
REDIS_URL=redis://host:6379
USE_MOCK_AI=True
CLAUDE_API_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
CORS_ORIGINS=["http://localhost:5173"]
```

### Useful URLs

- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

Now you're ready to start developing! Visit http://localhost:8000/docs to test the API.
