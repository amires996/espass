from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pyvault.core.exceptions import VaultError
from pyvault.services.backup_service import BackupService
from pyvault.services.vault_service import VaultService

_USERNAME_RE = re.compile(r"^@?[A-Za-z][A-Za-z0-9_]{4,31}$")


class TelegramBackupService:
    """Send a user-confirmed encrypted vault copy through the Telegram Bot API.

    A personal Telegram username is not a valid private-chat destination by itself.
    For private users, Telegram only lets bots message chats that have already started
    the bot; we resolve the username from recent bot updates when possible.
    """

    def send_encrypted_backup(self, vault: VaultService, bot_token: str, recipient: str) -> None:
        if not vault.unlocked:
            raise VaultError("Unlock espass before sending a backup.")

        token = bot_token.strip()
        destination = recipient.strip()
        if not token or not destination:
            raise VaultError("Enter both the Telegram bot token and a username or numeric chat ID.")
        if not _valid_bot_token(token):
            raise VaultError("The bot token format does not look valid. Copy it from @BotFather.")

        # Resolve a private username only from updates generated after the recipient
        # has opened the bot and pressed Start. Public group/channel usernames can be
        # passed directly to sendDocument by Telegram's Bot API.
        if destination.startswith("@") or _looks_like_username(destination):
            username = destination.removeprefix("@").casefold()
            try:
                destination = self._resolve_username(token, username)
            except VaultError as exc:
                # The Bot API accepts @username directly for public channels/groups.
                # A private person's username must resolve to a chat that has started the bot.
                if "could not resolve" not in str(exc).casefold():
                    raise
                destination = "@" + username

        if not _valid_chat_id(destination) and not destination.startswith("@"):
            raise VaultError("Enter a numeric Telegram chat ID or a valid @username.")

        import tempfile

        with tempfile.TemporaryDirectory(prefix="espass-backup-") as temp_dir:
            backup_path = Path(temp_dir) / "espass-encrypted-backup.pyvault"
            BackupService().create(vault, backup_path)
            try:
                self._send_document(token, destination, backup_path)
            except VaultError as exc:
                if destination.startswith("@") and "chat not found" in str(exc).casefold():
                    raise VaultError(
                        f"Telegram could not send to {destination}. For a private user, open the bot, "
                        "press Start and send it a message; then retry or enter the numeric chat ID. "
                        "A username alone only works directly for a public group/channel."
                    ) from None
                raise

    def _resolve_username(self, token: str, username: str) -> str:
        if not _USERNAME_RE.fullmatch(username):
            raise VaultError("That Telegram username does not look valid. Use @username or a numeric chat ID.")
        result = self._api_json(token, "getUpdates", payload={"limit": 100, "timeout": 0})
        for update in result.get("result", []):
            message = update.get("message") or update.get("edited_message") or update.get("channel_post") or {}
            sender = message.get("from") or {}
            chat = message.get("chat") or {}
            sender_username = str(sender.get("username", "")).casefold()
            chat_username = str(chat.get("username", "")).casefold()
            if username in (sender_username, chat_username):
                chat_id = chat.get("id")
                if chat_id is not None:
                    return str(chat_id)
        raise VaultError(
            f"Telegram could not resolve @{username}. Open your bot in Telegram, press Start, "
            "send it a message, then try again. If this still fails, use your numeric chat ID. "
            "Telegram does not allow bots to start a private chat using only a username."
        )

    def _send_document(self, token: str, destination: str, backup_path: Path) -> None:
        boundary = "----espass" + uuid.uuid4().hex
        body = bytearray()
        self._add_field(body, boundary, "chat_id", destination.encode("utf-8"))
        self._add_field(
            body,
            boundary,
            "caption",
            b"Encrypted espass vault backup. The master password is required to open it.",
        )
        body.extend(f"--{boundary}\r\n".encode("ascii"))
        body.extend(
            b'Content-Disposition: form-data; name="document"; filename="espass-encrypted-backup.pyvault"\r\n'
        )
        body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
        body.extend(backup_path.read_bytes())
        body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode("ascii"))
        request = Request(
            f"https://api.telegram.org/bot{token}/sendDocument",
            data=bytes(body),
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        self._request_json(request)

    @staticmethod
    def _add_field(body: bytearray, boundary: str, name: str, value: bytes) -> None:
        body.extend(f"--{boundary}\r\n".encode("ascii"))
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("ascii"))
        body.extend(value)
        body.extend(b"\r\n")

    def _api_json(self, token: str, method: str, payload: dict) -> dict:
        request = Request(
            f"https://api.telegram.org/bot{token}/{method}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        return self._request_json(request)

    @staticmethod
    def _request_json(request: Request) -> dict:
        try:
            with urlopen(request, timeout=30) as response:
                result = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            try:
                payload = json.loads(exc.read().decode("utf-8"))
                detail = payload.get("description", "Telegram rejected the request.")
            except Exception:
                detail = "Telegram rejected the request. Check the bot token and destination."
            raise VaultError(str(detail)) from None
        except (URLError, TimeoutError, OSError, json.JSONDecodeError):
            raise VaultError("Could not reach Telegram. Check your internet connection and try again.") from None
        if not isinstance(result, dict) or not result.get("ok"):
            detail = result.get("description", "Telegram could not complete the request.") if isinstance(result, dict) else "Telegram returned an invalid response."
            raise VaultError(str(detail))
        return result


def _valid_bot_token(token: str) -> bool:
    if ":" not in token:
        return False
    bot_id, secret = token.split(":", 1)
    return bot_id.isdigit() and len(secret) >= 20 and all(ch.isalnum() or ch in "_-" for ch in secret)


def _looks_like_username(value: str) -> bool:
    return bool(_USERNAME_RE.fullmatch(value))


def _valid_chat_id(value: str) -> bool:
    return bool(re.fullmatch(r"-?\d{1,25}", value))
