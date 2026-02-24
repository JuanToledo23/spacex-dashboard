# SpaceX Dashboard — Backend API

REST API built with FastAPI that aggregates, caches, and serves data from the [SpaceX API](https://github.com/r-spacex/SpaceX-API). Acts as a gateway between the frontend and the upstream API, adding caching, data enrichment, and derived analytics (economics, emissions).

## Tech Stack

| Technology        | Purpose                                  |
|-------------------|------------------------------------------|
| FastAPI           | Async web framework with OpenAPI support |
| httpx             | Async HTTP client for SpaceX API calls   |
| Redis (hiredis)   | TTL-based caching with stampede prevention |
| Pydantic          | Request/response validation and schemas  |
| pydantic-settings | Environment-based configuration          |
| structlog         | Structured JSON logging with trace IDs   |
| Pytest            | Testing framework                        |
| Ruff              | Linting and formatting                   |

## Architecture

```
SpaceX API v4/v5
       ▲
       │
   ┌───┴───┐
   │ Client │  spacex_client.py — HTTP calls with retry and timeout
   └───┬───┘
       │
   ┌───┴─────┐
   │ Services │  Business logic, data transformation, cache orchestration
   └───┬─────┘
       │
   ┌───┴────┐
   │ Routes  │  FastAPI route handlers (thin layer)
   └───┬────┘
       │
   ┌───┴────────────┐
   │ Middleware      │  Request ID, structured logging, global rate limiting (120 req/min)
   └───┬────────────┘
       │
   ┌───┴───┐
   │ Cache  │  Redis with TTL + SET NX lock for stampede prevention
   └───────┘
```

Each request flows through this pipeline:

1. **Middleware** assigns a trace ID, logs the request, and enforces the global rate limit (120 requests per minute per IP via Redis)
2. **Route** receives the HTTP request and delegates to a service
3. **Service** checks the Redis cache. On hit, returns cached data immediately
4. On miss, the service acquires a Redis lock (`SET NX`), calls the **SpaceX client**, transforms the response, caches it, and returns
5. Concurrent requests that arrive during a cache miss wait briefly and read from cache once populated

## Setup

### Prerequisites

- Python 3.11+
- Redis running locally (default: `localhost:6379`)

### Installation

```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # macOS/Linux
pip install -r requirements-dev.txt
```

### Run

```bash
uvicorn app.main:app --reload
```

The API starts at http://localhost:8000. Interactive docs at http://localhost:8000/docs.

## Environment Variables

| Variable           | Default                            | Description                    |
|--------------------|------------------------------------|--------------------------------|
| `SPACEX_API_BASE`  | `https://api.spacexdata.com`       | SpaceX API base URL            |
| `REDIS_URL`        | `redis://localhost:6379/0`         | Redis connection string        |
| `SPACEX_TIMEOUT`   | `10`                               | HTTP timeout in seconds        |
| `SPACEX_RETRIES`   | `2`                                | Retry attempts for failed calls|
| `ROCKETS_TTL`      | `86400`                            | Rockets cache TTL (seconds)    |
| `LAUNCHES_TTL`     | `120`                              | Launches cache TTL             |
| `STARLINK_TTL`     | `300`                              | Starlink cache TTL             |
| `DASHBOARD_TTL`    | `300`                              | Dashboard cache TTL            |
| `CORES_TTL`        | `86400`                            | Cores/fleet cache TTL          |
| `LAUNCHPADS_TTL`   | `86400`                            | Launchpads cache TTL           |
| `HISTORY_TTL`      | `86400`                            | History cache TTL              |
| `LANDING_TTL`      | `86400`                            | Landing pads cache TTL         |
| `ROADSTER_TTL`     | `86400`                            | Roadster cache TTL             |
| `ECONOMICS_TTL`    | `300`                              | Economics cache TTL            |
| `EMISSIONS_TTL`    | `300`                              | Emissions cache TTL            |
| `GROQ_API_KEY`     | *(empty)*                          | Groq API key (optional, enables AI) |
| `GROQ_MODEL`       | `llama-3.3-70b-versatile`          | LLM model for AI features     |

All values can be set via environment variables or a `.env` file. See [.env.example](../.env.example).

## API Reference

### Health

| Method | Path      | Description               |
|--------|-----------|---------------------------|
| GET    | `/health` | Redis connectivity check  |

### Dashboard

| Method | Path             | Description                                    |
|--------|------------------|------------------------------------------------|
| GET    | `/api/dashboard` | Aggregated stats, launch cadence, cross-domain recommended actions, launchpad summaries |

### Rockets

| Method | Path                 | Description                            |
|--------|----------------------|----------------------------------------|
| GET    | `/api/rockets`       | All rockets with launch count and success rate |
| GET    | `/api/rockets/{id}`  | Detailed rocket info (stages, dimensions, images) |

### Launches

| Method | Path                  | Description                     |
|--------|-----------------------|---------------------------------|
| GET    | `/api/launches`       | Paginated and filterable list   |
| GET    | `/api/launches/{id}`  | Full launch detail (crew, payloads, cores, images) |

**Query parameters for `/api/launches`:**

| Param       | Type   | Default    | Description                       |
|-------------|--------|------------|-----------------------------------|
| `page`      | int    | 1          | Page number                       |
| `limit`     | int    | 20         | Items per page (max 100)          |
| `success`   | bool   | —          | Filter by outcome                 |
| `upcoming`  | bool   | —          | Filter upcoming or past missions  |
| `rocket_id` | string | —          | Filter by rocket ID               |
| `from_date` | string | —          | ISO date lower bound              |
| `to_date`   | string | —          | ISO date upper bound              |
| `sort`      | string | `date_utc` | Sort field                        |
| `order`     | string | `desc`     | Sort direction (`asc` or `desc`)  |

### Starlink

| Method | Path                      | Description                     |
|--------|---------------------------|---------------------------------|
| GET    | `/api/starlink`           | Paginated satellite list        |
| GET    | `/api/starlink/positions` | Positions for globe visualization |
| GET    | `/api/starlink/stats`     | Aggregate statistics by version |

**Query parameters for `/api/starlink`:**

| Param     | Type   | Default | Description                    |
|-----------|--------|---------|--------------------------------|
| `page`    | int    | 1       | Page number                    |
| `limit`   | int    | 20      | Items per page (max 100)       |
| `version` | string | —       | Filter by satellite version    |

### Fleet

| Method | Path              | Description                        |
|--------|-------------------|------------------------------------|
| GET    | `/api/cores/stats`| Booster reuse and landing statistics |

### Launchpads

| Method | Path              | Description                          |
|--------|-------------------|--------------------------------------|
| GET    | `/api/launchpads` | All launch sites with success rates  |

### Analytics

| Method | Path              | Description                                    |
|--------|-------------------|------------------------------------------------|
| GET    | `/api/economics`  | Cost per kg, annual spend, spend by vehicle    |
| GET    | `/api/emissions`  | CO2 estimates, fuel breakdown, reuse savings   |

### Explore

| Method | Path             | Description                             |
|--------|------------------|-----------------------------------------|
| GET    | `/api/history`   | Major SpaceX milestones                 |
| GET    | `/api/landing`   | Landing pad data, locations, statistics |
| GET    | `/api/roadster`  | Roadster/Starman live telemetry         |

### AI

| Method | Path               | Description                              |
|--------|--------------------|------------------------------------------|
| GET    | `/api/ai/status`   | Check if AI features are available       |
| POST   | `/api/ai/chat`     | Chat with AI assistant (SpaceX context)  |
| GET    | `/api/ai/fun-fact` | Random AI-generated SpaceX fun fact      |

**Request body for `/api/ai/chat`:**

```json
{
  "message": "Which rocket has the best success rate?",
  "history": [
    { "role": "user", "content": "Previous question" },
    { "role": "assistant", "content": "Previous answer" }
  ]
}
```

The AI service uses Groq (Llama 3.3 70B) to generate responses grounded in real SpaceX data. The chat context includes data from all dashboard sources: missions, rockets, fleet/booster stats, Starlink satellites, economics, emissions, historical milestones, landing pads, launch sites, and Roadster telemetry. Chat responses are formatted with markdown (bold, lists, paragraphs). The fun-fact endpoint generates a short, surprising curiosity (max ~25 words) that varies on each call. If `GROQ_API_KEY` is not set, the status endpoint returns `{ "available": false }` and the other AI endpoints return a 503 or helpful message.

**Input sanitization:** The `ChatRequest` schema enforces a 2,000 character limit on messages and uses a `field_validator` to strip common prompt-injection patterns (e.g., `ignore previous instructions`, `system:`, `[INST]`) before the message reaches the LLM. AI endpoints also have dedicated rate limits: chat is limited to 20 requests per minute and fun-fact to 10 requests per minute.

### Notifications

| Method | Path                          | Description                              |
|--------|-------------------------------|------------------------------------------|
| GET    | `/api/notifications/stream`   | SSE stream for real-time notifications  |
| POST   | `/api/notifications/send`     | Send test notification                   |

### Error Response Format

All errors follow a consistent structure:

```json
{
  "code": "RESOURCE_NOT_FOUND",
  "message": "Rocket not found",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

The `trace_id` is generated per request (via middleware) and included in both the response and structured logs for end-to-end tracing.

## Caching

Every cacheable resource uses the same pattern:

1. Check Redis for cached data
2. On hit → return immediately
3. On miss → acquire a `SET NX` lock, fetch from SpaceX API, cache the result, release the lock
4. Concurrent requests during a miss wait briefly and read from cache

This prevents cache stampedes where many requests would simultaneously hit the upstream API.

| Resource   | TTL    |
|------------|--------|
| Rockets    | 24 h   |
| Launches   | 2 min  |
| Starlink   | 5 min  |
| Dashboard  | 5 min  |
| Economics  | 5 min  |
| Emissions  | 5 min  |
| Cores      | 24 h   |
| Launchpads | 24 h   |
| History    | 24 h   |
| Landing    | 24 h   |
| Roadster   | 24 h   |

## Testing

```bash
# Run all tests
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=term-missing
```

| Metric | Value |
|---|---|
| Total tests | **203** |
| Code coverage | **96.12%** |
| Enforced minimum | **90%** (`--cov-fail-under=90` in CI) |
| Test files | 24 (routes, services, cache, middleware, rate_limit, AI, notifications, etc.) |

Tests cover all 14 API route modules, all 15 service modules, error handling, caching behavior, and the AI service. Requires Redis running locally — the CI pipeline uses a Redis service container.

## Linting

```bash
ruff check .           # Lint
ruff format --check .  # Format check
ruff format .          # Auto-format
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/         # One file per resource (14 route modules)
│   │   ├── middleware.py   # Request ID, structured logging, rate limiting (120 req/min)
│   │   └── rate_limit.py   # Per-endpoint rate limiting
│   ├── cache/
│   │   ├── helpers.py       # cached_fetch utility
│   │   └── redis_cache.py   # Redis connection management
│   ├── clients/
│   │   └── spacex_client.py # HTTP client with retry logic
│   ├── schemas/             # Pydantic models (14 modules, with input sanitization on AI schemas)
│   ├── services/            # Business logic (15 modules, one per resource)
│   ├── utils/
│   │   └── calculations.py  # Shared helpers (success_rate, etc.)
│   ├── config.py            # Settings from environment
│   └── main.py              # FastAPI app + lifespan
├── tests/                   # 24 test files (routes, services, cache, middleware, rate_limit, AI, notifications, etc.)
├── Dockerfile               # Multi-stage build with HEALTHCHECK instruction
├── pyproject.toml           # Ruff config + pytest-cov (fail_under=90)
├── requirements.txt
└── requirements-dev.txt     # Adds pytest, ruff
```
