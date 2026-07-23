import json
from collections.abc import Mapping
from typing import Any

from openapi_spec_validator import validate

from .engine import SirenEngine
from .service import SirenApiService
from .sources import OpenApiSource


def siren(openapi: Mapping[str, Any], *, root_path: str = "/") -> SirenEngine:
    """Compile an OpenAPI document into a reusable Siren engine."""
    if not isinstance(openapi, Mapping):
        raise TypeError("OpenAPI document must be a mapping")
    if not isinstance(root_path, str) or not root_path.startswith("/"):
        raise ValueError("Siren root path must start with '/'")
    try:
        document = json.loads(json.dumps(openapi))
        validate(document)
    except RecursionError as error:
        raise ValueError("OpenAPI document is invalid: cyclic reference") from error
    except Exception as error:
        raise ValueError(f"OpenAPI document is invalid: {error}") from error
    api = SirenApiService((OpenApiSource(root_path=root_path),)).build(document)
    return SirenEngine(api)
