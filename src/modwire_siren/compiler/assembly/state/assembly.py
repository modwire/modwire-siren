from dataclasses import dataclass, field

from ....vocabulary import SirenFieldType, SirenHttpMethod, SirenMediaType, SirenScope
from ..values import FieldDraft, OperationDraft, ResourceDraft


@dataclass
class SirenAssembly:
    root_path: str = "/"
    root_title: str = ""
    root_version: str = ""
    resources: list[ResourceDraft] = field(default_factory=list)
    operations: list[OperationDraft] = field(default_factory=list)
    fields: list[FieldDraft] = field(default_factory=list)
    root_operations: list[str] = field(default_factory=list)

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
        self.resources.append(ResourceDraft(reference, name, resource_class, collection_path, entity_path, identifier))
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
        self.operations.append(OperationDraft(resource, scope, name, method, path, media_type))
        return self

    def add_root_operation(self, name: str) -> "SirenAssembly":
        self.root_operations.append(name)
        return self

    def add_field(self, operation: str, name: str, type: SirenFieldType) -> "SirenAssembly":
        self.fields.append(FieldDraft(operation, name, type))
        return self
