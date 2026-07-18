from typing import Any

from .path_template_validator import OpenApiPathTemplateValidator
from .resource_injector import SirenResourceInjector
from .resource_spec import SirenResourceSpec
from .resource_spec_serializer import SirenResourceSpecSerializer
from .resource_validator import SirenResourceValidator


def inject_siren_resources(schema: dict[str, Any], resources: tuple[SirenResourceSpec, ...]) -> dict[str, Any]:
    """Attach typed Siren resource declarations to an OpenAPI schema copy."""
    return SirenResourceInjector(
        SirenResourceSpecSerializer(),
        OpenApiPathTemplateValidator(),
        SirenResourceValidator(),
    ).inject(schema, resources)


def validate_siren_resources(schema: dict[str, Any], resource_names: tuple[str, ...] = ()) -> None:
    """Validate Siren resource metadata with the standard OpenAPI catalog."""
    SirenResourceValidator().validate(schema, resource_names)
