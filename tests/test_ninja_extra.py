import asyncio
import inspect

import pytest

from modwire_siren import ModwireSirenFactory, NinjaExtraSirenController, SirenEntityDecorator

SCHEMA = {
    "paths": {
        "/records/{record_slug}": {
            "x-siren-resource": {
                "name": "record",
                "class": "record",
                "identifier": "slug",
                "path-parameters": {"record_slug": "slug"},
                "relations": {},
            },
            "get": {"operationId": "get_record"},
            "patch": {"operationId": "revise_record"},
        }
    }
}


class RecordController(NinjaExtraSirenController):
    @SirenEntityDecorator("record", operations=("revise_record",))
    def get_record(self, record_slug: str) -> dict:
        return {"slug": record_slug, "title": "Architecture"}

    @SirenEntityDecorator("record", operations=())
    async def get_record_async(self, record_slug: str) -> dict:
        return {"slug": record_slug}


def controller() -> RecordController:
    return RecordController(ModwireSirenFactory.standard(SCHEMA, "https://api.test"))


def test_siren_entity_keeps_controller_thin_and_preserves_route_signature():
    assert str(inspect.signature(RecordController.get_record)) == "(self, record_slug: str) -> dict"

    document = controller().get_record("architecture/aggregate")

    assert document["properties"] == {"slug": "architecture/aggregate", "title": "Architecture"}
    assert document["links"][0]["href"] == "https://api.test/records/architecture%2Faggregate"
    assert [action["name"] for action in document["actions"]] == ["revise_record"]


def test_siren_entity_supports_async_controller_methods():
    document = asyncio.run(controller().get_record_async("architecture"))
    assert document["class"] == ["record"]


def test_siren_entity_rejects_blank_resource_names_at_declaration_time():
    with pytest.raises(ValueError, match="must not be blank"):
        SirenEntityDecorator(" ", operations=())
