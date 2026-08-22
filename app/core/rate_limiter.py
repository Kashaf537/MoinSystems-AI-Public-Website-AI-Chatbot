"""
Day 6 - Rate limiting.

Provides:
- Per-IP rate limiting
- Per-session rate limiting
- Automatic cleanup of expired requests

Note:
This implementation uses in-memory storage and is suitable for
local/staging or a single application instance.

For multi-instance production deployment, use Redis-backed
rate limiting.
"""

import time
from collections import defaultdict, deque
from threading import Lock


class RateLimitExceeded(Exception):
    """Raised when a client exceeds the configured rate limit."""

    def __init__(self, message: str = "Too many requests. Please try again later."):
        self.message = message
        super().__init__(message)


class RateLimiter:
    """
    Simple sliding-window rate limiter.

    IP limit:
        Maximum number of requests from one IP within the window.

    Session limit:
        Maximum number of requests from one chat session within
        the same window.
    """

    def __init__(
        self,
        ip_limit: int = 30,
        session_limit: int = 20,
        window_seconds: int = 60,
    ):
        self.ip_limit = ip_limit
        self.session_limit = session_limit
        self.window_seconds = window_seconds

        self.ip_requests: dict[str, deque[float]] = defaultdict(deque)
        self.session_requests: dict[str, deque[float]] = defaultdict(deque)

        self.lock = Lock()

    def _cleanup(
        self,
        requests: deque[float],
        now: float,
    ) -> None:

        cutoff = now - self.window_seconds

        while requests and requests[0] <= cutoff:
            requests.popleft()

    def _check(
        self,
        requests: deque[float],
        limit: int,
        now: float,
    ) -> bool:

        self._cleanup(requests, now)

        if len(requests) >= limit:
            return False

        requests.append(now)
        return True

    def check(
        self,
        ip_address: str,
        session_id: str,
    ) -> None:

        now = time.monotonic()

        with self.lock:

            ip_allowed = self._check(
                self.ip_requests[ip_address],
                self.ip_limit,
                now,
            )

            if not ip_allowed:
                raise RateLimitExceeded(
                    "Too many requests from this IP. "
                    "Please try again later."
                )

            session_allowed = self._check(
                self.session_requests[session_id],
                self.session_limit,
                now,
            )

            if not session_allowed:
                raise RateLimitExceeded(
                    "Too many requests for this chat session. "
                    "Please try again later."
                )


rate_limiter = RateLimiter(
    ip_limit=30,
    session_limit=20,
    window_seconds=60,
)

