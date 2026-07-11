from modwire_siren.contracts.action import SirenAction, SirenField
from modwire_siren.contracts.entity import SirenEntity
from modwire_siren.contracts.link import SirenLink
from modwire_siren.serialization import PydanticSirenSerializer


def test_entity_contract_is_the_wire_format_source_of_truth():
    entity = SirenEntity(
        classes=("record",),
        properties={"slug": "architecture/aggregate"},
        links=(
            SirenLink(
                rel=("self",),
                href="https://api.test/records/architecture/aggregate",
                title="record",
                media_type="application/vnd.siren+json",
            ),
        ),
        actions=(
            SirenAction(
                name="close",
                href="https://api.test/records/architecture/aggregate",
                method="DELETE",
                title="Close record",
                media_type="application/json",
                fields=(
                    SirenField(
                        name="force",
                        type="checkbox",
                        required=False,
                        title="Force",
                        options=(),
                        schema={},
                    ),
                ),
            ),
        ),
        entities=(),
    )

    assert PydanticSirenSerializer().serialize(entity) == {
        "class": ["record"],
        "properties": {"slug": "architecture/aggregate"},
        "entities": [],
        "actions": [
            {
                "name": "close",
                "href": "https://api.test/records/architecture/aggregate",
                "method": "DELETE",
                "title": "Close record",
                "type": "application/json",
                "fields": [
                    {
                        "name": "force",
                        "type": "checkbox",
                        "required": False,
                        "title": "Force",
                        "options": [],
                        "schema": {},
                    }
                ],
            }
        ],
        "links": [
            {
                "rel": ["self"],
                "href": "https://api.test/records/architecture/aggregate",
                "title": "record",
                "type": "application/vnd.siren+json",
            }
        ],
    }
