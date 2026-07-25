from copy import deepcopy

import pytest
from openapi_documents import PARAMETER_MEDIA_SCHEMA

from modwire_siren import ModwireSirenError, audit, siren


class TestCompatibility:
    def test_public_facade_reports_all_independent_compatibility_findings_in_deterministic_order(self):
        document = deepcopy(PARAMETER_MEDIA_SCHEMA)
        document["paths"]["/records"]["get"]["parameters"] = [
            {"name": "session", "in": "header", "required": False, "schema": {"type": "string"}},
            {"name": "query", "in": "query", "required": True, "schema": {"type": "string"}},
            {
                "name": "tags",
                "in": "query",
                "required": False,
                "schema": {"type": "array", "items": {"type": "string"}},
            },
        ]
        document["paths"]["/records/{record_id}"]["patch"]["requestBody"]["content"] = {
            "application/json": {
                "schema": {
                    "type": "object",
                    "required": ["title"],
                    "properties": {"title": {"type": "string"}},
                }
            }
        }
        document["paths"]["/records"]["head"] = {
            "operationId": "head_records",
            "responses": {"200": {"description": "OK"}},
        }

        report = audit(document)

        assert report.compatible is False
        assert [(finding.category, finding.location) for finding in report.findings] == [
            ("parameter-location", "#/paths/~1records/get/parameters/0"),
            ("http-method", "#/paths/~1records/head"),
        ]
        assert report.render() == (
            "OpenAPI-to-Siren compatibility findings:\n"
            "- #/paths/~1records/get/parameters/0 [parameter-location]: OpenAPI parameter location is unsupported: "
            "header. Remediation: Use a path parameter or an optional query parameter.\n"
            "- #/paths/~1records/head [http-method]: OpenAPI operation method is unsupported: HEAD /records. "
            "Remediation: Use an official Siren action method: GET, POST, PUT, PATCH, or DELETE."
        )

    def test_public_facade_reports_a_compatible_contract_without_changing_fail_fast_compilation(self):
        report = audit(PARAMETER_MEDIA_SCHEMA)

        assert report.compatible is True
        assert report.findings == ()
        assert report.render() == "OpenAPI-to-Siren compatibility: compatible"

        incompatible = deepcopy(PARAMETER_MEDIA_SCHEMA)
        incompatible["paths"]["/records"]["get"]["parameters"] = [
            {"name": "page", "in": "query", "schema": {"type": "object"}}
        ]

        with pytest.raises(ModwireSirenError, match="Invalid or unsupported OpenAPI contract"):
            siren(incompatible)
