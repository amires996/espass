# ESPass 🔐
### Your passwords. Your device. Your control.

<img width="275" height="275" alt="image" src="https://github.com/user-attachments/assets/89180ef4-281d-4d87-9491-c8c95fb2296b" />


**ESPass** is a modern, local-first desktop password manager built with Python, PySide6, SQLite, Argon2id, and AES-256-GCM.

Designed for privacy, simplicity, and security, ESPass keeps your credentials encrypted locally while providing a polished desktop experience on Windows, Linux, and macOS.

> [!IMPORTANT]
> ESPass is a community-sized personal project and has not undergone an independent security audit. Use it at your own risk, and always maintain a separate encrypted backup of your vault.

---

## ✨ Features

- **🔒 Encrypted Vault** — Protect your credentials with a master password that is never stored.
- **🛡️ Modern Cryptography** — Argon2id key derivation, a randomly generated data-encryption key, and AES-256-GCM authenticated encryption.
- **💻 Local-First Privacy** — Your vault is stored locally, with credential fields encrypted together in SQLite.
- **🎨 Desktop Experience** — A polished interface with dark and light themes.
- **🌍 Bilingual Interface** — English and Persian (فارسی) interface support.
- **🗂️ Credential Organization** — Add, edit, delete, search, categorize, tag, and favorite entries.
- **🔑 Password Generator** — Generate strong, customizable passwords.
- **🧪 Password Hygiene** — Run offline password-quality checks using local heuristics.
- **📦 Encrypted Backups** — Create, validate, and restore encrypted vault backups.
- **✈️ Telegram Backup** — Manually send an encrypted vault backup after explicit confirmation.
- **⏱️ Auto-Lock** — Lock your vault automatically after inactivity.
- **📋 Clipboard Protection** — Clear copied passwords automatically.
- **⌨️ Keyboard Shortcuts** — Access common actions more efficiently.

New vaults include starter categories for Telegram, Instagram, Email, Social Media, Work, Banking, Shopping, Gaming, Development, Personal, and Other. These are categories only; ESPass never creates fake or empty credential entries.

## 🖥️ Screenshots

Screenshots and animated previews can be added here as the interface evolves.

<!-- Add screenshots using:
![ESPass Dashboard](assets/screenshots/dashboard.png)
-->

## 📥 Installation

### Windows

Download the latest Windows installer from the project's [GitHub Releases](https://github.com/amires996) page, if a release is available.

1. Download `espass-Setup.exe`.
2. Run the installer.
3. Follow the installation instructions.
4. Launch ESPass and create or open your vault.

> **Note:** Publish the installer as a GitHub Release asset and replace the link above with the repository's actual Releases URL when available.

### Run from Source

**Requirements:** Python 3.12 or later.

#### Windows PowerShell

```powershell
git clone <YOUR_REPOSITORY_URL>
cd espass

python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

python -m pip install -e ".[dev]"
python -m pyvault
```

#### Linux

```bash
git clone <YOUR_REPOSITORY_URL>
cd espass

python3 -m venv .venv
source .venv/bin/activate

python -m pip install -e '.[dev]'
python -m pyvault
```

## 🧪 Development

Run the test suite:

```bash
pytest
```

Check code quality:

```bash
ruff check .
```

## 🏗️ Build for Windows

Activate your virtual environment and run the following command from the repository root:

```powershell
python -m pip install -e ".[dev]"

python -m PyInstaller --noconfirm --clean --windowed `
  --name espass `
  --onedir `
  --paths src `
  --icon assets/icons/espass.ico `
  --add-data "assets/icons/espass.ico;assets/icons" `
  --collect-all PySide6 `
  --collect-all cryptography `
  --collect-all argon2 `
  src/pyvault/__main__.py
```

Test the generated application at:

```text
dist\espass\espass.exe
```

To create the Windows installer, open `packaging/installer/espass.iss` in Inno Setup and select **Build → Compile**.

The resulting installer should be available at:

```text
installer\espass-Setup.exe
```

## ☁️ Telegram Backup

ESPass supports optional Telegram-based encrypted backups.

To configure it:

1. Create a bot using [@BotFather](https://t.me/BotFather).
2. Start a conversation with the bot from the account that should receive backups.
3. Configure the bot token and destination chat.
4. Confirm before sending a manual backup.

Private Telegram users generally must initiate the conversation before a bot can message them. A username alone does not allow a bot to start a private conversation.

The uploaded file contains the encrypted vault, not a plaintext password export. The master password is never sent to Telegram.

Automatic backup on application close is optional and disabled by default. If enabled, the bot token is stored through the operating-system credential manager.

**Never publish or commit your Telegram bot token.**

## 📂 Data Storage

ESPass stores application settings and its default vault in the platform-specific application data directory:

| Platform | Default location |
|---|---|
| Windows | `%LOCALAPPDATA%\espass` |
| macOS | `~/Library/Application Support/espass` |
| Linux | `$XDG_DATA_HOME/espass` |

If `XDG_DATA_HOME` is not set, Linux applications commonly use `~/.local/share` as the data directory.

Existing vaults from the previous PyVault directory remain discoverable through the welcome screen. You can also select a `.pyvault` file from another location.

## 🔐 Security Model

ESPass uses several layers of protection:

- Argon2id for deriving encryption keys from the master password.
- A randomly generated data-encryption key.
- AES-256-GCM for authenticated encryption.
- Encrypted credential payloads, including titles, usernames, URLs, notes, categories, tags, and passwords.
- No plaintext master-password storage.
- Encrypted vault backups that still require the master password to unlock.

### Security Limitations

- ESPass has not undergone an independent security audit.
- Python cannot guarantee complete zeroization of all secret copies in memory.
- Malware, keyloggers, compromised operating systems, screenshots, or unlocked sessions may expose credentials.
- Password-hygiene checks use local heuristics and do not query data-breach databases.
- Backups are file-based; restoring a backup does not merge two vaults.

## 🌐 Language Support

ESPass is intended to support both English and Persian (فارسی), including appropriate left-to-right and right-to-left layouts.

Contributions to translations, accessibility, and interface improvements are welcome.

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome.

Before submitting changes:

1. Keep security-sensitive changes small and reviewable.
2. Add or update tests where appropriate.
3. Run `pytest` and `ruff check .`.
4. Never include real credentials, vault files, secrets, or bot tokens in commits.

## 📜 License

No license has been specified in this README. Add a `LICENSE` file before presenting the project as open source, and choose a license that matches your intentions.

## 👨‍💻 Author

Created by [@amires996](https://github.com/amires996).

---

**ESPass — Privacy by design. Security by default.**
