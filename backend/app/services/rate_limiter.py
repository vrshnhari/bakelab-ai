from time import monotonic

from fastapi import HTTPException, Request, status

from app.config import settings


class InMemoryRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, list[float]] = {}

    def check(self, key: str) -> None:
        now = monotonic()
        window_start = now - self.window_seconds
        recent_hits = [timestamp for timestamp in self._hits.get(key, []) if timestamp > window_start]

        if len(recent_hits) >= self.max_requests:
            retry_after = max(1, int(self.window_seconds - (now - recent_hits[0])))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "message": "You have reached the recipe generation limit. Please wait before trying again.",
                    "limit": self.max_requests,
                    "window_seconds": self.window_seconds,
                    "retry_after_seconds": retry_after,
                },
                headers={"Retry-After": str(retry_after)},
            )

        recent_hits.append(now)
        self._hits[key] = recent_hits


ai_limiter = InMemoryRateLimiter(
    max_requests=settings.ai_rate_limit_requests,
    window_seconds=settings.ai_rate_limit_window_seconds,
)


def rate_limit_ai(request: Request) -> None:
    client_host = request.client.host if request.client else "unknown"
    forwarded_for = request.headers.get("x-forwarded-for")
    client_key = forwarded_for.split(",")[0].strip() if forwarded_for else client_host
    ai_limiter.check(client_key)
