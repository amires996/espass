from __future__ import annotations

import os
from typing import Any

from argon2.low_level import Type, hash_secret_raw

from pyvault.core.exceptions import CorruptVaultError

DEFAULT_KDF: dict[str, Any] = {"name": "argon2id", "time_cost": 3, "memory_cost": 65536, "parallelism": 2, "hash_len": 32}


def new_salt() -> bytes:
    return os.urandom(16)


def validate_kdf_params(params: dict[str, Any]) -> None:
    if not isinstance(params, dict) or params.get("name") != "argon2id":
        raise CorruptVaultError("Unsupported key derivation configuration.")
    try:
        t, m, p, h = (params[k] for k in ("time_cost", "memory_cost", "parallelism", "hash_len"))
        if any(type(x) is not int for x in (t, m, p, h)):
            raise ValueError
        if not (1 <= t <= 10 and 8192 <= m <= 262144 and 1 <= p <= 8 and h == 32):
            raise ValueError
    except (KeyError, ValueError, TypeError):
        raise CorruptVaultError("Invalid or unsafe key derivation parameters.") from None


def derive_key(password: str, salt: bytes, params: dict[str, Any] | None = None) -> bytes:
    params = params or DEFAULT_KDF
    validate_kdf_params(params)
    if not isinstance(password, str) or len(password.encode("utf-8")) > 4096 or len(salt) != 16:
        raise CorruptVaultError("Invalid key derivation input.")
    return hash_secret_raw(password.encode("utf-8"), salt, time_cost=params["time_cost"],
                           memory_cost=params["memory_cost"], parallelism=params["parallelism"],
                           hash_len=params["hash_len"], type=Type.ID)
