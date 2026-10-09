from __future__ import annotations

import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from pyvault.core.exceptions import CorruptVaultError, InvalidPasswordError

NONCE_SIZE = 12
KEY_SIZE = 32


def encrypt(key: bytes, plaintext: bytes, aad: bytes) -> tuple[bytes, bytes]:
    if len(key) != KEY_SIZE:
        raise ValueError("Invalid encryption key length")
    nonce = os.urandom(NONCE_SIZE)
    return nonce, AESGCM(key).encrypt(nonce, plaintext, aad)


def decrypt(key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes, *, password_check: bool = False) -> bytes:
    if len(key) != KEY_SIZE or len(nonce) != NONCE_SIZE or len(ciphertext) < 16:
        raise CorruptVaultError("Malformed encrypted data.")
    try:
        return AESGCM(key).decrypt(nonce, ciphertext, aad)
    except InvalidTag:
        if password_check:
            raise InvalidPasswordError("Incorrect master password or invalid vault.") from None
        raise CorruptVaultError("Vault authentication failed; data may be damaged or modified.") from None
