"""Easter egg: trigger simulated errors for testing error handling in the frontend."""

import asyncio

from fastapi import APIRouter, Request
from starlette.responses import JSONResponse

from app.api.rate_limit import check_rate_limit

router = APIRouter(prefix="/api/dev", tags=["dev"])

ERROR_MESSAGES: dict[str, tuple[int, str, str]] = {
    "404": (404, "RESOURCE_NOT_FOUND", "Simulated 404 — Resource not found"),
    "500": (500, "INTERNAL_ERROR", "Simulated 500 — Internal server error"),
    "502": (502, "BAD_GATEWAY", "Simulated 502 — Bad gateway"),
    "503": (503, "SERVICE_UNAVAILABLE", "Simulated 503 — Service unavailable"),
    "timeout": (504, "GATEWAY_TIMEOUT", "Simulated timeout — Request took too long"),
}


@router.get("/trigger-error")
async def trigger_error(request: Request, code: str = "500"):
    """Return a simulated error response for testing frontend error handling.

    Query params:
        code: 404 | 500 | 502 | 503 | timeout

    Use the Error Lab panel (triple-click SPACEX in header) to trigger from the UI.
    """
    await check_rate_limit(request, prefix="rl:dev", max_requests=30, window_seconds=60)

    entry = ERROR_MESSAGES.get(code.lower(), ERROR_MESSAGES["500"])
    status_code, error_code, message = entry

    if code.lower() == "timeout":
        await asyncio.sleep(5)  # Simulated delay; client timeout (30s) still allows response

    trace_id = getattr(request.state, "trace_id", "unknown")
    return JSONResponse(
        status_code=status_code,
        content={"code": error_code, "message": message, "trace_id": trace_id},
    )
