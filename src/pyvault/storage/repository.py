from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from pyvault.core.exceptions import CorruptVaultError, VaultError
from pyvault.storage.database import SCHEMA_VERSION, connect


class VaultRepository:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def exists(self) -> bool:
        return self.path.is_file()

    def read_metadata(self) -> dict[str, Any]:
        if not self.path.exists():
            raise VaultError("Vault file does not exist.")
        try:
            with closing(connect(self.path)) as conn:
                row = conn.execute("SELECT schema_version, metadata FROM vault WHERE id=1").fetchone()
            if not row or row[0] != SCHEMA_VERSION:
                raise CorruptVaultError("Vault database schema is missing or unsupported.")
            value = json.loads(row[1])
            if not isinstance(value, dict):
                raise ValueError
            return value
        except (sqlite3.DatabaseError, json.JSONDecodeError, ValueError):
            raise CorruptVaultError("The vault database is damaged or has invalid metadata.") from None

    def create(self, metadata: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            raise VaultError("A file already exists at the selected vault path.")
        try:
            with closing(connect(self.path)) as conn:
                conn.execute("INSERT INTO vault(id, schema_version, metadata) VALUES(1, ?, ?)",
                             (SCHEMA_VERSION, json.dumps(metadata, separators=(",", ":"))))
                conn.commit()
        except Exception:
            self.path.unlink(missing_ok=True)
            raise
        try:
            self.path.chmod(0o600)
        except OSError:
            pass

    def write(self, metadata: dict[str, Any]) -> None:
        try:
            with closing(connect(self.path)) as conn:
                conn.execute("BEGIN IMMEDIATE")
                conn.execute("UPDATE vault SET metadata=? WHERE id=1",
                             (json.dumps(metadata, separators=(",", ":")),))
                conn.commit()
        except sqlite3.DatabaseError:
            raise CorruptVaultError("Unable to safely save the vault. Your current file was not intentionally replaced.") from None

    def validate_database(self) -> None:
        self.read_metadata()

    def copy_backup(self, destination: str | Path) -> None:
        dest = Path(destination)
        if dest.exists():
            raise VaultError("The backup destination already exists.")
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_name(dest.name + ".tmp")
        try:
            with closing(connect(self.path)) as source, closing(sqlite3.connect(str(tmp))) as target:
                source.backup(target)
                target.commit()
            tmp.replace(dest)
            try:
                dest.chmod(0o600)
            except OSError:
                pass
        except Exception:
            tmp.unlink(missing_ok=True)
            raise
