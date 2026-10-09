import string

import pytest

from pyvault.services.password_generator import estimate_strength, generate_password


def test_generator_length_and_character_sets():
    value = generate_password(32, uppercase=True, lowercase=True, digits=True, symbols=True)
    assert len(value) == 32
    assert any(c in string.ascii_uppercase for c in value)
    assert any(c in string.ascii_lowercase for c in value)
    assert any(c in string.digits for c in value)
    assert any(c in "!@#$%^&*_-+=?/" for c in value)


def test_generator_excludes_ambiguous():
    value = generate_password(80, exclude_ambiguous=True)
    assert not set(value) & set("Il1O0|`'\"{}[]()<>.,;:")


def test_generator_rejects_impossible_options():
    with pytest.raises(ValueError):
        generate_password(4, uppercase=False, lowercase=False, digits=False, symbols=False)
    with pytest.raises(ValueError):
        generate_password(3, uppercase=True, lowercase=True, digits=True, symbols=True)


def test_strength_is_heuristic_and_empty_supported():
    assert estimate_strength("")["score"] == 0
    assert estimate_strength("abc")["score"] < estimate_strength("Correct-Horse-Battery-Example-72!")["score"]
