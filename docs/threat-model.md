# Threat model

## Assets
Master password during entry, derived wrapping key, DEK, decrypted credentials, clipboard contents, encrypted vault and backups.

## Assumptions and protections
- A stolen vault/backup exposes metadata and ciphertext, but not credential fields without guessing the master password.
- AES-GCM detects ciphertext and authenticated-metadata modification.
- SQLite transactions reduce partial writes; restore validates/decrypts before replacing the current vault.
- Logs are configured not to include credential values or keys.
- Malformed KDF parameters are bounded before expensive derivation.

## Out of scope / residual risk
A weak master password can be guessed offline. Malware, a compromised OS, keyloggers, memory dumps, swap/hibernation, clipboard managers, shoulder surfing and screen capture can expose unlocked data. Python does not promise reliable memory zeroization. Filesystem permissions depend on the OS and user account. The audit is heuristic and does not query breach services. There is no independent security audit. Use backups and test recovery before relying on the application.
