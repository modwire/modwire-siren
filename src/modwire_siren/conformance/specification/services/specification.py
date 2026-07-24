from dataclasses import dataclass

from wireup import injectable

from ....siren_schema import SirenSchemaReader
from ..contracts import SirenSpecification
from ..values import SirenRequirement


@injectable(as_type=SirenSpecification)
@dataclass(frozen=True)
class SirenSchemaSpecification(SirenSpecification):
    schemas: SirenSchemaReader

    def requirements(self) -> tuple[SirenRequirement, ...]:
        document = self.schemas.document()
        definitions = (("Entity", document.value), *document.definitions().items())
        requirements: tuple[SirenRequirement, ...] = ()
        for name, definition in definitions:
            effective = document.effective(definition)
            for member, member_schema in effective.get("properties", {}).items():
                requirement = SirenRequirement(
                    name, member, member_schema, member in effective.get("required", ()), document.value
                )
                requirements += (requirement,)
                for value in member_schema.get("enum", []):
                    requirements += (
                        SirenRequirement(name, member, member_schema, requirement.required, document, value),
                    )
        return requirements
