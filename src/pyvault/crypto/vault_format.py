from __future__ import annotations

import json
from typing import Any

from pyvault.core.exceptions import CorruptVaultError, UnsupportedFormatError

FORMAT_VERSION = 1


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def associated_data(meta: dict[str, Any], purpose: str) -> bytes:
    # Bind all public KDF and version fields, while keeping the two encryption uses distinct.
    public = {"version": meta.get("version"), "kdf": meta.get("kdf"), "salt": meta.get("salt"), "purpose": purpose}
    return canonical_json(public)


def validate_metadata(meta: dict[str, Any]) -> None:
    if not isinstance(meta, dict):
        raise CorruptVaultError("Vault metadata is malformed.")
    if meta.get("version") != FORMAT_VERSION:
        raise UnsupportedFormatError("This vault format version is not supported.")
    for field in ("kdf", "salt", "wrap_nonce", "wrapped_key", "data_nonce", "payload"):
        if field not in meta:
            raise CorruptVaultError("Vault metadata is incomplete.")
    if not isinstance(meta["salt"], str) or not isinstance(meta["wrapped_key"], str) or not isinstance(meta["payload"], str):
        raise CorruptVaultError("Vault metadata has invalid field types.")
