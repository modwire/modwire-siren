import json
import subprocess
import sys
from typing import ClassVar

import pytest
from django.conf import settings
from django.http import JsonResponse
from django.test import RequestFactory, override_settings
from framework_fixtures.capability_policy import CapabilityPolicy

from modwire_siren import (
    ModwireSirenError,
    SirenAdapterPolicy,
    SirenAdapterRequest,
    SirenDjangoMiddleware,
    siren_adapter,
)


class TestAdapter:
    schema: ClassVar[dict[str, object]] = {
        "openapi": "3.1.1",
        "info": {"title": "Adapter API", "version": "4.0.0"},
        "paths": {
            "/api/articles": {
                "get": {
                    "operationId": "list_articles",
                    "responses": {
                        "200": {
                            "description": "Articles",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Article"},
                                    }
                                }
                            },
                        },
                        "default": {
                            "description": "List failure",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Problem"}
                                }
                            },
                        },
                    },
                }
            },
            "/api/articles/{article_key}": {
                "parameters": [
                    {
                        "name": "article_key",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "get": {
                    "operationId": "get_article",
                    "summary": "Read article",
                    "responses": {
                        "200": {
                            "description": "Article",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Article"}
                                }
                            },
                        },
                    },
                },
                "delete": {
                    "operationId": "delete_article",
                    "responses": {
                        "204": {"description": "Deleted"},
                        "404": {
                            "description": "Missing",
                            "content": {
                                "application/problem+json": {
                                    "schema": {"$ref": "#/components/schemas/Problem"}
                                }
                            },
                        },
                    },
                },
            },
            "/api/articles/{article_key}/publish": {
                "parameters": [
                    {
                        "name": "article_key",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "post": {
                    "operationId": "publish_article",
                    "responses": {
                        "202": {
                            "description": "Published",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"published": {"type": "boolean"}}}
                                }
                            },
                        },
                        "4XX": {
                            "description": "Publish failure",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Problem"}
                                }
                            },
                        },
                    },
                },
            },
        },
        "components": {
            "schemas": {
                "Article": {
                    "type": "object",
                    "properties": {
                        "article_key": {"type": "string"},
                        "title": {"type": "string"},
                    },
                },
                "Problem": {
                    "type": "object",
                    "properties": {"detail": {"type": "string"}},
                },
            }
        },
    }

    def test_framework_neutral_boundary_resolves_mounts_and_projects_every_outcome(self):
        adapter = siren_adapter(self.schema, source_path="/api", public_path="/siren")

        source = adapter.match("GET", "/api/articles/a%2Fb")
        public = adapter.match("GET", "/siren/articles/a%2Fb")
        assert source == public
        assert source.operation_id == "get_article"
        assert source.path_values == {"article_key": "a/b"}

        collection = adapter.respond(SirenAdapterRequest(
            method="GET",
            path="/api/articles",
            status=200,
            result=[{"article_key": "one", "title": "One"}],
            base_url="https://example.test",
        ))
        entity = adapter.respond(SirenAdapterRequest(
            operation_id="get_article",
            status=200,
            result={"article_key": "one", "title": "One"},
            base_url="https://example.test",
            headers={"ETag": "one", "Content-Type": "application/json", "Content-Length": "2"},
            policy=SirenAdapterPolicy(capabilities=frozenset({"get_article"})),
        ))
        command = adapter.respond(SirenAdapterRequest(
            method="POST",
            path="/api/articles/one/publish",
            status=202,
            result={"published": True},
            base_url="https://example.test",
            policy=SirenAdapterPolicy(representation="command"),
        ))
        empty = adapter.respond(SirenAdapterRequest(
            method="DELETE",
            path="/api/articles/one",
            status=204,
            base_url="https://example.test",
        ))
        validation = adapter.respond(SirenAdapterRequest(
            method="GET",
            path="/api/articles/invalid",
            status=422,
            result=[{"location": "article_key", "message": "Invalid"}],
            base_url="https://example.test",
        ))
        not_found = adapter.respond(SirenAdapterRequest(
            method="GET",
            path="/api/articles/missing",
            status=404,
            result={"detail": "Not found"},
            base_url="https://example.test",
        ))
        unmatched = adapter.respond(SirenAdapterRequest(
            method="GET",
            path="/api/unknown",
            status=404,
            result={"detail": "Not found"},
            base_url="https://example.test",
            request_url="https://example.test/api/unknown",
        ))

        assert collection.payload["class"] == ["collection", "article"]
        assert entity.payload["class"] == ["article"]
        assert entity.media_type == "application/vnd.siren+json"
        assert entity.headers == {"ETag": "one"}
        assert command.payload["class"] == ["command-result"]
        assert empty.payload["class"] == ["empty"]
        assert validation.payload["class"] == ["error"]
        assert validation.payload["properties"] == {
            "errors": [{"location": "article_key", "message": "Invalid"}],
            "status": 422,
        }
        assert not_found.payload == {
            "class": ["error"],
            "title": "Read article",
            "properties": {"detail": "Not found", "status": 404},
            "links": [
                {
                    "title": "Read article",
                    "rel": ["self"],
                    "href": "https://example.test/siren/articles/missing",
                }
            ],
        }
        assert unmatched.payload == {
            "class": ["error"],
            "properties": {"detail": "Not found", "status": 404},
            "links": [{"rel": ["self"], "href": "https://example.test/api/unknown"}],
        }

    def test_undeclared_errors_preserve_every_body_shape_and_operation_context(self):
        adapter = siren_adapter(self.schema, source_path="/api", public_path="/siren")

        mapping = adapter.respond(SirenAdapterRequest(
            method="GET",
            path="/api/articles/missing",
            status=404,
            result={"detail": "Missing"},
            base_url="https://example.test",
            request_url="https://example.test/api/articles/missing?trace=yes",
        ))
        scalar = adapter.respond(SirenAdapterRequest(
            operation_id="get_article",
            status=401,
            result="Denied",
            base_url="https://example.test",
            path_values={"article_key": "private"},
        ))
        empty = adapter.respond(SirenAdapterRequest(
            operation_id="get_article",
            status=500,
            base_url="https://example.test",
            path_values={"article_key": "broken"},
            policy=SirenAdapterPolicy(title="Unavailable"),
        ))

        assert mapping.payload == {
            "class": ["error"],
            "title": "Read article",
            "properties": {"detail": "Missing", "status": 404},
            "links": [
                {
                    "title": "Read article",
                    "rel": ["self"],
                    "href": "https://example.test/api/articles/missing?trace=yes",
                }
            ],
        }
        assert scalar.payload["properties"] == {"status": 401, "result": "Denied"}
        assert scalar.payload["links"][0]["href"] == "https://example.test/siren/articles/private"
        assert empty.payload["title"] == "Unavailable"
        assert empty.payload["properties"] == {"status": 500}

    @pytest.mark.parametrize(
        ("operation_id", "status", "media_type"),
        [
            ("delete_article", 404, "application/problem+json"),
            ("publish_article", 409, "application/json"),
            ("list_articles", 503, "application/json"),
        ],
    )
    def test_declared_exact_ranged_and_default_errors_remain_strict(
        self, operation_id, status, media_type
    ):
        adapter = siren_adapter(self.schema, source_path="/api", public_path="/siren")

        with pytest.raises(ModwireSirenError, match="Siren adapter response failed"):
            adapter.respond(SirenAdapterRequest(
                operation_id=operation_id,
                status=status,
                result="Declared object responses reject scalars",
                base_url="https://example.test",
                media_type=media_type,
                path_values={"article_key": "one"},
            ))

    def test_declared_status_with_an_incompatible_media_type_uses_generic_error(self):
        adapter = siren_adapter(self.schema, source_path="/api", public_path="/siren")

        response = adapter.respond(SirenAdapterRequest(
            operation_id="delete_article",
            status=404,
            result="Missing",
            base_url="https://example.test",
            media_type="application/json",
            path_values={"article_key": "missing"},
        ))

        assert response.payload["properties"] == {"status": 404, "result": "Missing"}

    def test_successful_undeclared_responses_remain_strict(self):
        adapter = siren_adapter(self.schema, source_path="/api", public_path="/siren")

        with pytest.raises(ModwireSirenError, match="Siren adapter response failed"):
            adapter.respond(SirenAdapterRequest(
                operation_id="get_article",
                status=201,
                result={"article_key": "one"},
                base_url="https://example.test",
            ))

    def test_django_bridge_executes_once_and_preserves_unselected_json(self):
        if not settings.configured:
            settings.configure(DEFAULT_CHARSET="utf-8", ALLOWED_HOSTS=["testserver"])
        adapter = siren_adapter(self.schema, source_path="/api", public_path="/siren")
        calls = []
        original = JsonResponse({"article_key": "one", "title": "One"}, headers={"ETag": "one"})

        def handler(request):
            calls.append(request.path)
            if request.path.endswith("invalid"):
                return JsonResponse(
                    [{"location": "article_key", "message": "Invalid"}], status=422, safe=False
                )
            return original

        policy = CapabilityPolicy()
        middleware = SirenDjangoMiddleware(get_response=handler, adapter=adapter, policy=policy)
        factory = RequestFactory()
        with override_settings(ALLOWED_HOSTS=["testserver"]):
            ordinary = middleware(factory.get("/api/articles/one", HTTP_ACCEPT="application/json"))
            siren = middleware(factory.get(
                "/api/articles/one?view=full&view=compact",
                HTTP_ACCEPT="application/vnd.siren+json",
            ))
            validation = middleware(factory.get(
                "/api/articles/invalid",
                HTTP_ACCEPT="application/vnd.siren+json",
            ))

        assert ordinary is original
        assert siren.status_code == 200
        assert siren["Content-Type"] == "application/vnd.siren+json"
        assert siren["ETag"] == "one"
        assert json.loads(siren.content)["class"] == ["article"]
        assert json.loads(validation.content)["properties"] == {
            "errors": [{"location": "article_key", "message": "Invalid"}],
            "status": 422,
        }
        assert calls == ["/api/articles/one", "/api/articles/one", "/api/articles/invalid"]
        assert policy.calls == [("get_article", 200), ("get_article", 422)]

    def test_root_import_keeps_django_optional(self):
        script = (
            "import builtins\n"
            "original = builtins.__import__\n"
            "def guarded(name, *args, **kwargs):\n"
            "    level = kwargs.get('level', args[3] if len(args) > 3 else 0)\n"
            "    if level == 0 and (name == 'django' or name.startswith('django.')):\n"
            "        raise AssertionError('core imported Django')\n"
            "    return original(name, *args, **kwargs)\n"
            "builtins.__import__ = guarded\n"
            "import modwire_siren\n"
        )

        result = subprocess.run((sys.executable, "-c", script), capture_output=True, text=True)

        assert result.returncode == 0, result.stderr
