# Architecture

`api`, `contexts/compiler`, `contexts/runtime`, `contexts/conformance`, and `contexts/ledger` respectively compose the
public callable, compile OpenAPI, project Siren documents, provide conformance inputs, and assess conformance.
`shared/siren_schema` is dependency-free shared infrastructure for the pinned schema, provenance, and immutable reader.
Root `__init__.py` exports only.

Contexts are feature packages: roots expose only public types and composition entry points; a capability's
contracts, values, and services stay beneath that capability. `.modwire/architecture.yaml` is the authority for
allowed dependencies; `make modwire` enforces it for source, tests, and scripts.

`wiring.py` alone scans registrations across contexts and builds containers. It discovers only `**.services`;
each feature service package re-exports its decorated injectables. The API facade and conformance command are the
composition entry points; other code receives dependencies rather than creating or querying containers.
