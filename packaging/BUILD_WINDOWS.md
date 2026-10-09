# Build espass for Windows

Open PowerShell in the repository root. Use Python 3.12+ and activate the virtual environment.

```powershell
python -m pip install -e ".[dev]"
python -m PyInstaller --noconfirm --clean --windowed --name espass --onedir --paths src --icon assets/icons/espass.ico --add-data "assets/icons/espass.ico;assets/icons" --collect-all PySide6 --collect-all cryptography --collect-all argon2 --collect-all keyring src/pyvault/__main__.py
```

First test `dist\espass\espass.exe` on the build computer. Then open `packaging\installer\espass.iss` in Inno Setup and compile it to create `installer\espass-Setup.exe`. Test the installer and uninstall process in a Windows account that does not have Python installed.

Telegram backup is off by default. Manual uploads require confirmation. Automatic uploads on app close require a separate explicit opt-in and send only the encrypted `.pyvault` file. When automatic backups are enabled, the bot token is stored using the operating-system credential manager; the destination is stored in local app settings. Never commit or share a Telegram bot token.
