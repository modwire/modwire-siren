# Architecture

`modwire-siren` has three bounded contexts and a technical package entry:

- `api` composes the public `siren` callable.
- `compiler` turns OpenAPI into an immutable Siren contract.
- `runtime` owns contracts and projects them with request context.
- Root `__init__.py` is exports only; it is the technical package entry.

`.modwire/architecture.yaml` makes those dependencies explicit. `make modwire` scopes the map to the source package; architectural rules belong in boundary rules, not an aspirational file-shape baseline.
