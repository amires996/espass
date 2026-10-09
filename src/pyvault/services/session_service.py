from __future__ import annotations

import time


class SessionService:
    def __init__(self, timeout_seconds: int = 300):
        self.timeout_seconds = timeout_seconds
        self.last_activity = time.monotonic()

    def touch(self) -> None:
        self.last_activity = time.monotonic()

    def expired(self) -> bool:
        return self.timeout_seconds > 0 and time.monotonic() - self.last_activity >= self.timeout_seconds
