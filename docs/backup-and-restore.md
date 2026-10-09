# Backup and restore

A backup is a byte-for-byte copy of the SQLite vault database; credential payload and DEK are still encrypted. Public format metadata is present. Create backups while the vault is unlocked so SQLite is in a consistent state. Backups do not contain the master password and cannot be recovered without it.

Restore validates the SQLite structure and cryptographically unlocks the candidate using the supplied master password before replacing the current vault. Keep a separate backup before restoring. Restore replaces rather than merges. A damaged or unsupported backup is rejected; the original vault should remain untouched.
