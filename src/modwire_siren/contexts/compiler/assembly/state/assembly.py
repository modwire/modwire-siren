from pydantic import Field

from modwire_siren.shared import BaseState, SirenFieldType, SirenHttpMethod, SirenMediaType, SirenScope

from ..values import FieldDraft, OperationDraft, ResourceDraft


class SirenAssembly(BaseState):
    root_path: str = "/"
    root_title: str = ""
    root_version: str = ""
    resources: list[ResourceDraft] = Field(default_factory=list)
    operations: list[OperationDraft] = Field(default_factory=list)
    fields: list[FieldDraft] = Field(default_factory=list)
    root_operations: list[str] = Field(default_factory=list)

    def set_root(self, path: str = "/", title: str = "", version: str = "") -> "SirenAssembly":
        self.root_path = path
        self.root_title = title
        self.root_version = version
        return self

    def add_resource(
        self,
        reference: str,
        name: str,
        resource_class: str,
        collection_path: str,
        entity_path: str | None = None,
        identifier: str = "id",
    ) -> "SirenAssembly":
        self.resources.append(ResourceDraft(
            reference=reference,
            name=name,
            resource_class=resource_class,
            collection_path=collection_path,
            entity_path=entity_path,
            identifier=identifier,
        ))
        return self

    def add_operation(
        self,
        resource: str | None,
        scope: SirenScope,
        name: str,
        method: SirenHttpMethod,
        path: str,
        media_type: SirenMediaType | None = None,
    ) -> "SirenAssembly":
        self.operations.append(OperationDraft(
            resource=resource,
            scope=scope,
            name=name,
            method=method,
            path=path,
            media_type=media_type,
        ))
        return self

    def add_root_operation(self, name: str) -> "SirenAssembly":
        self.root_operations.append(name)
        return self

    def add_field(self, operation: str, name: str, type: SirenFieldType) -> "SirenAssembly":
        self.fields.append(FieldDraft(operation=operation, name=name, type=type))
        return self
