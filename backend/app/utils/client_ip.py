"""Extract client IP, honoring X-Real-IP / X-Forwarded-For when behind a trusted proxy."""

from starlette.requests import Request


def get_client_ip(request: Request) -> str:
    """Return the client IP, using proxy headers when available.

    When behind nginx or another trusted proxy, X-Forwarded-For and X-Real-IP
    contain the real client IP. Otherwise falls back to request.client.host.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "unknown"
