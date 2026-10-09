from __future__ import annotations

import json
from pathlib import Path

from pyvault.utils.paths import data_dir

DEFAULTS = {"theme": "dark", "auto_lock_minutes": 5, "clipboard_clear_seconds": 30,
            "generator_length": 20, "window_width": 1180, "window_height": 760,
            "telegram_auto_backup": False, "telegram_recipient": ""}


class Config:
    def __init__(self, path: Path | None = None):
        self.path = path or data_dir() / "settings.json"
        self.values = dict(DEFAULTS)
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                self.values.update({k: v for k, v in loaded.items() if k in DEFAULTS})
        except (OSError, json.JSONDecodeError):
            pass
        if self.values["theme"] not in ("dark", "light", "system"):
            self.values["theme"] = "dark"
        if not isinstance(self.values["auto_lock_minutes"], int) or not 0 <= self.values["auto_lock_minutes"] <= 60:
            self.values["auto_lock_minutes"] = 5
        if not isinstance(self.values["clipboard_clear_seconds"], int) or not 5 <= self.values["clipboard_clear_seconds"] <= 600:
            self.values["clipboard_clear_seconds"] = 30
        if not isinstance(self.values["generator_length"], int) or not 12 <= self.values["generator_length"] <= 128:
            self.values["generator_length"] = 20
        if not isinstance(self.values["window_width"], int) or not 900 <= self.values["window_width"] <= 5000:
            self.values["window_width"] = 1240
        if not isinstance(self.values["window_height"], int) or not 620 <= self.values["window_height"] <= 5000:
            self.values["window_height"] = 800
        if not isinstance(self.values["telegram_auto_backup"], bool):
            self.values["telegram_auto_backup"] = False
        if not isinstance(self.values["telegram_recipient"], str):
            self.values["telegram_recipient"] = ""

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.values, indent=2), encoding="utf-8")
        tmp.replace(self.path)
