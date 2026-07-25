import json
from collections.abc import Mapping
from typing import Any

from openapi_spec_validator import validate

from ..compiler.compatibility import SirenCompatibilityReport
from ..compiler.errors import SirenCompilationError
from ..wiring import SirenApplicationContainer


def audit(openapi: Mapping[str, Any]) -> SirenCompatibilityReport:
    """Inspect a valid OpenAPI document against the current official-Siren support boundary.

    Call this during startup before `siren(openapi)` when a consumer needs every currently
    unsupported construct at once. The report exposes typed findings and `render()` for terminal
    or CI output; `siren(openapi)` remains the strict fail-fast compilation entry point.
    """

    try:
        if not isinstance(openapi, Mapping):
            raise TypeError("OpenAPI document must be a mapping")
        document = json.loads(json.dumps(openapi))
        validate(document)
    except Exception as error:
        raise SirenCompilationError("Invalid or unsupported OpenAPI contract") from error
    return SirenApplicationContainer().application().api_service().audit(document)
