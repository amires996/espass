from __future__ import annotations

import secrets
import string

AMBIGUOUS = set("Il1O0|`'\"{}[]()<>.,;:")


def generate_password(length: int = 20, *, uppercase: bool = True, lowercase: bool = True,
                      digits: bool = True, symbols: bool = True, exclude_ambiguous: bool = False,
                      custom_characters: str = "") -> str:
    if not 4 <= length <= 4096:
        raise ValueError("Password length must be between 4 and 4096 characters.")
    groups: list[str] = []
    if uppercase: groups.append(string.ascii_uppercase)
    if lowercase: groups.append(string.ascii_lowercase)
    if digits: groups.append(string.digits)
    if symbols: groups.append("!@#$%^&*_-+=?/~")
    if custom_characters: groups.append(custom_characters)
    if exclude_ambiguous:
        groups = ["".join(c for c in group if c not in AMBIGUOUS) for group in groups]
    groups = ["".join(dict.fromkeys(g)) for g in groups if g]
    if not groups:
        raise ValueError("Select at least one non-empty character set.")
    alphabet = "".join(dict.fromkeys("".join(groups)))
    if len(groups) > length:
        raise ValueError("Password length is too short to include every selected character type.")
    # Guarantee one from each selected group, then use secrets.choice and unbiased Fisher-Yates.
    chars = [secrets.choice(group) for group in groups]
    chars.extend(secrets.choice(alphabet) for _ in range(length - len(chars)))
    for i in range(len(chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        chars[i], chars[j] = chars[j], chars[i]
    return "".join(chars)


def estimate_strength(password: str) -> dict[str, str | int]:
    if not password:
        return {"score": 0, "label": "Empty", "suggestion": "Generate a unique password."}
    variety = sum((any(c.islower() for c in password), any(c.isupper() for c in password),
                   any(c.isdigit() for c in password), any(not c.isalnum() for c in password)))
    score = min(4, (1 if len(password) >= 12 else 0) + (1 if len(password) >= 16 else 0) +
                (1 if len(password) >= 24 else 0) + (1 if variety >= 3 else 0))
    label = ["Very weak", "Weak", "Fair", "Strong", "Very strong"][score]
    suggestion = "Prefer a longer unique password or passphrase." if score < 3 else "Avoid reusing this password on other sites."
    return {"score": score, "label": label, "suggestion": suggestion}
