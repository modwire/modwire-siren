# Rules

- Keep the public API to the supported `modwire_siren` root imports; do not make private modules contractual.
- Use OOP: one class per file, no helper or pseudo-private functions. A function is allowed only as public API, such as `siren()`.
- Keep contexts feature-packaged: root modules expose only the minimal context API and composition entry points.
  Collaborating contracts, values, and services belong in a feature subpackage; flat service fields are forbidden.
- `wiring.py` is the sole technical-plumbing exception: it may group the discovery and application-container
  classes so that all cross-context wiring is visible in one place.
- Put every `@injectable` class in its feature's `services` package and re-export it from that package's
  `__init__.py`; `wiring.py` discovers only those packages. Stateless services are singletons, mutable
  operation state is constructed by its coordinator, and request values remain ordinary method arguments.
- Model injectable services as frozen dataclasses, including stateless services with no fields; this gives
  Wireup a declarative constructor without handwritten initialization plumbing.
- Keep `values` packages for immutable records only. `services` contains only injectable services; operation-bound
  state belongs in `state` and its coordinator constructs it for that operation instead of registering it.
- Service collaborations are dataclass fields resolved by Wireup, never method parameters. Operation state receives
  its collaborators in its constructor; methods receive only operation inputs.
- Use one unqualified implementation per interface. Multiple implementations require qualifiers; inject
  `Sequence[Interface]` only for plug-in pipelines, whose coordinator validates the selected behavior.
- Comments are public-API docstrings only. User documentation explains use, not internal inventories.
- Read `.modwire/INDEX.md` and local guidance before changing code.
- Run local commands with the user's effective privileges.
