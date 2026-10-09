from __future__ import annotations

from pyvault.core.exceptions import VaultError

_SERVICE_NAME = "espass.telegram"
_TOKEN_KEY = "bot-token"


def store_bot_token(token: str) -> None:
    """Store the bot token using the operating system credential vault."""
    try:
        import keyring

        keyring.set_password(_SERVICE_NAME, _TOKEN_KEY, token)
    except Exception:
        raise VaultError(
            "Could not store the Telegram token securely. Install the application dependencies "
            "and make sure the operating-system credential manager is available."
        ) from None


def get_bot_token() -> str | None:
    try:
        import keyring

        return keyring.get_password(_SERVICE_NAME, _TOKEN_KEY)
    except Exception:
        return None


def delete_bot_token() -> None:
    try:
        import keyring

        keyring.delete_password(_SERVICE_NAME, _TOKEN_KEY)
    except Exception:
        pass
