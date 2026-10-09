# Contributing

1. Create a virtual environment and install `pip install -e '.[dev]'`.
2. Run `pytest` and `ruff check .` before submitting changes.
3. Add regression tests for bug fixes, especially crypto/storage changes.
4. Never commit real vaults, credentials, backups, screenshots containing secrets, or keys.
5. Keep cryptography out of UI modules; explain any format changes and add migrations.
6. For security-sensitive reports, do not open a public issue containing exploit details. See `SECURITY.md`.
