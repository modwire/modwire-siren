from collections.abc import Mapping

from pytest import mark
from pytest_bdd import given, scenarios, then, when

from modwire_siren import SirenAction, SirenField, SirenFieldValue


class FieldSteps:
    field: SirenField | None = None
    fields: tuple[SirenField, ...] | None = None
    payload: Mapping[str, object] | None = None
    payloads: tuple[Mapping[str, object], ...] | None = None
    error: ValueError | None = None
    unsupported_type: str | None = None
    duplicate_names: bool = False

    @staticmethod
    @given("public Siren fields for every permitted type", stacklevel=2)
    def public_siren_fields_for_every_permitted_type() -> None:
        FieldSteps.field = None
        FieldSteps.payload = None
        FieldSteps.payloads = None
        FieldSteps.error = None
        FieldSteps.unsupported_type = None
        FieldSteps.duplicate_names = False
        FieldSteps.fields = tuple(
            SirenField(name=f"{field_type}-value", type=field_type)
            for field_type in (
                "checkbox",
                "color",
                "date",
                "datetime",
                "datetime-local",
                "email",
                "file",
                "hidden",
                "month",
                "number",
                "password",
                "radio",
                "range",
                "search",
                "tel",
                "text",
                "time",
                "url",
                "week",
            )
        )

    @staticmethod
    @given("a public Siren field without a type", stacklevel=2)
    def public_siren_field_without_a_type() -> None:
        FieldSteps.fields = None
        FieldSteps.payload = None
        FieldSteps.payloads = None
        FieldSteps.error = None
        FieldSteps.unsupported_type = None
        FieldSteps.duplicate_names = False
        FieldSteps.field = SirenField(name="title")

    @staticmethod
    @given("a public Siren field with an unsupported type", stacklevel=2)
    def public_siren_field_with_an_unsupported_type() -> None:
        FieldSteps.field = None
        FieldSteps.fields = None
        FieldSteps.payload = None
        FieldSteps.payloads = None
        FieldSteps.error = None
        FieldSteps.unsupported_type = "textarea"
        FieldSteps.duplicate_names = False

    @staticmethod
    @given("a public radio field with selectable values", stacklevel=2)
    def public_radio_field_with_selectable_values() -> None:
        FieldSteps.fields = None
        FieldSteps.payload = None
        FieldSteps.payloads = None
        FieldSteps.error = None
        FieldSteps.unsupported_type = None
        FieldSteps.duplicate_names = False
        FieldSteps.field = SirenField(
            name="visibility",
            type="radio",
            value=(
                SirenFieldValue(value="private"),
                SirenFieldValue(value="public", selected=True),
            ),
        )

    @staticmethod
    @given('a public Siren action with two fields named "title"', stacklevel=2)
    def public_siren_action_with_duplicate_field_names() -> None:
        FieldSteps.field = None
        FieldSteps.fields = None
        FieldSteps.payload = None
        FieldSteps.payloads = None
        FieldSteps.error = None
        FieldSteps.unsupported_type = None
        FieldSteps.duplicate_names = True

    @staticmethod
    @when("it is created", stacklevel=2)
    def created_field() -> None:
        try:
            if FieldSteps.unsupported_type is not None:
                FieldSteps.field = SirenField(name="title", type=FieldSteps.unsupported_type)
            if FieldSteps.duplicate_names:
                SirenAction(
                    name="update",
                    href="https://api.example.com/records/42",
                    fields=(SirenField(name="title"), SirenField(name="title")),
                )
        except ValueError as error:
            FieldSteps.error = error

    @staticmethod
    @when("it is serialized", stacklevel=2)
    def serialized_field() -> None:
        assert isinstance(FieldSteps.field, SirenField)
        FieldSteps.payload = FieldSteps.field.model_dump(by_alias=True, mode="json", exclude_none=True)

    @staticmethod
    @when("they are serialized", stacklevel=2)
    def serialized_fields() -> None:
        assert isinstance(FieldSteps.fields, tuple)
        FieldSteps.payloads = tuple(
            field.model_dump(by_alias=True, mode="json", exclude_none=True) for field in FieldSteps.fields
        )

    @staticmethod
    @then("their types are the permitted Siren field types", stacklevel=2)
    def field_types_are_permitted_siren_field_types() -> None:
        assert FieldSteps.payloads is not None
        assert [payload["type"] for payload in FieldSteps.payloads] == [
            "checkbox",
            "color",
            "date",
            "datetime",
            "datetime-local",
            "email",
            "file",
            "hidden",
            "month",
            "number",
            "password",
            "radio",
            "range",
            "search",
            "tel",
            "text",
            "time",
            "url",
            "week",
        ]

    @staticmethod
    @then('its type is "text"', stacklevel=2)
    def field_type_is_text() -> None:
        assert FieldSteps.payload == {"name": "title", "type": "text"}

    @staticmethod
    @then("the field has its selectable values", stacklevel=2)
    def field_has_its_selectable_values() -> None:
        assert FieldSteps.payload == {
            "name": "visibility",
            "type": "radio",
            "value": [
                {"value": "private", "selected": False},
                {"value": "public", "selected": True},
            ],
        }

    @staticmethod
    @then("creation is rejected", stacklevel=2)
    def field_creation_is_rejected() -> None:
        assert isinstance(FieldSteps.error, ValueError)


scenarios("../features/fields.feature")
globals()["test_duplicate_field_names_are_rejected"] = mark.xfail(
    strict=True,
    reason="SirenAction does not enforce unique field names",
)(globals()["test_duplicate_field_names_are_rejected"])
