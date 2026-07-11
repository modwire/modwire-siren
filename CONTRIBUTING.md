# Contributing

Keep contracts frozen, strict, explicit, and non-nullable. Constructors receive complete
dependencies, polymorphic collaborators use abstract base classes, OpenAPI remains the source of
truth for operations and routes, and feature packages are not export barrels.

Generated README regions project root `__all__`, public docstrings, and the executable example. Edit
those sources and run `make docs`; never hand-edit generated regions.

```bash
uv sync --all-groups --frozen
make verify
```
