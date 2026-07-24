from collections.abc import Mapping

from pytest_bdd import given, scenarios, then, when

from modwire_siren import SirenLink


class LinkSteps:
    link: SirenLink | None = None
    payload: Mapping[str, object] | None = None
    error: ValueError | None = None
    invalid_href: str | None = None
    invalid_media_type: str | None = None

    @staticmethod
    @given('a public link with rel "self" and an href', stacklevel=2)
    def public_link_with_relation_and_href() -> None:
        LinkSteps.payload = None
        LinkSteps.error = None
        LinkSteps.invalid_href = None
        LinkSteps.invalid_media_type = None
        LinkSteps.link = SirenLink(rel=("self",), href="https://api.example.com/records/42", type="application/json")

    @staticmethod
    @given("a public link without rel", stacklevel=2)
    def public_link_without_relation() -> None:
        LinkSteps.link = None
        LinkSteps.payload = None
        LinkSteps.error = None
        LinkSteps.invalid_href = None
        LinkSteps.invalid_media_type = None

    @staticmethod
    @given("a public link with a non-URI href", stacklevel=2)
    def public_link_with_non_uri_href() -> None:
        LinkSteps.link = None
        LinkSteps.payload = None
        LinkSteps.error = None
        LinkSteps.invalid_href = "not-a-uri"
        LinkSteps.invalid_media_type = None

    @staticmethod
    @given("a public link with an invalid media type", stacklevel=2)
    def public_link_with_an_invalid_media_type() -> None:
        LinkSteps.link = None
        LinkSteps.payload = None
        LinkSteps.error = None
        LinkSteps.invalid_href = None
        LinkSteps.invalid_media_type = "not a media type"

    @staticmethod
    @when("it is created", stacklevel=2)
    def created_link() -> None:
        try:
            if LinkSteps.link is None:
                LinkSteps.link = SirenLink(
                    rel=("self",) if LinkSteps.invalid_href or LinkSteps.invalid_media_type else None,
                    href=LinkSteps.invalid_href or "https://api.example.com/records/42",
                    type=LinkSteps.invalid_media_type,
                )
        except ValueError as error:
            LinkSteps.error = error

    @staticmethod
    @when("it is serialized", stacklevel=2)
    def serialized_link() -> None:
        assert isinstance(LinkSteps.link, SirenLink)
        LinkSteps.payload = LinkSteps.link.model_dump(by_alias=True, mode="json", exclude_none=True)

    @staticmethod
    @then('the link has rel "self" and its href', stacklevel=2)
    def link_has_relation_and_href() -> None:
        assert LinkSteps.payload == {
            "rel": ["self"],
            "href": "https://api.example.com/records/42",
            "type": "application/json",
        }

    @staticmethod
    @then("creation is rejected", stacklevel=2)
    def link_creation_is_rejected() -> None:
        assert isinstance(LinkSteps.error, ValueError)

scenarios("../features/links.feature")
