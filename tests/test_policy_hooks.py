from dataclasses import dataclass

import pytest

from modwire_siren import (
    ModwireSirenFactory,
    NinjaExtraSirenController,
    OpenApiError,
    RelatedLinkInput,
    SirenEntityRequest,
    siren_collection,
    siren_entity,
)

SCHEMA = {
    "openapi": "3.1.0",
    "paths": {
        "/users/{user_id}": {
            "x-siren-resource": {
                "name": "user",
                "class": "user",
                "identifier": "id",
                "path-parameters": {"user_id": "id"},
                "relations": {},
            },
            "get": {"operationId": "get_user"},
        },
        "/tags/{tag_id}": {
            "x-siren-resource": {
                "name": "tag",
                "class": "tag",
                "identifier": "id",
                "path-parameters": {"tag_id": "id"},
                "relations": {},
            },
            "get": {"operationId": "get_tag"},
        },
        "/records": {
            "get": {"operationId": "list_records"},
            "post": {"operationId": "create_record"},
        },
        "/records/{record_id}": {
            "x-siren-resource": {
                "name": "record",
                "class": "record",
                "identifier": "id",
                "path-parameters": {"record_id": "id"},
                "relations": {},
                "operations": ("preview_record", "get_record_schema"),
            },
            "get": {"operationId": "get_record"},
            "patch": {"operationId": "update_record"},
        },
        "/records/{record_id}/preview": {
            "post": {"operationId": "preview_record"},
        },
        "/records/{record_id}/schema": {
            "get": {"operationId": "get_record_schema"},
        },
    },
}


@dataclass(frozen=True, slots=True)
class Request:
    can_edit: bool
    can_create: bool


class RecordPolicy:
    def operations_for_entity(self, request: Request, resource_name: str, properties: dict) -> tuple[str, ...]:
        operations = ["get_record", "get_record_schema"]
        if request.can_edit:
            operations.extend(("update_record", "preview_record"))
        return tuple(operations)

    def operations_for_collection(self, request: Request, resource_name: str) -> tuple[str, ...]:
        if request.can_create:
            return ("list_records", "create_record")
        return ("list_records",)

    def related_links_for_entity(
        self, request: Request, resource_name: str, properties: dict
    ) -> tuple[RelatedLinkInput, ...]:
        return (
            RelatedLinkInput(rel="owner", resource="user", value=properties["owner_id"]),
            RelatedLinkInput(rel="tag", resource="tag", value=properties["tag_ids"]),
        )


class RecordController(NinjaExtraSirenController):
    @siren_entity(resource="record", policy=RecordPolicy())
    def get_record(self, request: Request, record_id: str) -> dict:
        return {"id": record_id, "owner_id": "user-1", "tag_ids": ("tag-1", "tag-2")}

    @siren_entity(
        resource="record",
        operations=lambda request, properties: ("get_record",) if request.can_edit else (),
        related_links=lambda request, properties: (RelatedLinkInput(rel="owner", resource="user", value="user-1"),),
    )
    def get_record_functional(self, request: Request, record_id: str) -> dict:
        return {"id": record_id}

    @siren_collection(resource="record", policy=RecordPolicy(), item_operations=("get_record",))
    def list_records(self, request: Request) -> tuple[dict, ...]:
        return ({"id": "rec-1"},)


def siren():
    return ModwireSirenFactory.standard(SCHEMA, "https://api.test")


def controller() -> RecordController:
    return RecordController(siren())


def test_owned_sub_actions_are_projected_when_resource_declares_them():
    document = siren().document(
        SirenEntityRequest(
            resource_name="record",
            properties={"id": "rec-1"},
            operation_ids=("preview_record", "get_record_schema"),
            path_values={},
            entities=(),
        )
    )

    assert [action["name"] for action in document["actions"]] == ["preview_record", "get_record_schema"]
    assert document["actions"][0]["href"] == "https://api.test/records/rec-1/preview"
    assert document["actions"][1]["href"] == "https://api.test/records/rec-1/schema"


def test_foreign_operation_still_fails_when_resource_does_not_own_it():
    with pytest.raises(OpenApiError, match="do not belong"):
        siren().document(
            SirenEntityRequest(
                resource_name="record",
                properties={"id": "rec-1"},
                operation_ids=("get_user",),
                path_values={},
                entities=(),
            )
        )


def test_entity_policy_selects_operations_and_related_links_from_request():
    response = controller().get_record(Request(can_edit=True, can_create=False), "architecture/aggregate")

    assert [action["name"] for action in response.body["actions"]] == [
        "get_record",
        "get_record_schema",
        "update_record",
        "preview_record",
    ]
    assert response.body["links"][0]["href"] == "https://api.test/records/architecture%2Faggregate"
    assert [link["rel"] for link in response.body["links"][1:]] == [["owner"], ["tag"], ["tag"]]
    assert response.body["links"][1]["href"] == "https://api.test/users/user-1"
    assert response.body["links"][2]["href"] == "https://api.test/tags/tag-1"
    assert response.body["links"][3]["href"] == "https://api.test/tags/tag-2"


def test_functional_policy_selectors_are_supported():
    response = controller().get_record_functional(Request(can_edit=True, can_create=False), "rec-1")

    assert [action["name"] for action in response.body["actions"]] == ["get_record"]
    assert response.body["links"][1]["href"] == "https://api.test/users/user-1"


def test_collection_policy_selects_collection_operations_from_request():
    response = controller().list_records(Request(can_edit=False, can_create=True))

    assert [action["name"] for action in response.body["actions"]] == ["list_records", "create_record"]
    assert response.body["entities"][0]["rel"] == ["item"]
    assert [action["name"] for action in response.body["entities"][0]["actions"]] == ["get_record"]


def test_policy_hook_names_must_be_callable():
    class InvalidPolicy:
        operations_for_entity = ("get_record",)

    class InvalidController(NinjaExtraSirenController):
        @siren_entity(resource="record", policy=InvalidPolicy())
        def get_record(self, request: Request, record_id: str) -> dict:
            return {"id": record_id}

    with pytest.raises(ValueError, match="must be callable"):
        InvalidController(siren()).get_record(Request(can_edit=False, can_create=False), "rec-1")
