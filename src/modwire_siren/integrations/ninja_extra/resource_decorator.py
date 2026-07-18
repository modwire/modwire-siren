from collections.abc import Mapping
from typing import Any, TypeVar

from ...openapi.relation_spec import SirenRelationSpec
from ...openapi.resource_spec import SirenResourceSpec
from .relation_input_factory import SirenRelationInputFactory

T = TypeVar("T")


class SirenResourceDecorator:
    def __init__(
        self,
        *,
        name: str,
        path: str,
        resource_class: str,
        identifier: str,
        path_parameters: Mapping[str, str],
        relations: Mapping[str, SirenRelationSpec | Mapping[str, Any]],
    ):
        relation_inputs = SirenRelationInputFactory()
        self._spec = SirenResourceSpec(
            name=name,
            path=path,
            resource_class=resource_class,
            identifier=identifier,
            path_parameters=dict(path_parameters),
            relations={field: relation_inputs.create(relation) for field, relation in relations.items()},
        )

    def __call__(self, controller: T) -> T:
        existing = getattr(controller, "siren_resource_specs", ())
        controller.siren_resource_specs = (*existing, self._spec)
        return controller


def siren_resource(
    *,
    name: str,
    path: str,
    class_: str,
    identifier: str,
    path_parameters: Mapping[str, str],
    relations: Mapping[str, SirenRelationSpec | Mapping[str, Any]],
) -> SirenResourceDecorator:
    """Attach a typed Siren resource declaration to a Ninja Extra controller class."""
    return SirenResourceDecorator(
        name=name,
        path=path,
        resource_class=class_,
        identifier=identifier,
        path_parameters=path_parameters,
        relations=relations,
    )
