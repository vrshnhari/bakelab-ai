import pytest
from fastapi import HTTPException

from app.services.rate_limiter import InMemoryRateLimiter


def test_rate_limiter_blocks_after_limit():
    limiter = InMemoryRateLimiter(max_requests=2, window_seconds=60)

    limiter.check("test-client")
    limiter.check("test-client")

    with pytest.raises(HTTPException) as exc_info:
        limiter.check("test-client")

    assert exc_info.value.status_code == 429
    assert exc_info.value.headers["Retry-After"]
