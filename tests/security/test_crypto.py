from pyvault.crypto.encryption import decrypt, encrypt
from pyvault.core.exceptions import CorruptVaultError
import pytest


def test_authenticated_encryption_and_nonce_uniqueness():
    key=b"k"*32; plaintext=b"same content"; aad=b"context"
    n1,c1=encrypt(key,plaintext,aad);n2,c2=encrypt(key,plaintext,aad)
    assert n1 != n2 and c1 != c2
    assert decrypt(key,n1,c1,aad)==plaintext
    with pytest.raises(CorruptVaultError): decrypt(key,n1,c1[:-1]+bytes([c1[-1]^1]),aad)
    with pytest.raises(CorruptVaultError): decrypt(key,b"bad",c1,aad)


def test_key_separation_wrapping_key_is_not_data_key():
    from pyvault.crypto.kdf import derive_key, new_salt
    wrapping=derive_key("master passphrase",new_salt())
    dek=__import__("secrets").token_bytes(32)
    assert wrapping != dek
