import pytest

from pyvault.core.exceptions import CorruptVaultError
from pyvault.crypto.kdf import DEFAULT_KDF, derive_key, new_salt, validate_kdf_params


def test_salt_and_derived_key():
    a, b = new_salt(), new_salt()
    assert len(a) == 16 and a != b
    assert derive_key("test passphrase", a) == derive_key("test passphrase", a)
    assert derive_key("test passphrase", a) != derive_key("different passphrase", a)


def test_kdf_parameters_are_bounded():
    validate_kdf_params(DEFAULT_KDF)
    with pytest.raises(CorruptVaultError): validate_kdf_params({**DEFAULT_KDF, "memory_cost": 999999999})
    with pytest.raises(CorruptVaultError): validate_kdf_params({**DEFAULT_KDF, "name": "pbkdf2"})
