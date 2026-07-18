from typing import Annotated, Any

from pydantic import BeforeValidator, Field

from ..contracts.base import SirenContract


def _string_tuple(value: Any) -> Any:
    if isinstance(value, list | tuple):
        return tuple(value)
    return value


StringTuple = Annotated[tuple[str, ...], BeforeValidator(_string_tuple)]


class OpenApiRelationExtension(SirenContract):
    rel: str
    resource: str
    many: bool


class OpenApiResourceExtension(SirenContract):
    name: str
    resource_class: Annotated[str, Field(validation_alias="class")]
    identifier: str
    path_parameters: Annotated[dict[str, str], Field(validation_alias="path-parameters")]
    relations: dict[str, OpenApiRelationExtension]
    operations: StringTuple = ()
    collection_operations: Annotated[StringTuple, Field(validation_alias="collection-operations")] = ()
    collection_only: Annotated[bool, Field(validation_alias="collection-only")] = False
    singleton: bool = False
    root_visible: Annotated[bool | None, Field(validation_alias="root-visible")] = None
