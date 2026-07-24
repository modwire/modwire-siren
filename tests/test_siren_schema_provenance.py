import hashlib
import json
from importlib.resources import files

import modwire_siren


class TestSirenSchemaProvenance:
    def test_vendored_schema_matches_the_pinned_source_and_digest(self):
        schema = files(modwire_siren).joinpath("runtime/document/schema/siren.schema.json")
        provenance = files(modwire_siren).joinpath("runtime/document/schema/siren.schema.provenance.json")

        assert json.loads(provenance.read_text()) == {
            "source_url": "https://github.com/kevinswiber/siren/blob/c29a87840407419d52c2acd742a1ad6a03ce80da/siren.schema.json",
            "source_revision": "c29a87840407419d52c2acd742a1ad6a03ce80da",
            "source_blob": "805711bc43d82a62e13f056bfa00791fe7b3b0fc",
            "vendored_sha256": "589aee71cca493ca398bb6246e0fb5dcab502c1f7fd2d2ae4ac6f776a51e564f",
        }
        assert hashlib.sha256(schema.read_bytes()).hexdigest() == json.loads(provenance.read_text())["vendored_sha256"]
