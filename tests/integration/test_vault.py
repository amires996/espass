import sqlite3

import pytest

from pyvault.core.exceptions import CorruptVaultError, InvalidPasswordError, VaultLockedError
from pyvault.services.vault_service import VaultService

PASSWORD = "a very long correct horse battery passphrase"


def test_create_unlock_crud_and_lock(tmp_path):
    path = tmp_path / "test.pyvault"
    vault = VaultService(path)
    vault.create(PASSWORD, PASSWORD)
    locked = VaultService(path)
    with pytest.raises(VaultLockedError): locked.credentials()
    vault.upsert({"title": "Email", "username": "user@example.test", "password": "secret-do-not-store-plaintext", "url": "https://example.test"})
    item = vault.credentials()[0]
    assert item["title"] == "Email"
    item["favorite"] = True
    vault.upsert(item)
    vault.lock()
    with pytest.raises(InvalidPasswordError): VaultService(path).unlock("incorrect password here")
    loaded = VaultService(path); loaded.unlock(PASSWORD)
    assert loaded.credentials()[0]["favorite"] is True
    loaded.delete(item["id"])
    assert loaded.credentials() == []


def test_sensitive_values_not_in_database(tmp_path):
    path = tmp_path / "test.pyvault"
    v = VaultService(path); v.create(PASSWORD)
    v.upsert({"title": "Secret Title", "username": "private-user", "password": "ultra-secret-password", "notes": "private notes"})
    raw = path.read_bytes()
    for secret in (b"Secret Title", b"private-user", b"ultra-secret-password", b"private notes", PASSWORD.encode()):
        assert secret not in raw


def test_tampered_payload_fails_closed(tmp_path):
    path = tmp_path / "test.pyvault"; v = VaultService(path); v.create(PASSWORD)
    with sqlite3.connect(path) as conn:
        meta = conn.execute("SELECT metadata FROM vault WHERE id=1").fetchone()[0]
        import json
        obj = json.loads(meta); obj["payload"] = obj["payload"][:-4] + "AAAA"
        conn.execute("UPDATE vault SET metadata=? WHERE id=1", (json.dumps(obj),))
    with pytest.raises(CorruptVaultError): VaultService(path).unlock(PASSWORD)


def test_unsupported_format_and_missing_file(tmp_path):
    path=tmp_path/"test.pyvault"; v=VaultService(path); v.create(PASSWORD)
    with sqlite3.connect(path) as conn:
        import json
        m=json.loads(conn.execute("SELECT metadata FROM vault").fetchone()[0]);m["version"]=99
        conn.execute("UPDATE vault SET metadata=?",(json.dumps(m),))
    from pyvault.core.exceptions import UnsupportedFormatError
    with pytest.raises(UnsupportedFormatError): VaultService(path).unlock(PASSWORD)


def test_restore_replace_failure_keeps_original_vault_unlocked(tmp_path, monkeypatch):
    import os
    from pathlib import Path
    import pyvault.services.vault_service as vault_module

    current_path = tmp_path / "current.pyvault"
    backup_path = tmp_path / "backup.pyvault"
    current = VaultService(current_path)
    current.create(PASSWORD)
    current.upsert({"title": "Keep original", "password": "original-secret"})
    backup = VaultService(backup_path)
    backup.create(PASSWORD)
    backup.upsert({"title": "Backup item", "password": "backup-secret"})

    real_replace = os.replace
    failed = {"once": False}

    def fail_first_target_replace(src, dst):
        if Path(dst) == current_path and not failed["once"]:
            failed["once"] = True
            raise OSError("simulated replace failure")
        return real_replace(src, dst)

    monkeypatch.setattr(vault_module.os, "replace", fail_first_target_replace)
    with pytest.raises(OSError, match="simulated replace failure"):
        current.replace_from_backup(backup_path, PASSWORD)

    assert current.unlocked
    assert [item["title"] for item in current.credentials()] == ["Keep original"]
    reopened = VaultService(current_path)
    reopened.unlock(PASSWORD)
    assert [item["title"] for item in reopened.credentials()] == ["Keep original"]


def test_new_vault_has_social_and_email_categories(tmp_path):
    vault = VaultService(tmp_path / "categories.pyvault")
    vault.create(PASSWORD)
    categories = vault.categories()
    assert "Telegram" in categories
    assert "Instagram" in categories
    assert "Email" in categories
    assert vault.credentials() == []


def test_previous_builtin_categories_migrate_without_fake_items(tmp_path):
    path = tmp_path / "legacy-categories.pyvault"
    vault = VaultService(path)
    vault.create(PASSWORD)
    vault.set_categories(["Personal", "Work", "Development", "Social", "Finance", "Shopping", "Other"])
    vault.lock()

    reopened = VaultService(path)
    reopened.unlock(PASSWORD)
    categories = reopened.categories()
    assert "Telegram" in categories
    assert "Instagram" in categories
    assert "Email" in categories
    assert reopened.credentials() == []
