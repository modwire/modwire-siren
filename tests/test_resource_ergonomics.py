import pytest

from modwire_siren import (
    ModwireSirenFactory,
    OpenApiError,
    SirenEntityRequest,
    SirenRelationSpec,
    SirenResourceSpec,
    collect_siren_resources,
    inject_siren_resources,
    siren_resource,
    validate_siren_resources,
)

SCHEMA = {
    "openapi": "3.1.0",
    "paths": {
        "/users/{user_id}": {
            "get": {"operationId": "get_user"},
        },
        "/records/{record_id}": {
            "get": {"operationId": "get_record"},
            "patch": {"operationId": "update_record"},
        },
    },
}


def record_spec() -> SirenResourceSpec:
    return SirenResourceSpec(
        name="record",
        path="/records/{record_id}",
        resource_class="record",
        identifier="id",
        path_parameters={"record_id": "id"},
        relations={"owner_id": SirenRelationSpec(rel="owner", resource="user", many=False)},
    )


def user_spec() -> SirenResourceSpec:
    return SirenResourceSpec(
        name="user",
        path="/users/{user_id}",
        resource_class="user",
        identifier="id",
        path_parameters={"user_id": "id"},
        relations={},
    )


def test_inject_siren_resources_returns_schema_copy_with_typed_extensions():
    schema = inject_siren_resources(SCHEMA, (user_spec(), record_spec()))

    assert SCHEMA["paths"]["/records/{record_id}"].get("x-siren-resource") is None
    assert schema["paths"]["/records/{record_id}"]["x-siren-resource"] == {
        "name": "record",
        "class": "record",
        "identifier": "id",
        "path-parameters": {"record_id": "id"},
        "relations": {"owner_id": {"rel": "owner", "resource": "user", "many": False}},
    }


def test_validate_siren_resources_reuses_catalog_validation_and_required_resource_lookup():
    schema = inject_siren_resources(SCHEMA, (user_spec(), record_spec()))

    validate_siren_resources(schema, ("record", "user"))

    document = ModwireSirenFactory.standard(schema, "https://api.test").document(
        SirenEntityRequest(
            resource_name="record",
            properties={"id": "rec-1", "owner_id": "user-1"},
            operation_ids=("update_record",),
            path_values={},
            entities=(),
        )
    )
    assert document["links"][0]["href"] == "https://api.test/records/rec-1"
    assert document["links"][1]["href"] == "https://api.test/users/user-1"


def test_validate_siren_resources_rejects_missing_required_resource():
    with pytest.raises(OpenApiError, match="Unknown Siren resource"):
        validate_siren_resources(SCHEMA, ("record",))


def test_inject_siren_resources_rejects_missing_openapi_path():
    spec = SirenResourceSpec(
        name="record",
        path="/missing/{record_id}",
        resource_class="record",
        identifier="id",
        path_parameters={"record_id": "id"},
        relations={},
    )

    with pytest.raises(ValueError, match="not present"):
        inject_siren_resources(SCHEMA, (spec,))


def test_inject_siren_resources_rejects_framework_converter_path_syntax():
    spec = SirenResourceSpec(
        name="record",
        path="/records/{path:record_id}",
        resource_class="record",
        identifier="id",
        path_parameters={"record_id": "id"},
        relations={},
    )

    with pytest.raises(ValueError, match="OpenAPI template syntax"):
        inject_siren_resources(SCHEMA, (spec,))


def test_inject_siren_resources_rejects_invalid_relation_targets():
    with pytest.raises(OpenApiError, match="unknown resources"):
        inject_siren_resources(SCHEMA, (record_spec(),))


def test_siren_resource_decorator_collects_controller_specs_and_accepts_relation_dicts():
    @siren_resource(
        name="record",
        path="/records/{record_id}",
        class_="record",
        identifier="id",
        path_parameters={"record_id": "id"},
        relations={"owner_id": {"rel": "owner", "resource": "user", "many": False}},
    )
    class RecordController:
        pass

    resources = collect_siren_resources(RecordController)

    assert resources == (record_spec(),)


def test_siren_resource_decorator_rejects_non_boolean_many():
    with pytest.raises(ValueError, match="boolean"):
        siren_resource(
            name="record",
            path="/records/{record_id}",
            class_="record",
            identifier="id",
            path_parameters={"record_id": "id"},
            relations={"owner_id": {"rel": "owner", "resource": "user", "many": "false"}},
        )
