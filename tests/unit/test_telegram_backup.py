import json
from io import BytesIO

import pytest

from pyvault.core.exceptions import VaultError
from pyvault.services import telegram_backup
from pyvault.services.telegram_backup import TelegramBackupService, _valid_bot_token, _valid_chat_id


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.payload


def test_validators_accept_expected_telegram_inputs():
    assert _valid_bot_token("123456:abcdefghijklmnopqrstuvwxyzABCDE")
    assert not _valid_bot_token("bad-token")
    assert _valid_chat_id("123456789")
    assert _valid_chat_id("-100123456789")
    assert not _valid_chat_id("@amires996")


def test_username_resolves_to_private_chat_id(monkeypatch):
    payload = {
        "ok": True,
        "result": [
            {"update_id": 1, "message": {"from": {"username": "amires996"}, "chat": {"id": 987654321}}}
        ],
    }
    monkeypatch.setattr(telegram_backup, "urlopen", lambda *_args, **_kwargs: FakeResponse(payload))
    assert TelegramBackupService()._resolve_username("123456:abcdefghijklmnopqrstuvwxyzABCDE", "amires996") == "987654321"


def test_username_requires_bot_interaction_when_no_update(monkeypatch):
    monkeypatch.setattr(telegram_backup, "urlopen", lambda *_args, **_kwargs: FakeResponse({"ok": True, "result": []}))
    with pytest.raises(VaultError, match="press Start"):
        TelegramBackupService()._resolve_username("123456:abcdefghijklmnopqrstuvwxyzABCDE", "amires996")


def test_username_validation_rejects_bad_input():
    with pytest.raises(VaultError, match="does not look valid"):
        TelegramBackupService()._resolve_username("123456:abcdefghijklmnopqrstuvwxyzABCDE", "bad username")
