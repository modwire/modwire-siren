# Rules

- Keep the public API to the supported `modwire_siren` root imports; do not make private modules contractual.
- Use OOP: one class per file, no helper or pseudo-private functions. A function is allowed only as public API, such as `siren()`.
- Comments are public-API docstrings only. User documentation explains use, not internal inventories.
- Read `.modwire/INDEX.md` and local guidance before changing code.
- Run local commands with the user's effective privileges.
