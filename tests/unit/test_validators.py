import pytest

from pyvault.core.exceptions import ValidationError
from pyvault.core.models import Credential
from pyvault.core.validators import validate_credential, validate_master_password


def test_master_password_validation():
    with pytest.raises(ValidationError): validate_master_password("short")
    with pytest.raises(ValidationError): validate_master_password("a" * 12, "b" * 12)
    validate_master_password("a long and unique passphrase")


def test_credential_validation():
    with pytest.raises(ValidationError): validate_credential(Credential(title=" "))
    with pytest.raises(ValidationError): validate_credential(Credential(title="Example", url="javascript:alert(1)"))
    validate_credential(Credential(title="Software license", password="abc"))
