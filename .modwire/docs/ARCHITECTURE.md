# Architecture

`api`, `contexts/compiler`, `contexts/graph`, `contexts/runtime`, and `contexts/conformance` respectively compose
the public callable, compile OpenAPI, own the immutable compiled Siren graph, project Siren documents, and assess
conformance. Conformance owns its specification, implementation, and ledger modules. `shared` is a dependency-free
context whose foundation, vocabulary, and Siren-schema modules supply common state, values, and the pinned schema
with its provenance. Root `__init__.py` files export only.

Runtime's adapter feature owns the optional HTTP boundary: it resolves compiled operation routes, accepts only
already-executed results, and produces framework-neutral Siren responses. Framework bridges receive an explicit
application capability policy and remain dependency-optional; they never redispatch operations or infer policy.

Contexts are feature packages: roots expose only public types and composition entry points; a capability's
contracts, values, and services stay beneath that capability. `.modwire/architecture.yaml` is the authority for
allowed dependencies; `make modwire` enforces it for source, tests, and scripts.

`wiring.py` alone scans registrations across contexts and builds containers. It discovers only `**.services`;
each feature service package re-exports its decorated injectables. The API facade and conformance command are the
composition entry points; other code receives dependencies rather than creating or querying containers.
