# espass

**espass** is a local-first desktop password manager built with Python, PySide6, SQLite, Argon2id and AES-256-GCM.

> **Security note:** This is a community-sized personal project and has not received an independent security audit. Use at your own risk and keep a separate encrypted backup.

## Features

- Polished desktop interface with dark and light themes.
- Master-password-protected vault; the master password is never saved.
- Argon2id key derivation, a random data-encryption key, and AES-256-GCM authenticated encryption.
- Encrypted credential payload in SQLite; titles, usernames, URLs, notes, categories, tags and passwords are encrypted together.
- Add, edit, delete, search, categories, favorites and recently added items.
- Secure password generator and offline password-hygiene checks.
- Encrypted backup and restore with backup validation.
- Manual Telegram backup sends only the encrypted vault after explicit confirmation. Automatic backup on close is optional and off by default; if enabled, the bot token is stored through the operating-system credential manager.
- Auto-lock, clipboard clearing, keyboard shortcuts and installer configuration.

## Requirements

Python 3.12 or later. Dependencies are listed in `pyproject.toml`.

## Run from source

### Windows PowerShell

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pyvault
```

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pyvault
```

## Tests

```bash
pytest
ruff check .
```

## Windows build

Run PowerShell from the repository root with `.venv` active:

```powershell
python -m pip install -e ".[dev]"
python -m PyInstaller --noconfirm --clean --windowed --name espass --onedir --paths src --icon assets/icons/espass.ico --add-data "assets/icons/espass.ico;assets/icons" --collect-all PySide6 --collect-all cryptography --collect-all argon2 src/pyvault/__main__.py
```

Test `dist\espass\espass.exe`. Then open `packaging\installer\espass.iss` in Inno Setup and choose **Build → Compile**. This creates `installer\espass-Setup.exe`.

## Telegram backup limitations

Create a bot using `@BotFather`, then start the bot from the account that should receive the backup. The app accepts a numeric chat ID or a username. For a private user, Telegram's Bot API does not let a bot initiate a chat using only a username; espass tries to match the username in recent bot updates and explains how to proceed if it cannot. Public group/channel usernames may be used directly when the bot has permission to post.

Telegram stores the uploaded encrypted vault file. It does not receive the master password or a plaintext export of the passwords. The backup still requires the master password to open. Never share or commit a bot token.

## Data location

New settings and default vault data use the platform's espass user data directory (`%LOCALAPPDATA%\espass` on Windows, `~/Library/Application Support/espass` on macOS, or `$XDG_DATA_HOME/espass` on Linux). An existing default vault from the previous PyVault folder remains discoverable by the welcome screen. You can also select a `.pyvault` file from any location.

## Limitations

- No independent security audit.
- Python cannot guarantee zeroization of every secret copy in process memory.
- A compromised OS, keylogger, malware, screenshots, or an unlocked session can expose secrets.
- The security audit uses heuristics and does not query breach databases.
- Backups are file-based and do not merge vaults.

Source code: https://github.com/amires996


New vaults include starter categories for Telegram, Instagram, Email, Social Media, Work, Banking, Shopping, Gaming, Development, Personal, and Other. These are categories only; espass never creates fake or empty password entries.
