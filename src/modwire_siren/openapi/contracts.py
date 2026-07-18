from typing import Annotated

from pydantic import Field

from ..contracts.base import SirenContract


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
    operations: tuple[str, ...] = ()
