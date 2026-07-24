.PHONY: docs docs-check modwire service-check siren-spec verify

modwire:
	modwire report --architecture-root . --language python --summary

docs:
	uv run python scripts/generate_docs.py

docs-check:
	uv run python scripts/generate_docs.py --check

service-check:
	uv run python scripts/check_service_conventions.py

siren-spec:
	uv run python scripts/siren_spec.py

verify: docs-check service-check
	uv run ruff check .
	uv run pytest
