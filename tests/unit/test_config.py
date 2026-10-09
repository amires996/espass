import json

from pyvault.config import Config


def test_config_defaults_and_invalid_values(tmp_path):
    path=tmp_path/"settings.json";path.write_text(json.dumps({"theme":"unknown","auto_lock_minutes":999,"secret":"not loaded"}))
    c=Config(path)
    assert c.values["theme"]=="dark"
    assert c.values["auto_lock_minutes"]==5
    assert "secret" not in c.values
    c.values["theme"]="light";c.save();assert Config(path).values["theme"]=="light"


def test_telegram_auto_backup_is_opt_in(tmp_path):
    c = Config(tmp_path / "settings.json")
    assert c.values["telegram_auto_backup"] is False
    assert c.values["telegram_recipient"] == ""
    c.values["telegram_auto_backup"] = True
    c.values["telegram_recipient"] = "@example_user"
    c.save()
    loaded = Config(tmp_path / "settings.json")
    assert loaded.values["telegram_auto_backup"] is True
    assert loaded.values["telegram_recipient"] == "@example_user"
