# Rules

- Keep the public API to the supported `modwire_siren` root imports; do not make private modules contractual.
- Use OOP: one class per file, no helper or pseudo-private functions. A function is allowed only as public API, such as `siren()`.
- Keep contexts feature-packaged: root modules expose only the minimal context API and composition entry points.
  Collaborating contracts, values, and services belong in a feature subpackage; flat service fields are forbidden.
- `wiring.py` is the sole technical-plumbing exception: it may group the discovery and application-container
  classes so that all cross-context wiring is visible in one place.
- Comments are public-API docstrings only. User documentation explains use, not internal inventories.
- Read `.modwire/INDEX.md` and local guidance before changing code.
- Run local commands with the user's effective privileges.
