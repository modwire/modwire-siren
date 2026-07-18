# Python profile API

`modwire_siren.profile` is the single supported import location for the Python profile API.
Everything below that package is private implementation.

<!-- generated:public-api:start -->
## Public API

The supported root imports below are generated from `modwire_siren.profile.__all__`.

| Symbol | Purpose | Primary API |
| --- | --- | --- |
| `SirenProfile` | Validate, discover, and apply the Modwire Siren UI Profile. | `identifier: str`<br>`schema_id: str`<br>`media_type: str`<br>`validate(metadata: Mapping[str, typing.Any]) -> dict[str, typing.Any]`<br>`discover(document: Mapping[str, typing.Any]) -> dict[str, typing.Any]`<br>`enhance(document: Mapping[str, typing.Any], metadata: Mapping[str, typing.Any]) -> dict[str, typing.Any]` |

## Executable example

Source: [`profile.py`](../../examples/profile.py). This file is executed by the test suite.

```python
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
```
<!-- generated:public-api:end -->
