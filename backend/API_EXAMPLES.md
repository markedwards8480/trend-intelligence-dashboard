# API Examples

Complete examples of all API endpoints with curl commands and expected responses.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication is required. In production, add JWT or API key authentication.

---

## Health & Info Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "app": "Trend Intelligence Dashboard",
  "version": "1.0.0"
}
```

### API Info
```bash
curl http://localhost:8000/
```

Response:
```json
{
  "message": "Welcome to Trend Intelligence Dashboard",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

## Trends Endpoints

### Submit a New Trend
```bash
curl -X POST http://localhost:8000/api/trends/submit \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.instagram.com/p/example123abc",
    "source_platform": "instagram",
    "submitted_by": "fashion_analyst_001",
    "image_url": "https://example.com/image.jpg"
  }'
```

Response (with mock AI analysis):
```json
{
  "id": 1,
  "url": "https://www.instagram.com/p/example123abc",
  "source_platform": "instagram",
  "image_url": "https://example.com/image.jpg",
  "submitted_by": "fashion_analyst_001",
  "submitted_at": "2024-02-07T10:30:00+00:00",
  "category": "midi dress",
  "subcategory": null,
  "colors": ["navy blue", "cream"],
  "patterns": ["solid"],
  "style_tags": ["cottagecore", "quiet luxury"],
  "price_point": "mid",
  "likes": 12500,
  "comments": 450,
  "shares": 320,
  "views": 125000,
  "engagement_rate": 14.5,
  "trend_score": 82.45,
  "velocity_score": 45.67,
  "cross_platform_score": 0.0,
  "scraped_at": null,
  "last_updated": "2024-02-07T10:30:00+00:00",
  "status": "active",
  "ai_analysis_text": "This item exemplifies current trending aesthetics. The styling combines elements of popular substyles while maintaining contemporary appeal to junior fashion consumers..."
}
```

### Get Daily Trending Items
```bash
# Get top 20 trends
curl "http://localhost:8000/api/trends/daily?limit=20&offset=0"

# Filter by category
curl "http://localhost:8000/api/trends/daily?category=midi%20dress&limit=10"

# Filter by platform
curl "http://localhost:8000/api/trends/daily?source_platform=tiktok&limit=10"

# Sort by velocity instead of trend score
curl "http://localhost:8000/api/trends/daily?sort_by=velocity_score&limit=10"

# Sort by most recent
curl "http://localhost:8000/api/trends/daily?sort_by=submitted_at&limit=10"

# Complex filter: recent tiktok trends about crop tops
curl "http://localhost:8000/api/trends/daily?source_platform=tiktok&category=crop%20top&sort_by=submitted_at"
```

Response:
```json
{
  "items": [
    {
      "id": 1,
      "url": "https://www.instagram.com/p/example123abc",
      "source_platform": "instagram",
      "category": "midi dress",
      "colors": ["navy blue", "cream"],
      "style_tags": ["cottagecore", "quiet luxury"],
      "trend_score": 82.45,
      "velocity_score": 45.67,
      "status": "active",
      ...
    },
    {
      "id": 2,
      "url": "https://www.tiktok.com/video/example456def",
      "source_platform": "tiktok",
      "category": "crop top",
      "colors": ["blush pink", "white"],
      "style_tags": ["y2k", "coquette"],
      "trend_score": 76.23,
      "velocity_score": 52.34,
      "status": "active",
      ...
    }
  ],
  "total": 245,
  "limit": 20,
  "offset": 0
}
```

### Get Specific Trend
```bash
curl http://localhost:8000/api/trends/1
```

Response:
```json
{
  "id": 1,
  "url": "https://www.instagram.com/p/example123abc",
  "source_platform": "instagram",
  "image_url": "https://example.com/image.jpg",
  "submitted_by": "fashion_analyst_001",
  "submitted_at": "2024-02-07T10:30:00+00:00",
  "category": "midi dress",
  "colors": ["navy blue", "cream"],
  "patterns": ["solid"],
  "style_tags": ["cottagecore", "quiet luxury"],
  "price_point": "mid",
  "likes": 12500,
  "comments": 450,
  "shares": 320,
  "views": 125000,
  "engagement_rate": 14.5,
  "trend_score": 82.45,
  "velocity_score": 45.67,
  "cross_platform_score": 0.0,
  "status": "active",
  "ai_analysis_text": "..."
}
```

### Re-analyze a Trend
```bash
curl -X POST http://localhost:8000/api/trends/1/analyze
```

Response: Updated trend item with fresh AI analysis

### Get Trend Metrics History
```bash
# Get last 24 hours of metrics
curl http://localhost:8000/api/trends/1/metrics?hours=24

# Get last week of metrics
curl http://localhost:8000/api/trends/1/metrics?hours=168

# Get full month
curl http://localhost:8000/api/trends/1/metrics?hours=720
```

Response:
```json
[
  {
    "recorded_at": "2024-02-06T10:30:00+00:00",
    "likes": 10000,
    "comments": 350,
    "shares": 250,
    "views": 100000,
    "trend_score": 78.5
  },
  {
    "recorded_at": "2024-02-06T12:30:00+00:00",
    "likes": 11200,
    "comments": 400,
    "shares": 280,
    "views": 112000,
    "trend_score": 80.2
  },
  {
    "recorded_at": "2024-02-07T10:30:00+00:00",
    "likes": 12500,
    "comments": 450,
    "shares": 320,
    "views": 125000,
    "trend_score": 82.45
  }
]
```

---

## Mood Boards Endpoints

### Create a Mood Board
```bash
curl -X POST http://localhost:8000/api/moodboards \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Spring Cottage Core Collection",
    "description": "Latest cottagecore inspired trends for spring 2024",
    "category": "spring_2024",
    "created_by": "curator_001",
    "item_ids": [1, 2, 3, 5, 7]
  }'
```

Response:
```json
{
  "id": 1,
  "title": "Spring Cottage Core Collection",
  "description": "Latest cottagecore inspired trends for spring 2024",
  "created_by": "curator_001",
  "created_at": "2024-02-07T10:30:00+00:00",
  "updated_at": "2024-02-07T10:30:00+00:00",
  "category": "spring_2024",
  "items": [1, 2, 3, 5, 7]
}
```

### List Mood Boards
```bash
# Get all mood boards
curl http://localhost:8000/api/moodboards

# Filter by creator
curl "http://localhost:8000/api/moodboards?created_by=curator_001"

# Filter by category
curl "http://localhost:8000/api/moodboards?category=spring_2024"

# Pagination
curl "http://localhost:8000/api/moodboards?limit=10&offset=0"
```

Response:
```json
[
  {
    "id": 1,
    "title": "Spring Cottage Core Collection",
    "description": "Latest cottagecore inspired trends for spring 2024",
    "created_by": "curator_001",
    "created_at": "2024-02-07T10:30:00+00:00",
    "updated_at": "2024-02-07T10:30:00+00:00",
    "category": "spring_2024",
    "items": [1, 2, 3, 5, 7]
  }
]
```

### Get Mood Board with Items
```bash
curl http://localhost:8000/api/moodboards/1
```

Response:
```json
{
  "id": 1,
  "title": "Spring Cottage Core Collection",
  "description": "Latest cottagecore inspired trends for spring 2024",
  "created_by": "curator_001",
  "created_at": "2024-02-07T10:30:00+00:00",
  "updated_at": "2024-02-07T10:30:00+00:00",
  "category": "spring_2024",
  "items": [1, 2, 3, 5, 7],
  "trend_items": [
    {
      "id": 1,
      "url": "https://www.instagram.com/p/example123abc",
      "category": "midi dress",
      ...
    },
    ...
  ]
}
```

### Update Mood Board
```bash
curl -X PUT http://localhost:8000/api/moodboards/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Spring Cottage Core",
    "items": [1, 2, 3, 5, 7, 9, 11]
  }'
```

### Delete Mood Board
```bash
curl -X DELETE http://localhost:8000/api/moodboards/1
```

Response:
```json
{
  "message": "Mood board deleted successfully"
}
```

---

## Monitoring Endpoints

### Add Monitoring Target
```bash
curl -X POST http://localhost:8000/api/monitoring/targets \
  -H "Content-Type: application/json" \
  -d '{
    "type": "hashtag",
    "value": "cottagecore",
    "platform": "instagram",
    "added_by": "analyst_001"
  }'
```

Response:
```json
{
  "id": 1,
  "type": "hashtag",
  "value": "cottagecore",
  "platform": "instagram",
  "active": true,
  "added_by": "analyst_001",
  "added_at": "2024-02-07T10:30:00+00:00"
}
```

### List Monitoring Targets
```bash
# Get all targets
curl http://localhost:8000/api/monitoring/targets

# Filter by platform
curl "http://localhost:8000/api/monitoring/targets?platform=instagram"

# Filter by type
curl "http://localhost:8000/api/monitoring/targets?type=hashtag"

# Only active targets
curl "http://localhost:8000/api/monitoring/targets?active=true"

# Combine filters
curl "http://localhost:8000/api/monitoring/targets?platform=tiktok&type=keyword&active=true"
```

### Get Specific Target
```bash
curl http://localhost:8000/api/monitoring/targets/1
```

### Update Monitoring Target
```bash
# Toggle active status
curl -X PUT http://localhost:8000/api/monitoring/targets/1 \
  -H "Content-Type: application/json" \
  -d '{"active": false}'

# Change value
curl -X PUT http://localhost:8000/api/monitoring/targets/1 \
  -H "Content-Type: application/json" \
  -d '{"value": "y2k_fashion"}'
```

### Delete Monitoring Target
```bash
curl -X DELETE http://localhost:8000/api/monitoring/targets/1
```

---

## Dashboard Endpoints

### Get Dashboard Summary
```bash
# Get stats for last 7 days (default)
curl http://localhost:8000/api/dashboard/summary

# Get stats for last 30 days
curl "http://localhost:8000/api/dashboard/summary?days=30"

# Get stats for last 24 hours
curl "http://localhost:8000/api/dashboard/summary?days=1"
```

Response:
```json
{
  "top_categories": [
    {
      "name": "midi dress",
      "count": 45,
      "trend_score": 78.5
    },
    {
      "name": "crop top",
      "count": 38,
      "trend_score": 75.2
    },
    {
      "name": "cargo pants",
      "count": 32,
      "trend_score": 72.1
    }
  ],
  "trending_colors": [
    {
      "color": "navy blue",
      "count": 78
    },
    {
      "color": "cream",
      "count": 65
    },
    {
      "color": "sage green",
      "count": 52
    }
  ],
  "trending_styles": [
    {
      "style": "cottagecore",
      "count": 89
    },
    {
      "style": "quiet luxury",
      "count": 76
    },
    {
      "style": "y2k",
      "count": 64
    }
  ],
  "velocity_leaders": [
    {
      "id": 1,
      "title": "https://www.instagram.com/p/example123abc...",
      "category": "midi dress",
      "velocity_score": 95.5,
      "trend_score": 82.45
    },
    {
      "id": 3,
      "title": "https://www.tiktok.com/video/example456def...",
      "category": "crop top",
      "velocity_score": 88.2,
      "trend_score": 76.23
    }
  ],
  "total_active_trends": 245,
  "new_today": 12,
  "timestamp": "2024-02-07T10:30:00+00:00"
}
```

---

## Error Responses

### 404 Not Found
```json
{
  "detail": "Trend not found"
}
```

### 400 Bad Request
```json
{
  "detail": "URL already submitted"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "url"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## Interactive API Documentation

Visit `http://localhost:8000/docs` to test all endpoints interactively using Swagger UI.

Visit `http://localhost:8000/redoc` for ReDoc documentation.

---

## Batch Operations Examples

### Submit multiple trends
```bash
# Create a script to submit multiple URLs
for url in "https://instagram.com/p/123" "https://instagram.com/p/456" "https://tiktok.com/video/789"; do
  curl -X POST http://localhost:8000/api/trends/submit \
    -H "Content-Type: application/json" \
    -d "{\"url\": \"$url\", \"source_platform\": \"instagram\", \"submitted_by\": \"batch_import\"}"
  sleep 1  # Rate limit: 1 second between requests
done
```

---

## Performance Tips

1. **Use pagination**: Always limit results to avoid loading too much data
   ```bash
   curl "http://localhost:8000/api/trends/daily?limit=50&offset=0"
   ```

2. **Filter early**: Use filters to reduce data processing
   ```bash
   curl "http://localhost:8000/api/trends/daily?category=midi%20dress&source_platform=instagram"
   ```

3. **Cache results**: Popular endpoints like dashboard summary can be cached
   ```bash
   curl -H "Cache-Control: max-age=300" http://localhost:8000/api/dashboard/summary
   ```

4. **Use appropriate time windows**: For metrics, query only needed date ranges
   ```bash
   curl "http://localhost:8000/api/trends/1/metrics?hours=24"
   ```

---

## Testing with Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Submit a trend
response = requests.post(
    f"{BASE_URL}/api/trends/submit",
    json={
        "url": "https://instagram.com/p/example",
        "source_platform": "instagram",
        "submitted_by": "test_user"
    }
)
trend = response.json()
print(f"Created trend: {trend['id']}")

# Get trending items
response = requests.get(
    f"{BASE_URL}/api/trends/daily",
    params={"limit": 10, "sort_by": "trend_score"}
)
trends = response.json()
print(f"Found {trends['total']} trending items")

# Get dashboard
response = requests.get(f"{BASE_URL}/api/dashboard/summary")
dashboard = response.json()
print(f"Top category: {dashboard['top_categories'][0]['name']}")
```
