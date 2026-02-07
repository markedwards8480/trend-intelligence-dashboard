# Trend Intelligence Dashboard Backend

A production-ready FastAPI backend for tracking fashion trends targeting junior customers (girls 15-28) for Mark Edwards Apparel.

## Features

- **Trend Submission & Analysis**: Submit URLs and automatically analyze them using Claude AI (with mock mode for development)
- **Trend Scoring**: Multi-factor scoring algorithm considering engagement, velocity, and recency
- **Mood Boards**: Create and manage curated collections of trend items
- **Monitoring**: Track specific hashtags, keywords, colors, and styles across platforms
- **Dashboard Analytics**: Aggregate statistics on trending categories, colors, and styles
- **Time-Series Metrics**: Historical tracking of trend performance over time
- **Multiple Platforms**: Support for Instagram, TikTok, Pinterest, and other fashion platforms

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **AI Integration**: Anthropic Claude API (optional)
- **Async**: Built on async/await patterns
- **Server**: Uvicorn
- **Containerization**: Docker

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration and settings
│   ├── main.py                # FastAPI app setup
│   ├── api/                   # API route handlers
│   │   ├── __init__.py
│   │   ├── trends.py          # Trend submission and retrieval
│   │   ├── moodboards.py      # Mood board management
│   │   ├── monitoring.py      # Monitoring target management
│   │   └── dashboard.py       # Dashboard statistics
│   ├── models/                # Database models
│   │   ├── __init__.py
│   │   ├── database.py        # SQLAlchemy setup
│   │   └── models.py          # SQLAlchemy ORM models
│   ├── schemas/               # Pydantic schemas
│   │   ├── __init__.py
│   │   └── schemas.py         # Request/response schemas
│   ├── services/              # Business logic
│   │   ├── __init__.py
│   │   ├── ai_service.py      # Claude API integration
│   │   └── scoring_service.py # Trend scoring algorithm
│   └── tasks/                 # Celery/background tasks
│       └── __init__.py
├── db/
│   └── schema.sql             # PostgreSQL schema
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── Dockerfile                # Docker build configuration
└── README.md                 # This file
```

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Redis (optional, for Celery)

### Installation

1. Clone the repository
2. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

3. Create a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up the database:
   ```bash
   # Option 1: Using raw SQL
   psql -U postgres -d trend_dashboard -f db/schema.sql

   # Option 2: Let SQLAlchemy create tables on app startup
   # Just run the app, tables will be created automatically
   ```

6. Configure environment variables in `.env`:
   ```bash
   DATABASE_URL=postgresql://postgres:password@localhost:5432/trend_dashboard
   REDIS_URL=redis://localhost:6379
   USE_MOCK_AI=True  # Set to False if you have Claude API key
   CLAUDE_API_KEY=your_api_key_here  # Optional
   ```

7. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### Trends
- `POST /api/trends/submit` - Submit a new trend URL
- `GET /api/trends/daily` - Get trending items (with filtering and sorting)
- `GET /api/trends/{id}` - Get specific trend details
- `POST /api/trends/{id}/analyze` - Re-run AI analysis on a trend
- `GET /api/trends/metrics/{id}` - Get time-series metrics for a trend

### Mood Boards
- `POST /api/moodboards` - Create a mood board
- `GET /api/moodboards` - List mood boards
- `GET /api/moodboards/{id}` - Get mood board with items
- `PUT /api/moodboards/{id}` - Update mood board
- `DELETE /api/moodboards/{id}` - Delete mood board

### Monitoring
- `POST /api/monitoring/targets` - Add monitoring target
- `GET /api/monitoring/targets` - List monitoring targets
- `GET /api/monitoring/targets/{id}` - Get specific target
- `PUT /api/monitoring/targets/{id}` - Update monitoring target
- `DELETE /api/monitoring/targets/{id}` - Delete monitoring target

### Dashboard
- `GET /api/dashboard/summary` - Get aggregated dashboard statistics

### Health
- `GET /health` - Health check endpoint
- `GET /` - Root endpoint with API info

## Configuration

All configuration is managed through the `app/config.py` file using pydantic-settings.

Key settings:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `CLAUDE_API_KEY`: Anthropic API key (optional)
- `USE_MOCK_AI`: Set to True for mock analysis (development mode)
- `CORS_ORIGINS`: Allowed CORS origins
- `AWS_*`: AWS credentials for S3 integration (optional)

## AI Analysis

The system supports two modes of AI analysis:

### Mock Mode (Development)
When `USE_MOCK_AI=True`, the system generates realistic mock fashion data:
- Fashion item categories (midi dress, crop top, cargo pants, etc.)
- Colors (navy blue, cream, olive green, etc.)
- Patterns (plaid, striped, floral, etc.)
- Style tags (cottagecore, y2k, quiet luxury, coquette, etc.)
- Price points (budget, mid, luxury, designer)

This allows full development without API costs.

### Real Mode (Production)
When `USE_MOCK_AI=False` and `CLAUDE_API_KEY` is set:
- Analyzes actual trend URLs using Claude API
- Extracts category, colors, patterns, style tags, and price point
- Generates narrative analysis text
- Falls back to mock mode if Claude API fails

## Trend Scoring Algorithm

The system uses a multi-factor scoring algorithm:

1. **Engagement Score** (0-100): Based on normalized likes, comments, shares, and views
2. **Velocity Score** (1.0-3.0x multiplier): Growth rate over 24 hours
3. **Recency Factor** (1.0-1.5x): Recent trends get boosted
4. **Cross-Platform Bonus**: Extra points for items appearing on multiple platforms
5. **Final Score**: Capped at 100, combines all factors

## Docker Deployment

Build and run with Docker:

```bash
# Build image
docker build -t trend-dashboard:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e REDIS_URL=redis://host:6379 \
  -e USE_MOCK_AI=True \
  trend-dashboard:latest
```

## Database Schema

### Tables
- `trend_items`: Main trend data with engagement metrics and scores
- `trend_metrics_history`: Historical metrics snapshots for time-series analysis
- `mood_boards`: Curated collections of trends
- `trending_hashtags`: Cross-platform hashtag tracking
- `monitoring_targets`: Configuration for monitoring specific items

All tables include appropriate indexes for query performance.

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Code Style
- Uses Python type hints throughout
- Follows PEP 8 conventions
- Uses pydantic for validation
- Async/await patterns for I/O operations

## Performance Considerations

- Database indexes on frequently queried columns (trend_score, velocity_score, etc.)
- Pagination support for all list endpoints (limit/offset)
- Time-series metrics stored separately for efficient querying
- JSONB fields for flexible categorical data
- Connection pooling via SQLAlchemy

## Security

- CORS middleware for cross-origin requests
- SQL injection protection via SQLAlchemy ORM
- Input validation via Pydantic schemas
- Environment variable management for secrets
- No sensitive data in logs

## Common Issues

### Database Connection Error
- Ensure PostgreSQL is running
- Check DATABASE_URL format
- Verify database exists: `psql -l`

### Claude API Errors
- Falls back to mock mode automatically
- Check CLAUDE_API_KEY validity
- Ensure API rate limits not exceeded

### Import Errors
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check Python version: 3.11+

## Future Enhancements

- Celery task queue for async processing
- Real-time trend updates via WebSockets
- Image analysis capabilities
- Advanced filtering and search
- User authentication and authorization
- Notification system for trend alerts
- Batch import from CSV/JSON

## Support

For issues or questions, contact the development team or create an issue in the repository.

## License

Copyright Mark Edwards Apparel. All rights reserved.
