# SpaceX Dashboard — Frontend

Single-page application built with Vue 3 and TypeScript. Features 11 interactive views with D3.js visualizations, dark/light theming, and a fully responsive layout.

## Tech Stack

| Technology      | Purpose                                |
|-----------------|----------------------------------------|
| Vue 3           | UI framework (Composition API + `<script setup>`) |
| TypeScript      | Strict typing, no `any` — interfaces mirror backend schemas |
| Vite            | Build tool and dev server              |
| D3.js           | Custom charts, globe, maps, and orbital diagrams |
| Pinia           | Centralized state management           |
| Axios           | HTTP client for backend API calls      |
| Vue Router      | Client-side routing with lazy loading  |
| ESLint          | Code linting (Vue + TypeScript rules)  |

## Setup

### Prerequisites

- Node.js 20+
- Backend API running at `http://localhost:8000` (or via Docker Compose)

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Opens at http://localhost:5173. The Vite dev server proxies `/api` requests to the backend at `http://localhost:8000`.

### Production Build

```bash
npm run build
```

Runs TypeScript type checking followed by a Vite production build. Output goes to `dist/`, served by Nginx in the Docker container.

## Scripts

| Command          | Description                              |
|------------------|------------------------------------------|
| `npm run dev`    | Start Vite dev server with HMR           |
| `npm run build`  | Type-check + production build            |
| `npm run build:only` | Production build (skip type-check)  |
| `npm run preview`| Preview the production build locally     |
| `npm run type-check` | Run `vue-tsc --noEmit`              |
| `npm run lint`   | ESLint with auto-fix                     |

## Views

| Route              | View                | Description                                    |
|--------------------|---------------------|------------------------------------------------|
| `/`                | OverviewView        | Stats, launch cadence, next/latest mission, site performance, cross-domain recommended actions |
| `/launches`        | LaunchesView        | Filterable launch log with year breakdown      |
| `/launches/:id`    | LaunchDetailView    | Mission detail: crew, payloads, cores, gallery |
| `/fleet`           | FleetView           | Rocket showcase with specs and recovery stats  |
| `/rockets/:id`     | RocketDetailView    | Rocket specs, stages, dimensions, gallery      |
| `/starlink`        | StarlinkView        | Interactive 3D globe, satellite table, versions |
| `/economics`       | EconomicsView       | Cost per kg, annual spend, vehicle comparison  |
| `/emissions`       | EmissionsView       | CO2 estimates, fuel breakdown, reuse savings   |
| `/history`         | HistoryView         | Interactive timeline of SpaceX milestones      |
| `/landing`         | LandingView         | Landing pad map, pad comparison, success rates |
| `/starman`         | StarmanView         | Roadster telemetry, orbital diagram, gallery   |

All views are lazy-loaded via dynamic `import()` for optimal bundle splitting. Route transitions are accompanied by a `RouteProgressBar` and a smooth `view-fade` CSS transition (250ms).

## Components

### Charts (`components/charts/`)

Custom D3.js visualizations — each component uses `ResizeObserver` to adapt to its container width:

| Component              | Type                  | Used in         |
|------------------------|-----------------------|-----------------|
| LaunchCadenceChart     | Area + line chart     | Overview        |
| LaunchesByYearChart    | Stacked bar chart     | Launches        |
| RocketSuccessChart     | Horizontal bars       | Fleet           |
| CoreReuseChart         | Grouped bars          | Fleet           |
| StarlinkGlobe         | 3D orthographic globe | Starlink        |
| CostPerKgChart         | Horizontal bars       | Economics       |
| AnnualSpendChart       | Area chart            | Economics       |
| SpendByVehicleChart    | Horizontal bars       | Economics       |
| MassByOrbitChart        | Stacked bars          | Economics       |
| EmissionsTimelineChart | Area chart + tooltip  | Emissions       |
| FuelBreakdownChart     | Donut chart           | Emissions       |
| LandingMapChart        | Natural Earth map     | Landing         |
| RoadsterOrbitChart     | SVG orbital diagram   | Starman         |

### Common (`components/common/`)

| Component        | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| AiChat           | Floating AI assistant with markdown rendering and typewriter effect (lazy-loaded via `defineAsyncComponent`) |
| DataTable        | Paginated table with clickable rows                                        |
| ErrorLabPanel    | Easter egg panel for triggering simulated errors (triple-click SPACEX)     |
| ErrorState       | Error message with retry button and `retrying` spinner state               |
| FunFact          | AI-generated curiosity banner on site load with auto-dismiss (lazy-loaded via `defineAsyncComponent`) |
| ImageLightbox    | Full-screen image viewer with keyboard navigation and focus trap           |
| InfoTip          | Tooltip/info icon for contextual help                                      |
| MiniTimeline     | Compact mission list for Overview                                          |
| NotificationToast | Toast notification item (used by notifications store)                      |
| SectionNav       | Section navigation component                                               |
| SkeletonLoader   | Loading placeholder with 8 layout variants: `rect`, `circle`, `text`, `card`, `stat`, `table`, `chart`, `hero` |

### Layout (`components/layout/`)

| Component        | Description                                     |
|------------------|-------------------------------------------------|
| AppHeader        | Top navigation with mobile hamburger drawer and accessible theme toggle (`aria-pressed`) |
| AppFooter        | Footer with credits                             |
| RouteProgressBar | Slim accent-colored progress bar at the top of the viewport during route transitions |
| SpaceBackground  | Animated canvas with stars and shooting stars (deferred via `requestIdleCallback`) |

## State Management

Pinia stores handle data fetching and caching on the client side:

| Store         | Manages                                                                 |
|---------------|-------------------------------------------------------------------------|
| dashboard     | Overview page data (stats, recommended actions, launches)               |
| launches      | Launch list with filters and pagination                                |
| fleet         | Fleet stats + rockets list (FleetView)                                 |
| rockets       | Rocket list (used by FleetView, RocketDetailView, etc.)                |
| starlink      | Starlink satellites with version filter                                |
| notifications | Toast notifications + SSE connection to `/api/notifications/stream`    |
| theme         | Dark/light mode toggle (persisted to localStorage)                      |

Most data stores follow the same pattern: `loading`, `error`, and `data` refs with a `load()` action that fetches from the backend API. The `notifications` store manages toast UI state and an SSE connection to the backend.

## Theming

The app supports dark and light themes via CSS custom properties defined in `assets/styles/main.css`:

- **Dark theme** (default): Dark backgrounds, light text, amber accent
- **Light theme**: White backgrounds, dark text, warm accent

The theme toggle in the header switches the `data-theme` attribute on the root element. The preference is persisted to `localStorage`.

All components use CSS variables (`--bg-base`, `--text`, `--accent`, etc.) so theme changes propagate automatically.

## Responsive Design

Three breakpoints ensure the layout works across devices:

| Breakpoint   | Target       | Key changes                                    |
|--------------|--------------|------------------------------------------------|
| `> 768px`    | Desktop      | Full navigation, multi-column grids            |
| `<= 768px`   | Tablet       | Hamburger menu, single-column layouts          |
| `<= 640px`   | Mobile       | Reduced font sizes, compact spacing            |

Mobile-specific features:
- Hamburger menu with slide-in drawer and accordion for "Explore" sub-navigation
- Touch-friendly tap targets (minimum 44px)
- Satellite detail panel repositioned to bottom sheet
- Tables with horizontal scroll

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── index.ts          # Axios client + API functions
│   ├── assets/
│   │   └── styles/
│   │       └── main.css       # Design tokens, reset, global styles
│   ├── components/
│   │   ├── charts/            # 13 D3.js visualization components
│   │   ├── common/            # 10 reusable UI components
│   │   └── layout/            # Header, footer, progress bar, space background
│   ├── router/
│   │   └── index.ts           # 11 routes with lazy loading
│   ├── stores/
│   │   ├── dashboard.ts
│   │   ├── errorLab.ts
│   │   ├── fleet.ts
│   │   ├── launches.ts
│   │   ├── notifications.ts
│   │   ├── rockets.ts
│   │   ├── starlink.ts
│   │   └── theme.ts
│   ├── types/
│   │   └── index.ts           # TypeScript interfaces for all entities
│   ├── utils/
│   │   ├── chartColors.ts     # CSS variable reader for D3 charts
│   │   ├── formatDate.ts      # Date formatting helpers
│   │   └── handleError.ts     # Centralized Axios error extraction
│   ├── views/                 # 11 page components
│   ├── App.vue                # Root component
│   └── main.ts                # App initialization
├── index.html
├── tsconfig.json
├── tsconfig.app.json
├── vite.config.ts
├── Dockerfile                 # Multi-stage: Node build + Nginx serve
├── nginx.conf                 # SSL termination + reverse proxy to API
└── package.json
```

## API & Loading

The Axios client ([`src/api/index.ts`](src/api/index.ts)) uses a 30-second timeout for all API requests. The Overview page fetches `/api/dashboard`, which the backend optimizes with parallel fetches, full-response caching (5 min), and prefetched AI context. Cold-cache loads typically complete in 6–12 seconds; cached loads return in under 1 second.

## Build Optimization

Vite is configured with `manualChunks` in `vite.config.ts` to split vendor dependencies into independently cacheable chunks:

| Chunk | Approx. Size | Contents |
|---|---|---|
| `vendor-vue` | 105 KB | Vue 3, Vue Router, Pinia |
| `vendor-d3` | 88 KB | All D3 modules (14 sub-packages) |
| `vendor-axios` | 36 KB | Axios HTTP client |
| `index` (app code) | **12.9 KB** | Application logic (92% reduction from pre-split 158 KB) |

The `chunkSizeWarningLimit` is set to 250 KB to catch regressions. Returning users benefit from browser caching of vendor chunks, which change far less frequently than application code.

Additionally, `AiChat` and `FunFact` are loaded via `defineAsyncComponent`, so their code (and the 2 API calls they trigger) are excluded from the critical rendering path.

## Loading UX

Every view has a tailored loading state that mirrors its actual content structure using `SkeletonLoader` variants:

| View | Skeleton Layout |
|---|---|
| Overview | `hero` + 4x `stat` + `chart` |
| Launches | `table` with header and rows |
| Fleet | `card` grid with image + text areas |
| Starlink | `chart` (globe) + `table` |
| Economics | 3x `stat` + 2x `chart` |
| Emissions | `stat` row + `chart` + `table` |
| History | Alternating `text` blocks (timeline) |
| Landing | `chart` (map) + `stat` row |
| Starman | `hero` + `stat` row + `chart` |
| Launch/Rocket Detail | `hero` + `text` blocks + `card` grid |

The `ErrorState` component includes a `retrying` prop that shows a spinner and "RETRYING..." label during automatic retry operations, avoiding UI flicker.

## Error Testing Lab (Easter Egg)

The dashboard includes a hidden **Error Testing Lab** to demonstrate error handling. See also the [Backend dev endpoint](backend/README.md#error-testing-dev-endpoint).

**How to open:** Triple-click the "SPACEX" brand in the header (three clicks within ~500 ms).

**Panel options:**
- **Show ErrorState** — Simulates an inline error on Overview with a RETRY button
- **Show error toast** — Displays a NotificationToast with type `error` (auto-dismisses after 12 s)
- **API errors (404, 500, 502, 503, timeout)** — Calls the backend `/api/dev/trigger-error` and shows the resulting error on Overview

**Direct API testing** (curl or browser):

```bash
# Local
curl "http://localhost:8000/api/dev/trigger-error?code=404"
curl "http://localhost:8000/api/dev/trigger-error?code=500"
curl "http://localhost:8000/api/dev/trigger-error?code=timeout"   # waits 5s

# Production
curl "https://quadsci.juantoledo.com.mx/api/dev/trigger-error?code=404"
```

## Tests

The frontend test suite includes **242 tests** across **47 test files**, covering:

| Category | Files | Description |
|---|---|---|
| Views | 11 | Loading, data rendering, error states for all pages |
| Charts | 13 | Mount and render validation for all D3 charts |
| Stores | 7 | Pinia store fetch, error handling, state management |
| Components | 10 | AiChat, DataTable, ErrorState, SkeletonLoader, NotificationToast, etc. |
| Utils | 3 | handleError, formatDate, chartColors |
| Router | 1 | Route definitions, lazy loading, path matching |
| Integration | 4 | SpaceBackground, ImageLightbox, FunFact, MiniTimeline |

Run all tests:

```bash
npm run test
```

The test runner is [Vitest](https://vitest.dev/) with `happy-dom` as the DOM environment and `@vue/test-utils` for component mounting.
