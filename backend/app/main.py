"""FastAPI application entry point with lifespan, middleware, and route registration."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware import RateLimitMiddleware, TraceMiddleware, error_handler
from app.api.routes import (
    ai,
    cores,
    dashboard,
    dev,
    economics,
    emissions,
    health,
    history,
    landing,
    launches,
    launchpads,
    notifications,
    roadster,
    rockets,
    starlink,
)
from app.cache.redis_cache import cache
from app.config import settings

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await cache.connect()
    yield
    await cache.disconnect()


app = FastAPI(
    title="SpaceX Dashboard API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Trace-ID"],
)
app.add_middleware(TraceMiddleware)
app.add_middleware(RateLimitMiddleware)

app.add_exception_handler(Exception, error_handler)

app.include_router(health.router)
app.include_router(rockets.router)
app.include_router(launches.router)
app.include_router(starlink.router)
app.include_router(cores.router)
app.include_router(launchpads.router)
app.include_router(dashboard.router)
app.include_router(economics.router)
app.include_router(history.router)
app.include_router(landing.router)
app.include_router(roadster.router)
app.include_router(emissions.router)
app.include_router(ai.router)
app.include_router(notifications.router)
app.include_router(dev.router)
