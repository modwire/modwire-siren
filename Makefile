.PHONY: docs docs-check verify

docs:
	uv run python scripts/generate_docs.py

docs-check:
	uv run python scripts/generate_docs.py --check

verify: docs-check
	uv run ruff check .
	uv run pytest
