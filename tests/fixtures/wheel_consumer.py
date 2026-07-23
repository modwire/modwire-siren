import modwire_siren
from modwire_siren import SirenContext, siren

schema = {
    "openapi": "3.1.1",
    "info": {"title": "Consumer", "version": "1"},
    "paths": {
        "/widgets": {
            "get": {"operationId": "list_widgets", "responses": {"200": {"description": "OK"}}}
        }
    },
}
context = SirenContext(
    base_url="https://api.example.com",
    scope="collection",
    resource="widget",
    capabilities=frozenset({"list_widgets"}),
)
document = siren(schema).project(context)

assert document["links"] == [{"rel": ["self"], "href": "https://api.example.com/widgets"}]
print(modwire_siren.__file__)
