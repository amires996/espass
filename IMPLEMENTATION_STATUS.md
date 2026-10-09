# Implementation status

Verified in the available build environment (Linux, Python 3.13, cryptography, argon2-cffi, pytest):

- `python -m compileall -q src tests`: passed.
- `pytest -q`: 22 passed, 1 skipped. The UI import test is skipped because PySide6 is not installed in this environment.
- Ruff is not installed in this environment, so linting was not verified.
- The PySide6 desktop UI was not launched here and a Windows EXE/installer was not built here. Test those on Windows before distributing the installer.

This is a tested source release, not an independently audited security product.
