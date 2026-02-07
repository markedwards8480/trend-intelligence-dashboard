# Quick Start Guide

Get the Trend Intelligence Dashboard backend running in 5 minutes.

## Option 1: Local Development (Easiest)

### Step 1: Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# In psql:
CREATE DATABASE trend_dashboard;
CREATE USER trend_user WITH PASSWORD 'trend_password';
ALTER ROLE trend_user SET client_encoding TO 'utf8';
ALTER ROLE trend_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE trend_user SET default_transaction_deferrable TO on;
ALTER ROLE trend_user SET default_transaction_READ_ONLY TO off;
GRANT ALL PRIVILEGES ON DATABASE trend_dashboard TO trend_user;
\q
```

### Step 2: Setup Python Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Create .env file
cp .env.example .env

# Edit .env with your database credentials
# Set USE_MOCK_AI=True to use mock data (no API keys needed)
```

### Step 4: Start the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at: http://localhost:8000

## Option 2: Using Docker Compose

Create a `docker-compose.yml` in the backend directory:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: trend_user
      POSTGRES_PASSWORD: trend_password
      POSTGRES_DB: trend_dashboard
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://trend_user:trend_password@postgres:5432/trend_dashboard
      REDIS_URL: redis://redis:6379
      USE_MOCK_AI: "True"
    depends_on:
      - postgres
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

volumes:
  postgres_data:
```

Then run:
```bash
docker-compose up
```

## Testing the API

### 1. Check Health
```bash
curl http://localhost:8000/health
```

### 2. View API Documentation
Open in browser: http://localhost:8000/docs

Or view ReDoc: http://localhost:8000/redoc

### 3. Submit a Trend

```bash
curl -X POST http://localhost:8000/api/trends/submit \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://instagram.com/p/example123",
    "source_platform": "instagram",
    "submitted_by": "john_doe",
    "image_url": "https://example.com/image.jpg"
  }'
```

### 4. Get Trending Items

```bash
curl http://localhost:8000/api/trends/daily?limit=10
```

### 5. Get Dashboard Summary

```bash
curl http://localhost:8000/api/dashboard/summary
```

## Next Steps

1. **Read the API Documentation**: Visit http://localhost:8000/docs (Swagger UI)

2. **Explore Endpoints**: Try different filters and sorting options

3. **Create Mood Boards**: POST to `/api/moodboards` to create collections

4. **Add Monitoring Targets**: POST to `/api/monitoring/targets` to track hashtags/keywords

5. **Enable Real Claude AI** (Optional):
   - Get API key from https://console.anthropic.com
   - Set `CLAUDE_API_KEY` in `.env`
   - Set `USE_MOCK_AI=False`

## Common Commands

```bash
# View API docs
open http://localhost:8000/docs

# View database
psql -U trend_user -d trend_dashboard

# Check active trends
SELECT COUNT(*) FROM trend_items WHERE status='active';

# Stop the server
# Press Ctrl+C

# Deactivate venv
deactivate
```

## Troubleshooting

**Database connection error?**
- Check PostgreSQL is running: `psql -U postgres -l`
- Verify DATABASE_URL in `.env`

**Port 8000 already in use?**
```bash
uvicorn app.main:app --reload --port 8001
```

**Python version wrong?**
```bash
python3 --version  # Must be 3.11+
```

**Missing dependencies?**
```bash
pip install -r requirements.txt
```

## Demo Data

With `USE_MOCK_AI=True`, each trend submission generates realistic fashion data including:
- Fashion item categories (midi dress, crop top, etc.)
- Colors (navy blue, cream, sage green, etc.)
- Patterns (plaid, striped, floral, etc.)
- Style tags (cottagecore, y2k, quiet luxury, coquette, etc.)

This allows you to test the full system without API calls!

## What's Next?

- Build a frontend (React, Vue, etc.) that calls these endpoints
- Set up automated trend scraping tasks
- Implement webhooks for real-time updates
- Add user authentication
- Deploy to production (Railway, Heroku, AWS, etc.)

## Documentation

For detailed API documentation, visit: http://localhost:8000/docs

For more information, see README.md in this directory.
