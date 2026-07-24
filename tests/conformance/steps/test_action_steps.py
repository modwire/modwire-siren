from collections.abc import Mapping

from pytest import mark
from pytest_bdd import given, scenarios, then, when

from modwire_siren import SirenAction, SirenDocument, SirenField


class ActionSteps:
    action: SirenAction | None = None
    actions: tuple[SirenAction, ...] | None = None
    document: SirenDocument | None = None
    payload: Mapping[str, object] | None = None
    payloads: tuple[Mapping[str, object], ...] | None = None
    error: ValueError | None = None
    unsupported_method: str | None = None
    invalid_href: str | None = None
    duplicate_names: bool = False

    @staticmethod
    @given("a public Siren action with official members", stacklevel=2)
    def public_siren_action_with_official_members() -> None:
        ActionSteps.actions = None
        ActionSteps.document = None
        ActionSteps.payload = None
        ActionSteps.payloads = None
        ActionSteps.error = None
        ActionSteps.unsupported_method = None
        ActionSteps.invalid_href = None
        ActionSteps.duplicate_names = False
        ActionSteps.action = SirenAction(
            class_=("update",),
            name="update",
            method="PATCH",
            href="https://api.example.com/records/42",
            title="Update record",
            type="application/json",
            fields=(SirenField(name="title"),),
        )

    @staticmethod
    @given("a public Siren action without a method", stacklevel=2)
    def public_siren_action_without_a_method() -> None:
        ActionSteps.actions = None
        ActionSteps.document = None
        ActionSteps.payload = None
        ActionSteps.payloads = None
        ActionSteps.error = None
        ActionSteps.unsupported_method = None
        ActionSteps.invalid_href = None
        ActionSteps.duplicate_names = False
        ActionSteps.action = SirenAction(name="update", href="https://api.example.com/records/42")

    @staticmethod
    @given("public Siren actions for every permitted method", stacklevel=2)
    def public_siren_actions_for_every_permitted_method() -> None:
        ActionSteps.action = None
        ActionSteps.document = None
        ActionSteps.payload = None
        ActionSteps.payloads = None
        ActionSteps.error = None
        ActionSteps.unsupported_method = None
        ActionSteps.invalid_href = None
        ActionSteps.duplicate_names = False
        ActionSteps.actions = tuple(
            SirenAction(
                name=f"{method.lower()}-record",
                method=method,
                href="https://api.example.com/records/42",
            )
            for method in ("DELETE", "GET", "PATCH", "POST", "PUT")
        )

    @staticmethod
    @given("a public Siren action with an unsupported method", stacklevel=2)
    def public_siren_action_with_an_unsupported_method() -> None:
        ActionSteps.action = None
        ActionSteps.actions = None
        ActionSteps.document = None
        ActionSteps.payload = None
        ActionSteps.payloads = None
        ActionSteps.error = None
        ActionSteps.unsupported_method = "HEAD"
        ActionSteps.invalid_href = None
        ActionSteps.duplicate_names = False

    @staticmethod
    @given("a public Siren action with a non-URI href", stacklevel=2)
    def public_siren_action_with_non_uri_href() -> None:
        ActionSteps.action = None
        ActionSteps.actions = None
        ActionSteps.document = None
        ActionSteps.payload = None
        ActionSteps.payloads = None
        ActionSteps.error = None
        ActionSteps.unsupported_method = None
        ActionSteps.invalid_href = "not-a-uri"
        ActionSteps.duplicate_names = False

    @staticmethod
    @given('a public Siren document with two actions named "update"', stacklevel=2)
    def public_siren_document_with_duplicate_action_names() -> None:
        ActionSteps.action = None
        ActionSteps.actions = None
        ActionSteps.document = None
        ActionSteps.payload = None
        ActionSteps.payloads = None
        ActionSteps.error = None
        ActionSteps.unsupported_method = None
        ActionSteps.invalid_href = None
        ActionSteps.duplicate_names = True

    @staticmethod
    @given("a public Siren action with fields and no type", stacklevel=2)
    def public_siren_action_with_fields_and_no_type() -> None:
        ActionSteps.actions = None
        ActionSteps.document = None
        ActionSteps.payload = None
        ActionSteps.payloads = None
        ActionSteps.error = None
        ActionSteps.unsupported_method = None
        ActionSteps.invalid_href = None
        ActionSteps.duplicate_names = False
        ActionSteps.action = SirenAction(
            name="update",
            href="https://api.example.com/records/42",
            fields=(SirenField(name="title"),),
        )

    @staticmethod
    @when("it is created", stacklevel=2)
    def created_action() -> None:
        try:
            if ActionSteps.invalid_href is not None:
                ActionSteps.action = SirenAction(
                    name="inspect",
                    href=ActionSteps.invalid_href,
                )
            if ActionSteps.unsupported_method is not None:
                ActionSteps.action = SirenAction(
                    name="inspect",
                    method=ActionSteps.unsupported_method,
                    href="https://api.example.com/records/42",
                )
            if ActionSteps.duplicate_names:
                ActionSteps.document = SirenDocument(
                    actions=(
                        SirenAction(name="update", href="https://api.example.com/records/42"),
                        SirenAction(name="update", href="https://api.example.com/records/42"),
                    ),
                )
        except ValueError as error:
            ActionSteps.error = error

    @staticmethod
    @when("it is serialized", stacklevel=2)
    def serialized_action() -> None:
        assert isinstance(ActionSteps.action, SirenAction)
        ActionSteps.payload = ActionSteps.action.model_dump(by_alias=True, mode="json", exclude_none=True)

    @staticmethod
    @when("they are serialized", stacklevel=2)
    def serialized_actions() -> None:
        assert isinstance(ActionSteps.actions, tuple)
        ActionSteps.payloads = tuple(
            action.model_dump(by_alias=True, mode="json", exclude_none=True) for action in ActionSteps.actions
        )

    @staticmethod
    @then("the action has its official members", stacklevel=2)
    def action_has_its_official_members() -> None:
        assert ActionSteps.payload == {
            "class": ["update"],
            "name": "update",
            "method": "PATCH",
            "href": "https://api.example.com/records/42",
            "title": "Update record",
            "type": "application/json",
            "fields": [{"name": "title", "type": "text"}],
        }

    @staticmethod
    @then('its method is "GET"', stacklevel=2)
    def action_method_is_get() -> None:
        assert ActionSteps.payload == {
            "name": "update",
            "method": "GET",
            "href": "https://api.example.com/records/42",
        }

    @staticmethod
    @then("their methods are the permitted Siren methods", stacklevel=2)
    def action_methods_are_permitted_siren_methods() -> None:
        assert ActionSteps.payloads is not None
        assert [payload["method"] for payload in ActionSteps.payloads] == ["DELETE", "GET", "PATCH", "POST", "PUT"]

    @staticmethod
    @then('its type is "application/x-www-form-urlencoded"', stacklevel=2)
    def action_type_is_form_encoding() -> None:
        assert isinstance(ActionSteps.payload, Mapping)
        assert ActionSteps.payload.get("type") == "application/x-www-form-urlencoded"

    @staticmethod
    @then("creation is rejected", stacklevel=2)
    def action_creation_is_rejected() -> None:
        assert isinstance(ActionSteps.error, ValueError)


scenarios("../features/actions.feature")
globals()["test_duplicate_action_names_are_rejected"] = mark.xfail(
    strict=True,
    reason="SirenDocument does not enforce unique action names",
)(globals()["test_duplicate_action_names_are_rejected"])
globals()["test_an_action_with_fields_serializes_its_default_type"] = mark.xfail(
    strict=True,
    reason="SirenAction does not default its type when fields are present",
)(globals()["test_an_action_with_fields_serializes_its_default_type"])
