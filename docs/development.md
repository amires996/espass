# Development

Install `pip install -e '.[dev]'`, run `pytest`, and run `ruff check .`. Core services are designed to run without Qt so cryptographic/storage tests can execute headlessly. UI tests need a working Qt platform plugin; use `QT_QPA_PLATFORM=offscreen` only in headless CI. Keep test vaults in temporary directories and never use production credentials in fixtures.
