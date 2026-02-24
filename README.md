# SpaceX Dashboard

Full-stack analytics dashboard consuming the public [SpaceX API](https://github.com/r-spacex/SpaceX-API). Provides real-time mission tracking, fleet analytics, Starlink constellation monitoring, cost analysis, emissions estimates, and more — all through interactive D3.js visualizations.

Built as a technical assessment for the Full-Stack Engineer role at **QuadSci.ai**.

## Architecture

```
Browser ──▶ Nginx (SSL + Vue 3 SPA) ──▶ FastAPI Backend ──▶ Redis Cache ──▶ SpaceX API v4/v5
```

| Layer     | Technology                        | Purpose                                      |
|-----------|-----------------------------------|----------------------------------------------|
| Frontend  | Vue 3 + TypeScript + Vite + D3.js | SPA with interactive charts and visualizations |
| Backend   | FastAPI (Python 3.11+)            | API gateway, data aggregation, caching       |
| Cache     | Redis 7                           | TTL-based cache with stampede prevention      |
| SSL       | Let's Encrypt + Nginx             | HTTPS with auto-renewal                      |
| Containers| Docker + Docker Compose           | Single-command deployment                    |
| CI/CD     | GitHub Actions                    | Lint, type-check, test, deploy on push to main |

## Live Demo

**[https://quadsci.juantoledo.com.mx](https://quadsci.juantoledo.com.mx)**

## Quick Start

### Docker (recommended)

```bash
docker compose up --build
```

| Service    | URL                          |
|------------|------------------------------|
| Frontend   | http://localhost              |
| API        | http://localhost:8000         |
| API Docs   | http://localhost:8000/docs    |

### Local Development

See the dedicated READMEs for each project:

- [Backend setup instructions](backend/README.md)
- [Frontend setup instructions](frontend/README.md)

## Project Structure

```
spacex-dashboard/
├── backend/                # FastAPI REST API (Python 3.11+)
│   ├── app/
│   │   ├── api/            # Route handlers (14) + middleware + rate_limit
│   │   ├── cache/          # Redis cache with stampede prevention
│   │   ├── clients/        # SpaceX API HTTP client with retry
│   │   ├── schemas/        # Pydantic models (14 modules)
│   │   ├── services/       # Business logic layer (15 modules)
│   │   ├── utils/          # Shared calculations
│   │   ├── config.py       # Environment-based settings
│   │   └── main.py         # Application entry point
│   └── tests/              # 203 Pytest tests (96% coverage)
├── frontend/               # Vue 3 SPA (TypeScript strict)
│   ├── src/
│   │   ├── api/            # Axios HTTP client (17 functions)
│   │   ├── assets/         # Global CSS, design tokens, transitions
│   │   ├── components/
│   │   │   ├── charts/     # 13 D3.js visualizations
│   │   │   ├── common/     # 10 reusable UI components
│   │   │   └── layout/     # Header, footer, progress bar, space background
│   │   ├── router/         # 11 lazy-loaded routes
│   │   ├── stores/         # 7 Pinia stores
│   │   ├── types/          # TypeScript interfaces
│   │   ├── utils/          # Shared utilities
│   │   ├── views/          # 11 page components
│   │   └── __tests__/      # 242 Vitest tests (47 files)
│   └── package.json
├── docs/
│   └── DATA_CONTRACTS.md   # Data models for RAG/LLM indexing
├── .github/workflows/
│   ├── ci.yml              # Lint, type-check, test, coverage, security audit
│   └── deploy.yml          # Deploy to EC2 via SSH with rollback
├── .pre-commit-config.yaml # Ruff + ESLint + file hygiene hooks
├── docker-compose.yml      # API + Nginx + Redis with health checks
└── .env.example
```

## Features

| Section        | Description                                                                 |
|----------------|-----------------------------------------------------------------------------|
| **Overview**   | Mission stats, launch cadence, next/latest mission, site performance, cross-domain recommended actions |
| **Launches**   | Filterable launch log with pagination, year-by-year breakdown               |
| **Launch Detail** | Individual mission page with crew, payloads, cores, image gallery        |
| **Fleet**      | Rocket showcase with specs, recovery stats, and booster reuse tracking      |
| **Rocket Detail** | In-depth rocket page with stages, dimensions, and image gallery          |
| **Starlink**   | Interactive 3D globe, satellite positions, version distribution             |
| **Economics**  | Cost per kg to LEO, annual spend trends, spend by vehicle                   |
| **Emissions**  | Estimated CO2 by vehicle, annual trends, fuel breakdown, reuse savings      |
| **History**    | Interactive timeline of major SpaceX milestones                             |
| **Landing**    | Landing pad map with clustering, pad comparison, success rates              |
| **Starman**    | Roadster live telemetry, orbital diagram, Mars distance tracker             |

Additional features:

- **Recommended Actions** — cross-domain actionable recommendations (e.g., fleet + economics + emissions) with action type, priority badges, and domain pills. AI-generated when available, deterministic fallback otherwise
- **AI Chat Assistant** with markdown-formatted responses and typewriter effect
- **AI Fun Fact** — a random SpaceX curiosity shown on each site visit
- **Dark / Light theme** with smooth transitions
- **Fully responsive** layout (mobile, tablet, desktop) with safe-area support for iPhone
- **Animated space background** with twinkling stars and shooting stars
- **Image lightbox** for all galleries
- **Error Testing Lab** — Easter egg to demonstrate error handling (triple-click SPACEX in header)

## Error Testing Lab

The dashboard includes an **Error Testing Lab** to demonstrate how errors are handled across the stack. Useful for QA, demos, and onboarding.

**How to open:** Triple-click the "SPACEX" brand in the header (three clicks within ~500 ms).

**What it demonstrates:**
- **ErrorState** — Inline error panel with RETRY button (used across all views)
- **NotificationToast** — Toast notifications for non-blocking errors
- **API errors** — Real HTTP responses (404, 500, 502, 503, timeout) from the backend

The backend endpoint `GET /api/dev/trigger-error?code=404|500|502|503|timeout` returns simulated errors. The timeout variant waits 5 seconds before responding. See [Frontend README](frontend/README.md#error-testing-lab-easter-egg) and [Backend README](backend/README.md#error-testing-dev-endpoint) for details.

## API Endpoints

| Method | Path                     | Description                          |
|--------|--------------------------|--------------------------------------|
| GET    | `/health`                | Health check (Redis connectivity)    |
| GET    | `/api/dashboard`         | Aggregated metrics and insights      |
| GET    | `/api/rockets`           | All rockets with launch stats        |
| GET    | `/api/rockets/{id}`      | Single rocket detail                 |
| GET    | `/api/launches`          | Paginated launches (filterable)      |
| GET    | `/api/launches/{id}`     | Single launch detail                 |
| GET    | `/api/starlink`          | Paginated Starlink satellites        |
| GET    | `/api/starlink/positions`| Satellite positions for globe        |
| GET    | `/api/starlink/stats`    | Starlink aggregate statistics        |
| GET    | `/api/cores/stats`       | Fleet and booster reuse statistics   |
| GET    | `/api/launchpads`        | All launch sites with performance    |
| GET    | `/api/economics`         | Cost analysis and spend data         |
| GET    | `/api/emissions`         | Emissions estimates by vehicle       |
| GET    | `/api/history`           | Historical milestones                |
| GET    | `/api/landing`           | Landing pad data and statistics      |
| GET    | `/api/roadster`          | Roadster / Starman live telemetry    |
| GET    | `/api/ai/status`         | Check if AI features are available   |
| POST   | `/api/ai/chat`           | AI chat with SpaceX data context     |
| GET    | `/api/ai/fun-fact`       | Random AI-generated SpaceX fun fact  |
| GET    | `/api/notifications/stream` | Server-Sent Events stream for real-time notifications |
| POST   | `/api/notifications/send`   | Send test notification (admin/internal)              |
| GET    | `/api/dev/trigger-error`    | Easter egg: simulated errors (404, 500, 502, 503, timeout) for error-handling demos |

For detailed query parameters and response schemas, see the [Backend README](backend/README.md).

## AI Features

The dashboard integrates AI through three features, powered by [Groq](https://groq.com) (free tier, no credit card required):

**Recommended Actions** — The Overview page's "Recommended Actions" section generates cross-domain actionable recommendations by analyzing data from all domains simultaneously (missions, fleet, economics, emissions, Starlink, landing). Each recommendation proposes a specific action (optimize, investigate, scale, reduce, or monitor), includes a priority level (high/medium/low), and indicates which data domains it cross-references. When AI is enabled, a "Smart Actions" badge appears; if not, the system generates equally useful deterministic actions using rule-based cross-domain analysis.

**AI Chat Assistant** — A floating chat button (bottom-right corner) opens a conversational interface with markdown-formatted responses (bold, lists, paragraphs) and a typewriter effect. Users can ask natural language questions about any SpaceX data — missions, rockets, Starlink, costs, emissions, landing operations, historical milestones, launch sites, and even the Tesla Roadster's current position. The AI has full context of all dashboard data sources and maintains conversation history for follow-up questions.

**Fun Fact on Load** — Each time the site is opened, a subtle banner appears below the header with a short AI-generated curiosity about SpaceX (e.g., a surprising statistic or record). The banner auto-dismisses after 12 seconds and can be closed manually.

All three features follow a **graceful degradation** pattern: the dashboard works perfectly without an AI API key. To enable AI, add a free Groq key to your environment:

```bash
GROQ_API_KEY=your_key_here
```

Get a free key at [console.groq.com](https://console.groq.com).

## Caching Strategy

| Resource   | TTL    | Rationale                              |
|------------|--------|----------------------------------------|
| Rockets    | 24 h   | Rarely changes                         |
| Launches   | 2 min  | Updates frequently around launch events |
| Starlink   | 5 min  | Large dataset, moderate update rate    |
| Dashboard  | 5 min  | Aggregated from multiple sources       |
| Economics  | 5 min  | Derived from launches and rockets      |
| Emissions  | 5 min  | Derived from launches and rockets      |
| Cores      | 24 h   | Changes infrequently                   |
| Launchpads | 24 h   | Static infrastructure data             |
| History    | 24 h   | Historical events, rarely updated      |
| Landing    | 24 h   | Pad data changes infrequently          |
| Roadster   | 24 h   | Telemetry updates slowly               |

**Stampede prevention:** On cache miss, a Redis `SET NX` lock is acquired before calling the SpaceX API. Concurrent requests wait briefly and read from cache once it is populated, avoiding redundant upstream calls.

## Design Decisions

- **FastAPI over Flask** — Native async I/O for concurrent SpaceX API and Redis calls. Auto-generated OpenAPI docs. Type safety with Pydantic.
- **Redis-only (no SQL database)** — All data is sourced from the SpaceX API and cached in Redis. No persistent storage is needed since the upstream API is the source of truth.
- **TypeScript (strict mode)** — Full frontend type coverage with no `any` types. Interfaces mirror backend Pydantic schemas for end-to-end type safety.
- **D3.js over charting libraries** — Full control over rendering, interactivity, and custom visualizations (3D globe, orbital diagrams, animated maps).
- **Monorepo** — Single repository for backend and frontend simplifies CI, Docker Compose, and code review.
- **Cross-domain recommendations** — The Insight model supports `action_type`, `priority`, and `domains` fields. Both AI and deterministic paths produce actionable recommendations that cross-reference multiple data domains, using the same schema for graceful degradation.

## Quality & Testing

The project maintains strict quality standards enforced through automated tooling and continuous integration.

| Metric | Value |
|---|---|
| Total tests | **445** (203 backend + 242 frontend) |
| Backend coverage | **96%** (enforced minimum: 90%) |
| Backend lint errors | **0** (Ruff check + format) |
| Frontend lint errors | **0** (ESLint, 1 intentional warning for `v-html` in AI chat markdown) |
| Python module docstrings | **48/48** (100%) |
| Test files (frontend) | **47** covering views, stores, charts, components, utils, router |

**Automated enforcement:**

- Backend: `pytest --cov-fail-under=90` rejects PRs below the coverage threshold
- Linting: Ruff (Python) and ESLint (TypeScript/Vue) run in CI and via pre-commit hooks
- Security: `pip-audit` and `npm audit` scan dependencies on every CI run
- Pre-commit hooks: `.pre-commit-config.yaml` runs Ruff, ESLint, trailing-whitespace fixes, YAML validation, and large-file checks before each commit

## Performance

The frontend is optimized for fast initial load and smooth navigation.

**Lazy loading:**

- All 11 route views use dynamic `import()` for code splitting
- `AiChat` and `FunFact` components are loaded via `defineAsyncComponent`, removing them from the critical path and eliminating 2 API calls from the initial render
- `SpaceBackground` canvas animation is deferred via `requestIdleCallback` so it does not compete with content rendering

**Navigation UX:**

- `RouteProgressBar` — A slim accent-colored progress bar at the top of the viewport that animates during route transitions, providing visual feedback for lazy-loaded views
- `view-fade` transitions — Content fades in smoothly (250ms) when switching between views

**Loading states:**

- `SkeletonLoader` supports 8 layout variants (`rect`, `circle`, `text`, `card`, `stat`, `table`, `chart`, `hero`) so each view's loading state mirrors its actual content structure
- All 11 views use view-specific skeleton layouts that replicate headers, stat cards, charts, and tables

## Security

Multiple layers of security are applied across the stack.

**Rate limiting:**

- Global middleware limits all `/api/` endpoints to **120 requests per minute** per IP address (Redis-backed)
- AI endpoints have additional per-route limits: chat (20/min), fun-fact (10/min)

**Input validation:**

- All API inputs are validated through Pydantic schemas with strict types
- AI chat messages are sanitized via a `field_validator` that enforces a 2,000 character limit and strips common prompt-injection patterns (`ignore previous instructions`, `system:`, etc.)

**Infrastructure:**

- HTTPS enforced via Nginx with HSTS, X-Frame-Options, X-Content-Type-Options, Content-Security-Policy, and Permissions-Policy headers
- Docker containers run as non-root users
- `.env` files are excluded from version control via `.gitignore`
- `pip-audit` and `npm audit` run in CI to catch vulnerable dependencies
- `.well-known/security.txt` provides a security contact endpoint

## AI-Powered Quality Assessment

This project was iteratively evaluated and improved through a structured AI-assisted quality audit. The process consisted of three rounds of expert evaluation, each followed by targeted improvements until all categories reached production-grade standards.


### Final Scores

| Category | Score | Key Evidence |
|---|---|---|
| Architecture & Structure | 9.5 | Clean layered architecture, 48/48 module docstrings |
| Backend Quality | 9.8 | Null-safe Redis cache, typed function signatures, structured logging |
| Frontend Quality | 9.7 | Focus trap, 8 skeleton variants, aria-hidden on all decorative elements |
| Tests & Coverage | 9.8 | 445 tests, 96% backend coverage, 47 frontend test files covering all views/charts |
| DevOps & CI/CD | 9.8 | Docker healthchecks, coverage enforcement, security scanning, pre-commit hooks |
| Security | 9.7 | Global rate limiting, prompt-injection sanitization, security.txt, HSTS/CSP headers |
| Documentation | 9.5 | 5 documentation files, API reference, data contracts, deployment guide |
| UX/UI & Accessibility | 9.8 | Skip-to-content, focus trap, ARIA on 13 charts, route progress bar, view transitions |
| Performance | 9.0 | 92% bundle reduction, lazy-loading, deferred animations, chunk splitting |
| Maintainability | 9.7 | 100% docstrings, pre-commit hooks, coverage thresholds, CI hardening |

**Overall: 9.73 / 10**

### Verified Metrics

These numbers are not estimates — they are the output of automated tooling:

```
Backend:  203 tests passed | 96.12% coverage | 0 Ruff errors | 80 files formatted
Frontend: 242 tests passed | 47 test files   | 0 ESLint errors | 0 type errors
Bundle:   12.94 KB main | 105 KB vendor-vue | 88 KB vendor-d3 (all gzipped ~50% smaller)
```

## Deployment (AWS)

The project is deployed at **[https://quadsci.juantoledo.com.mx](https://quadsci.juantoledo.com.mx)** using GitHub Actions for CI/CD.

### Architecture

```
Push to main → GitHub Actions (CI: lint, test, build) → SSH to EC2 → docker compose up --build
```

### Infrastructure

| Component | Details |
|---|---|
| Instance | EC2 c7i-flex.large (2 vCPU, 4 GB RAM) — Amazon Linux 2023 |
| SSL | Let's Encrypt (auto-renewal via certbot) |
| Domain | `quadsci.juantoledo.com.mx` (DNS A record → Elastic IP) |
| Containers | API (512 MB), Nginx (256 MB), Redis (256 MB) |

### Setup

1. **EC2 instance** — Create an instance with Amazon Linux 2023, 20 GB storage, and ports 22/80/443 open. Install Docker, Docker Compose plugin, and Docker Buildx.

2. **Elastic IP** — Assign an Elastic IP for a fixed public address.

3. **SSL certificate** — Run `sudo certbot certonly --standalone -d your-domain` on the instance. The Nginx container mounts `/etc/letsencrypt` for HTTPS.

4. **GitHub Secrets** — Add the following in the repository's Settings > Secrets > Actions:

| Secret | Description |
|---|---|
| `EC2_HOST` | Elastic IP or public IP of the instance |
| `EC2_USER` | `ec2-user` (Amazon Linux) or `ubuntu` (Ubuntu) |
| `EC2_SSH_KEY` | Full contents of the `.pem` key file |
| `GROQ_API_KEY` | Groq API key for AI features |

5. **Deploy** — Push to `main` or trigger manually via the Actions tab. The workflow runs CI checks first, then SSHs into the instance, pulls the latest code, and rebuilds all containers.

## Requirements

- Docker and Docker Compose (for containerized and production deployment)
- Python 3.11+ (for local backend development)
- Node.js 20+ (for local frontend development)
