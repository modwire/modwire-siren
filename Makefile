.PHONY: docs docs-check modwire service-check siren-spec verify

PYTHON ?= uv run python

modwire:
	modwire report --architecture-root . --language python --summary

docs:
	uv run python scripts/generate_docs.py

docs-check:
	uv run python scripts/generate_docs.py --check

service-check:
	uv run python scripts/check_service_conventions.py

siren-spec:
	$(PYTHON) scripts/siren_spec.py

verify: docs-check service-check siren-spec
	uv run ruff check .
	uv run pytest
