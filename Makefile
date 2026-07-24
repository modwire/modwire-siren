.PHONY: docs docs-check modwire verify

modwire:
	modwire report --architecture-root src --language python --summary

docs:
	uv run python scripts/generate_docs.py

docs-check:
	uv run python scripts/generate_docs.py --check

verify: docs-check
	uv run ruff check .
	uv run pytest
