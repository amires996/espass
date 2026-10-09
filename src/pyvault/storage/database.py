from __future__ import annotations

import sqlite3
from pathlib import Path

from pyvault.core.exceptions import CorruptVaultError

SCHEMA_VERSION = 1


def connect(path: str | Path) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        conn = sqlite3.connect(str(path), timeout=10, isolation_level="DEFERRED")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=DELETE")
        conn.execute("PRAGMA synchronous=FULL")
        conn.execute("PRAGMA secure_delete=ON")
        conn.execute("CREATE TABLE IF NOT EXISTS vault (id INTEGER PRIMARY KEY CHECK(id=1), schema_version INTEGER NOT NULL, metadata TEXT NOT NULL)")
        conn.commit()
        return conn
    except sqlite3.DatabaseError:
        raise CorruptVaultError("The vault database is damaged or is not an espass vault file.") from None
