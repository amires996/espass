# Cryptographic design

Format version 1 uses Argon2id (`argon2-cffi`) with a 16-byte random salt, 64 MiB memory cost, 3 iterations, parallelism 2, and a 32-byte output. Parameters are stored in metadata and validated against safe bounds before allocation. AES-256-GCM is used through `cryptography`.

A fresh random 32-byte data-encryption key (DEK) encrypts the serialized vault. The Argon2id output wraps the DEK. Independent 12-byte random nonces are generated for wrapping and payload encryption. Associated data binds a canonical representation of the format version and KDF metadata to each ciphertext. The encrypted DEK acts as the password verifier: only correct key derivation can authenticate and unwrap it.

This is not a claim that defaults are optimal on every machine. KDF settings need benchmarking and version-aware migration. AES-GCM nonce uniqueness is probabilistic with random 96-bit nonces; the small number of encryptions per DEK keeps collision risk very low. Do not reuse a DEK/nonce pair. Authentication errors fail closed.
