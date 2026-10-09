from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from urllib.parse import urlparse


def audit_credentials(items: list[dict]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    seen: dict[str, list[str]] = defaultdict(list)
    now = datetime.now(timezone.utc)
    for item in items:
        title = str(item.get("title") or "Untitled")
        password = str(item.get("password") or "")
        if not password:
            issues.append({"severity": "high", "title": title, "issue": "Empty password", "recommendation": "Add a password or remove this entry if it is not a login."})
        elif len(password) < 12:
            issues.append({"severity": "medium", "title": title, "issue": "Short password", "recommendation": "Use a longer unique password or passphrase."})
        if password:
            seen[password].append(title)
        url = str(item.get("url") or "")
        if url:
            parsed = urlparse(url)
            if parsed.scheme not in ("https", "http") or not parsed.hostname:
                issues.append({"severity": "low", "title": title, "issue": "Malformed website URL", "recommendation": "Review the saved website address."})
            elif parsed.scheme != "https":
                issues.append({"severity": "low", "title": title, "issue": "Website does not use HTTPS", "recommendation": "Check whether the service supports HTTPS."})
        updated = str(item.get("updated_at") or "")
        try:
            stamp = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            if stamp.tzinfo is None: stamp = stamp.replace(tzinfo=timezone.utc)
            if (now - stamp).days > 365:
                issues.append({"severity": "low", "title": title, "issue": "Not updated in over a year", "recommendation": "Review whether this credential should be rotated."})
        except (ValueError, TypeError):
            pass
    for names in seen.values():
        if len(names) > 1:
            for title in names:
                issues.append({"severity": "high", "title": title, "issue": "Potentially reused password", "recommendation": "Give each account a unique password."})
    return issues
