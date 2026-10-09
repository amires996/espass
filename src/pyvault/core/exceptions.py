class PyVaultError(Exception):
    """Base exception for safe, expected application errors."""

class VaultError(PyVaultError):
    pass

class VaultLockedError(VaultError):
    pass

class InvalidPasswordError(VaultError):
    pass

class CorruptVaultError(VaultError):
    pass

class UnsupportedFormatError(VaultError):
    pass

class ValidationError(PyVaultError):
    pass
