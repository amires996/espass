from __future__ import annotations

import os
import sys
from pathlib import Path


def data_dir() -> Path:
    if sys.platform == "win32":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        path = root / "espass"
    elif sys.platform == "darwin":
        path = Path.home() / "Library" / "Application Support" / "espass"
    else:
        path = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "espass"
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_vault_path() -> Path:
    """Return the new default while keeping an existing PyVault vault discoverable."""
    current = data_dir() / "vault.pyvault"
    if current.exists():
        return current
    if sys.platform == "win32":
        legacy_root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "PyVault"
    elif sys.platform == "darwin":
        legacy_root = Path.home() / "Library" / "Application Support" / "PyVault"
    else:
        legacy_root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / "pyvault"
    legacy = legacy_root / "vault.pyvault"
    return legacy if legacy.exists() else current


def resource_path(relative_path: str) -> Path:
    """Resolve bundled assets in development and PyInstaller builds."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root) / relative_path
    return Path(__file__).resolve().parents[3] / relative_path
