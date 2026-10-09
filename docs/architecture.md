# Architecture

- `core`: credential model, validation, and domain errors.
- `crypto`: KDF, AES-GCM primitives, and versioned vault format.
- `storage`: SQLite repository. The sensitive vault state is a single authenticated encrypted JSON payload.
- `services`: vault lifecycle, credential operations, password generation, offline audit, backup, and session timing.
- `ui`: PySide6 widgets and application shell; no cryptographic primitives live in UI code.

Every state mutation serializes the whole in-memory vault and commits one encrypted payload in a SQLite transaction. This intentionally favors a small, auditable data model over indexed plaintext metadata. It is suitable for modest personal vaults, not concurrent multi-process editing.
