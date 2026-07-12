from modwire_siren.profile import SirenProfile

profile = SirenProfile()
document = profile.enhance(
    {
        "class": ["record"],
        "properties": {"slug": "architecture", "title": "Architecture"},
        "entities": [],
        "actions": [],
        "links": [{"rel": ["self"], "href": "/records/architecture"}],
    },
    {
        "profile": profile.identifier,
        "presentation": {"role": "detail"},
        "properties": {"title": {"importance": "primary"}},
    },
)
