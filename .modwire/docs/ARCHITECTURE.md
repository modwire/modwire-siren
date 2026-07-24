# Architecture

`modwire-siren` has a small compiler/runtime architecture:

- The package API (`__init__.py`, `extras.py`) exposes `SirenContext` and `siren()`.
- The OpenAPI source, service, and builder compile an OpenAPI document into the immutable Siren contract.
- The engine projects that contract and request context into a Siren document.
- Contracts are the shared core; they never depend on the compiler or engine.

`.modwire/architecture.yaml` makes those dependencies explicit and keeps the source package, tests, and tooling classified. The current shape settings describe the existing codebase; architectural rules belong in boundary rules, not an aspirational file-shape baseline.
