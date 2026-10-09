# Security Policy

espass is an early release candidate and has not undergone an independent audit. Do not send real secrets in bug reports.

## Reporting a vulnerability

Please privately contact the repository maintainers through a verified security contact configured by the repository owner. Do not publish exploit details before a fix is available. This template repository does not currently define a maintainer email address; verify the project's official repository before sharing sensitive reports.

## Security properties

- Argon2id derives a wrapping key from the master password and a random salt.
- AES-256-GCM wraps a random DEK and encrypts the full serialized vault payload with independent random nonces.
- Format/KDF metadata is bound as authenticated associated data.
- The master password and derived keys are not persisted or logged.
- SQLite contains only public crypto metadata and ciphertext for sensitive content.

## Limitations

Weak master passwords remain vulnerable to offline guessing. Local malware, a compromised operating system, memory inspection, keyloggers, clipboard managers, and screen capture are out of scope. Python immutable objects cannot be reliably wiped. The application is not certified or independently audited.
