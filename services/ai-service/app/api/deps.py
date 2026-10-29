import time
from collections import defaultdict
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request, status

from app.core.config import Settings, get_settings

_rate_buckets: dict[str, list[float]] = defaultdict(list)


def verify_api_key(
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    settings: Settings = Depends(get_settings),
) -> None:
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


def check_rate_limit(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> None:
    client = request.client.host if request.client else "unknown"
    now = time.time()
    window_start = now - 60
    bucket = _rate_buckets[client]
    _rate_buckets[client] = [t for t in bucket if t > window_start]
    if len(_rate_buckets[client]) >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )
    _rate_buckets[client].append(now)
