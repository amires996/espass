from __future__ import annotations

from pathlib import Path

from pyvault.core.exceptions import VaultError
from pyvault.services.vault_service import VaultService


class BackupService:
    def create(self, vault: VaultService, destination: str | Path) -> None:
        if not vault.unlocked:
            raise VaultError("Unlock the vault before creating a backup.")
        vault.repository.copy_backup(destination)

    def validate(self, path: str | Path, password: str) -> bool:
        candidate = VaultService(path)
        candidate.unlock(password)
        candidate.lock()
        return True
