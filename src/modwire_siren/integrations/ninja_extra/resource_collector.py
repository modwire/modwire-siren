from typing import Any

from ...openapi.resource_spec import SirenResourceSpec


class SirenResourceCollector:
    def collect(self, controllers: tuple[Any, ...]) -> tuple[SirenResourceSpec, ...]:
        return tuple(
            resource
            for controller in controllers
            for resource in getattr(controller, "siren_resource_specs", ())
        )


def collect_siren_resources(*controllers: Any) -> tuple[SirenResourceSpec, ...]:
    """Collect Siren resource declarations attached to controller classes."""
    return SirenResourceCollector().collect(controllers)
