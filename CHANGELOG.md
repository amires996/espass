# Changelog

## 1.0.0 — espass redesign
- Reworked the desktop interface and credential editor.
- Added clearer vault statistics, category filtering, keyboard shortcuts and creator attribution.
- Improved Telegram backup recipient handling for numeric IDs and usernames, with explicit limitations for private chats.
- Updated Windows installer and PyInstaller build instructions.
- Added automated Telegram input and username-resolution tests.

The application has not received an independent security audit.


## 1.1.0
- Reworked dark/light palettes to avoid mismatched black panels and improve contrast.
- Removed creator-credit text from the UI; retained the GitHub profile link.
- Added Windows taskbar AppUserModelID handling and documented icon bundling.
- Added Telegram, Instagram, and Email starter categories, including migration of the previous built-in category list.
- Added opt-in automatic encrypted Telegram backup on app close; bot token is stored via the OS credential manager.
