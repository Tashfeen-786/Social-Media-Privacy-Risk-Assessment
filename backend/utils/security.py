"""
security.py
-----------
Small, dependency-light security utilities:
  * in-memory sliding-window rate limiter
  * security response headers
  * input sanitisation helpers (defence in depth against XSS)
  * API-key based authorisation concept for admin-style endpoints
"""

import html
import os
import re
import time
from collections import defaultdict, deque
from typing import Deque, Dict

RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

_BUCKETS: Dict[str, Deque[float]] = defaultdict(deque)

SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "SAMEORIGIN",
    "Referrer-Policy": "no-referrer",
    "X-XSS-Protection": "1; mode=block",
    "Permissions-Policy": "geolocation=(), camera=(), microphone=()",
    "Cache-Control": "no-store",
}

ID_PATTERN = re.compile(r"^SMPRA-[A-Z0-9]{6,32}$")


def rate_limit_check(client_key: str) -> bool:
    """Return True if the request is allowed, False if the limit is exceeded."""
    now = time.time()
    bucket = _BUCKETS[client_key]
    while bucket and now - bucket[0] > RATE_LIMIT_WINDOW:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT_REQUESTS:
        return False
    bucket.append(now)
    return True


def reset_rate_limits() -> None:
    _BUCKETS.clear()


def sanitize_text(value: str, max_length: int = 200) -> str:
    """Escape HTML and strip control characters (defence in depth)."""
    cleaned = re.sub(r"[\x00-\x1f\x7f]", "", str(value))[:max_length]
    return html.escape(cleaned, quote=True)


def valid_assessment_id(value: str) -> bool:
    return bool(ID_PATTERN.match(str(value)))


def admin_key_valid(provided: str | None) -> bool:
    """Authorisation concept: admin endpoints require the configured API key."""
    expected = os.getenv("ADMIN_API_KEY", "").strip()
    if not expected:
        return False
    return bool(provided) and provided.strip() == expected
