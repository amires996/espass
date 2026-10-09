from __future__ import annotations

from urllib.parse import urlparse

from pyvault.core.exceptions import ValidationError
from pyvault.core.models import Credential


def validate_master_password(password: str, confirmation: str | None = None) -> None:
    if not isinstance(password, str) or len(password) < 12:
        raise ValidationError("Use a master password or passphrase of at least 12 characters.")
    if len(password.encode("utf-8")) > 4096:
        raise ValidationError("The master password is too long (maximum 4096 UTF-8 bytes).")
    if confirmation is not None and password != confirmation:
        raise ValidationError("The master passwords do not match.")


def validate_credential(item: Credential) -> None:
    if not item.title.strip():
        raise ValidationError("A title is required.")
    if len(item.title) > 300 or len(item.username) > 4096 or len(item.url) > 4096 or len(item.notes) > 100_000:
        raise ValidationError("One or more fields exceed the supported size.")
    if not isinstance(item.tags, list) or any(not isinstance(tag, str) for tag in item.tags):
        raise ValidationError("Tags must be a list of text values.")
    if item.url:
        parsed = urlparse(item.url)
        if parsed.scheme not in ("http", "https") or not parsed.hostname:
            raise ValidationError("Website URL must start with http:// or https:// and include a host.")
