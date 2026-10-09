from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

@dataclass(slots=True)
class Credential:
    title: str
    username: str = ""
    password: str = ""
    url: str = ""
    category: str = "Personal"
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    favorite: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Credential":
        allowed = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: v for k, v in data.items() if k in allowed})
