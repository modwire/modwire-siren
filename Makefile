.PHONY: docs docs-check modwire package-check quality service-check siren-spec verify

PYTHON ?= python3
RUN = PYTHONPATH=src $(PYTHON)

modwire:
	uv run modwire report --architecture-root . --language python --summary

docs:
	$(RUN) scripts/generate_docs.py

docs-check:
	$(RUN) scripts/generate_docs.py --check

service-check:
	$(RUN) scripts/check_service_conventions.py

siren-spec:
	$(RUN) scripts/siren_spec.py

verify: docs-check service-check siren-spec
	$(RUN) -m ruff check .
	$(RUN) -m pytest

package-check:
	rm -rf dist/quality
	mkdir -p dist/quality
	$(RUN) -m build --wheel --sdist --outdir dist/quality
	$(RUN) -m twine check dist/quality/*

quality: modwire verify package-check
