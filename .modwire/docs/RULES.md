# Rules

- The supported public API is `modwire_siren` root imports; private modules are never contractual.
- Use OOP: one class per file and no helper or pseudo-private functions. Public functions such as `siren()` are allowed.
- Keep contexts feature-packaged: roots expose only their minimal public/composition API, and no flat service fields.
  `wiring.py` is the sole plumbing exception and keeps all cross-context discovery and application-container classes
  visible together.
- Every injectable is a frozen dataclass in its feature's `services` package and is re-exported there. Stateless
  services are singletons; projectors and factories are services; request values remain method inputs.
- `values` holds immutable records, `services` only injectables, and `state` operation-bound state constructed by
  its coordinator. Collaborators are Wireup-resolved dataclass fields, never method parameters; runtime and compiler
  declare neither constructors nor `TYPE_CHECKING` imports.
- Use one unqualified implementation per interface. Qualify alternatives; use `Sequence[Interface]` only for a
  validated plug-in pipeline.
- Comments are public-API docstrings; user docs explain use, not internal inventories.
- BDD adapters live only in `tests/conformance/steps`, use only root imports, contain no application logic, and never
  create or query a container.
- Read `.modwire/INDEX.md` and local guidance before changes; run commands with the user's effective privileges.
