import json
import subprocess
import sys
from typing import ClassVar

from django.conf import settings
from django.http import JsonResponse
from django.test import RequestFactory, override_settings
from framework_fixtures.capability_policy import CapabilityPolicy

from modwire_siren import (
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
                        }
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
                    "responses": {
                        "200": {
                            "description": "Article",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Article"}
                                }
                            },
                        },
                        "404": {
                            "description": "Missing",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Problem"}
                                }
                            },
                        },
                        "422": {
                            "description": "Invalid",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "array", "items": {"type": "object"}}
                                }
                            },
                        },
                    },
                },
                "delete": {
                    "operationId": "delete_article",
                    "responses": {"204": {"description": "Deleted"}},
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
                        }
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
            "properties": {"detail": "Not found", "status": 404},
            "links": [{"rel": ["self"], "href": "https://example.test/siren/articles/missing"}],
        }
        assert unmatched.payload == {
            "class": ["error"],
            "properties": {"detail": "Not found", "status": 404},
            "links": [{"rel": ["self"], "href": "https://example.test/api/unknown"}],
        }

    def test_django_bridge_executes_once_and_preserves_unselected_json(self):
        if not settings.configured:
            settings.configure(DEFAULT_CHARSET="utf-8", ALLOWED_HOSTS=["testserver"])
        adapter = siren_adapter(self.schema, source_path="/api", public_path="/siren")
        calls = []
        original = JsonResponse({"article_key": "one", "title": "One"}, headers={"ETag": "one"})

        def handler(request):
            calls.append(request.path)
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

        assert ordinary is original
        assert siren.status_code == 200
        assert siren["Content-Type"] == "application/vnd.siren+json"
        assert siren["ETag"] == "one"
        assert json.loads(siren.content)["class"] == ["article"]
        assert calls == ["/api/articles/one", "/api/articles/one"]
        assert policy.calls == [("get_article", 200)]

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
