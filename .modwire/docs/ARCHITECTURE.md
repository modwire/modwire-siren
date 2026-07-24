# Architecture

`modwire-siren` has four bounded contexts and a technical package entry:

- `api` composes the public `siren` callable.
- `compiler` turns OpenAPI into an immutable Siren contract.
- `runtime` owns contracts and projects them with request context.
- `conformance` owns development-time comparison of the official Siren contract and the public implementation.
- `wiring.py` is technical composition plumbing, not a bounded context. It discovers registrations across
  bounded contexts and assembles them without becoming part of their domain logic.
- Root `__init__.py` is exports only; it is the technical package entry.

`.modwire/architecture.yaml` makes those dependencies explicit. `make modwire` maps the source package, tests, and support scripts so boundary rules can require tests to use only the supported package API; architectural rules belong in boundary rules, not an aspirational file-shape baseline.

Each bounded context uses feature subpackages with minimal `__init__.py` APIs. A context root contains only
its public types and composition entry points. When a capability has collaborating contracts, values, or
services, place them under that capability rather than adding a flat sibling module to the context root.

Only `wiring.py` may scan registrations across contexts. The public `api` facade and development-time
conformance command are its composition entry points; all other bounded-context code receives dependencies and
never creates or queries a container.

Every injectable belongs in its feature's `services` package, whose `__init__.py` re-exports every decorated
registration beneath it. `wiring.py` discovers only `**.services`; projectors and factories are services for
registration purposes.
