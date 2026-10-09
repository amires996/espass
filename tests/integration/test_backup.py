import pytest

from pyvault.core.exceptions import InvalidPasswordError, VaultError
from pyvault.services.backup_service import BackupService
from pyvault.services.vault_service import VaultService

PASSWORD = "backup test master passphrase long"


def test_backup_restore_roundtrip(tmp_path):
    path=tmp_path/"main.pyvault"; backup=tmp_path/"backup.pyvault"
    vault=VaultService(path);vault.create(PASSWORD);vault.upsert({"title":"Example","password":"secret"})
    BackupService().create(vault,backup)
    with pytest.raises(VaultError): BackupService().create(vault,backup)
    vault.upsert({"title":"Second","password":"other"})
    vault.replace_from_backup(backup,PASSWORD)
    assert [x["title"] for x in vault.credentials()]==["Example"]


def test_wrong_backup_password_does_not_replace_current(tmp_path):
    p=tmp_path/"main.pyvault";b=tmp_path/"backup.pyvault"
    current=VaultService(p);current.create(PASSWORD);current.upsert({"title":"Keep me","password":"x"})
    candidate=VaultService(b);candidate.create("another backup master password")
    with pytest.raises(InvalidPasswordError): current.replace_from_backup(b,PASSWORD)
    assert current.unlocked and current.credentials()[0]["title"]=="Keep me"
