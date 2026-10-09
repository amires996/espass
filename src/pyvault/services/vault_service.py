from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any

from pyvault.core.exceptions import CorruptVaultError, InvalidPasswordError, VaultLockedError
from pyvault.core.validators import validate_master_password
from pyvault.crypto.encryption import decrypt, encrypt
from pyvault.crypto.kdf import DEFAULT_KDF, derive_key, new_salt
from pyvault.crypto.vault_format import FORMAT_VERSION, associated_data, canonical_json, validate_metadata
from pyvault.storage.repository import VaultRepository

DEFAULT_CATEGORIES = ["Telegram", "Instagram", "Email", "Social Media", "Work", "Banking", "Shopping", "Gaming", "Development", "Personal", "Other"]


class VaultService:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.repository = VaultRepository(self.path)
        self._dek: bytes | None = None
        self._state: dict[str, Any] | None = None

    @property
    def unlocked(self) -> bool:
        return self._dek is not None and self._state is not None

    def create(self, password: str, confirmation: str | None = None) -> None:
        validate_master_password(password, confirmation)
        salt = new_salt()
        params = dict(DEFAULT_KDF)
        meta: dict[str, Any] = {"version": FORMAT_VERSION, "kdf": params,
                                "salt": base64.b64encode(salt).decode("ascii")}
        wrapping_key = derive_key(password, salt, params)
        dek = os.urandom(32)
        wrap_nonce, wrapped = encrypt(wrapping_key, dek, associated_data(meta, "wrap-dek"))
        payload = {"credentials": [], "categories": DEFAULT_CATEGORIES.copy(), "tags": [], "created_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}
        data_nonce, ciphertext = encrypt(dek, canonical_json(payload), associated_data(meta, "vault-payload"))
        meta.update({"wrap_nonce": base64.b64encode(wrap_nonce).decode("ascii"),
                     "wrapped_key": base64.b64encode(wrapped).decode("ascii"),
                     "data_nonce": base64.b64encode(data_nonce).decode("ascii"),
                     "payload": base64.b64encode(ciphertext).decode("ascii")})
        self.repository.create(meta)
        self._dek, self._state = dek, payload

    def unlock(self, password: str) -> None:
        meta = self.repository.read_metadata()
        validate_metadata(meta)
        try:
            salt = base64.b64decode(meta["salt"], validate=True)
            nonce = base64.b64decode(meta["wrap_nonce"], validate=True)
            wrapped = base64.b64decode(meta["wrapped_key"], validate=True)
            payload_nonce = base64.b64decode(meta["data_nonce"], validate=True)
            ciphertext = base64.b64decode(meta["payload"], validate=True)
        except (ValueError, TypeError):
            raise CorruptVaultError("Vault contains malformed cryptographic fields.") from None
        wrapping_key = derive_key(password, salt, meta["kdf"])
        dek = decrypt(wrapping_key, nonce, wrapped, associated_data(meta, "wrap-dek"), password_check=True)
        if len(dek) != 32:
            raise CorruptVaultError("Invalid data encryption key.")
        plaintext = decrypt(dek, payload_nonce, ciphertext, associated_data(meta, "vault-payload"))
        try:
            state = json.loads(plaintext.decode("utf-8"))
            if not isinstance(state, dict) or not isinstance(state.get("credentials"), list) or not isinstance(state.get("categories"), list):
                raise ValueError
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
            raise CorruptVaultError("Decrypted vault payload has an invalid structure.") from None
        # Migrate vaults created by the previous espass/PyVault defaults without
        # overwriting user-customized category lists or creating fake credentials.
        previous_defaults = ["Personal", "Work", "Development", "Social", "Finance", "Shopping", "Other"]
        migrated_categories = state.get("categories") == previous_defaults
        if migrated_categories:
            state["categories"] = DEFAULT_CATEGORIES.copy()
        self._dek, self._state = dek, state
        if migrated_categories:
            # Persist the migration only when the old built-in defaults were detected.
            self._save()

    def lock(self) -> None:
        self._dek = None
        self._state = None

    def _require(self) -> tuple[bytes, dict[str, Any]]:
        if not self.unlocked:
            raise VaultLockedError("Unlock the vault to continue.")
        assert self._dek is not None and self._state is not None
        return self._dek, self._state

    def _save(self) -> None:
        dek, state = self._require()
        meta = self.repository.read_metadata()
        nonce, ciphertext = encrypt(dek, canonical_json(state), associated_data(meta, "vault-payload"))
        meta["data_nonce"] = base64.b64encode(nonce).decode("ascii")
        meta["payload"] = base64.b64encode(ciphertext).decode("ascii")
        self.repository.write(meta)

    def credentials(self) -> list[dict[str, Any]]:
        _, state = self._require()
        return [dict(c) for c in state["credentials"]]

    def get(self, credential_id: str) -> dict[str, Any] | None:
        return next((c for c in self.credentials() if c.get("id") == credential_id), None)

    def upsert(self, item: dict[str, Any]) -> None:
        _, state = self._require()
        from pyvault.core.models import Credential, utc_now
        from pyvault.core.validators import validate_credential
        credential = Credential.from_dict(item)
        validate_credential(credential)
        existing = next((c for c in state["credentials"] if c["id"] == credential.id), None)
        if existing:
            credential.created_at = existing.get("created_at", credential.created_at)
            credential.updated_at = utc_now()
            state["credentials"] = [c for c in state["credentials"] if c["id"] != credential.id]
        state["credentials"].append(credential.to_dict())
        if credential.category and credential.category not in state["categories"]:
            state["categories"].append(credential.category)
        self._save()

    def delete(self, credential_id: str) -> None:
        _, state = self._require()
        state["credentials"] = [c for c in state["credentials"] if c.get("id") != credential_id]
        self._save()

    def categories(self) -> list[str]:
        _, state = self._require()
        return list(state["categories"])

    def set_categories(self, categories: list[str]) -> None:
        _, state = self._require()
        clean = list(dict.fromkeys(c.strip() for c in categories if c.strip()))
        state["categories"] = clean or ["Other"]
        for item in state["credentials"]:
            if item.get("category") not in state["categories"]:
                item["category"] = "Other" if "Other" in state["categories"] else state["categories"][0]
        self._save()

    def replace_from_backup(self, backup_path: str | Path, password: str) -> None:
        """Validate a backup before replacing the current vault; roll back on failure."""
        import shutil
        import uuid

        source = Path(backup_path)
        if not self.unlocked:
            raise VaultLockedError("Unlock the current vault before restoring a backup.")
        if not source.is_file():
            raise CorruptVaultError("The selected backup file does not exist.")

        # Validate the source without changing the active vault or its in-memory state.
        candidate = VaultService(source)
        candidate.unlock(password)
        candidate.lock()

        suffix = uuid.uuid4().hex
        tmp = self.path.with_name(f"{self.path.name}.{suffix}.restore.tmp")
        rollback = self.path.with_name(f"{self.path.name}.{suffix}.restore.rollback")
        previous_dek, previous_state = self._dek, self._state
        try:
            shutil.copy2(self.path, rollback)
            shutil.copy2(source, tmp)
            check = VaultService(tmp)
            check.unlock(password)
            check.lock()
            os.replace(tmp, self.path)
            self._dek = None
            self._state = None
            self.unlock(password)
        except Exception:
            # If the destination was replaced, put the original file back. Preserve
            # the old unlocked state as well so a failed restore does not lock users out.
            try:
                if rollback.exists():
                    os.replace(rollback, self.path)
            finally:
                self._dek, self._state = previous_dek, previous_state
                tmp.unlink(missing_ok=True)
                rollback.unlink(missing_ok=True)
            raise
        else:
            tmp.unlink(missing_ok=True)
            rollback.unlink(missing_ok=True)
