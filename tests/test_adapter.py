import json
import subprocess
import sys
from io import BytesIO
from typing import ClassVar

import pytest
from django.conf import settings
from django.core.handlers.base import BaseHandler
from django.http import (
    FileResponse,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
    StreamingHttpResponse,
)
from django.test import RequestFactory, override_settings
from framework_fixtures.capability_policy import CapabilityPolicy
from framework_fixtures.django_openapi_provider import django_openapi_provider
from framework_fixtures.root_capability_policy import RootCapabilityPolicy

from modwire_siren import (
    ModwireSirenError,
    SirenAdapter,
    SirenAdapterPolicy,
    SirenAdapterRequest,
    SirenDjangoMiddleware,
    SirenMiddleware,
    siren_adapter,
)


class TestAdapter:
    schema: ClassVar[dict[str, object]] = {
        "openapi": "3.1.1",
        "info": {"title": "Adapter API", "version": "4.0.0"},
        "paths": {
            "/api": {
                "get": {
                    "operationId": "get_api_root",
                    "summary": "Read API entry point",
                    "responses": {
                        "200": {
                            "description": "API entry point",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "version": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/api/reindex": {
                "post": {
                    "operationId": "reindex",
                    "summary": "Reindex content",
                    "responses": {
                        "202": {
                            "description": "Reindex accepted",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"accepted": {"type": "boolean"}},
                                    }
                                }
                            },
                        }
                    },
                }
            },
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
        assert entity.headers == {}
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

    def test_adapter_route_resolution_is_specific_deterministic_and_mount_independent(self):
        parameter_paths = {
            "/api/items/{item_id}": {
                "parameters": [
                    {
                        "name": "item_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "get": {
                    "operationId": "get_item",
                    "responses": {"204": {"description": "Item"}},
                },
            },
            "/api/items/{item_id}/commands/{command_name}": {
                "parameters": [
                    {
                        "name": "item_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    },
                    {
                        "name": "command_name",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    },
                ],
                "post": {
                    "operationId": "run_item_command",
                    "responses": {"204": {"description": "Command"}},
                },
            },
        }
        literal_paths = {
            "/api/items/search": {
                "get": {
                    "operationId": "search_items",
                    "responses": {"204": {"description": "Search"}},
                }
            },
            "/api/items/{item_id}/commands/retry": {
                "parameters": [
                    {
                        "name": "item_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    }
                ],
                "post": {
                    "operationId": "retry_item",
                    "responses": {"204": {"description": "Retry"}},
                },
            },
        }

        for paths in (
            parameter_paths | literal_paths,
            literal_paths | parameter_paths,
        ):
            adapter = siren_adapter(
                {
                    "openapi": "3.1.1",
                    "info": {"title": "Routes", "version": "4.0.0"},
                    "paths": paths,
                },
                source_path="/api",
                public_path="/siren",
            )

            assert adapter.match("get", "/api/items/search/").operation_id == "search_items"
            assert adapter.match("GET", "/siren/items/search").operation_id == "search_items"
            encoded = adapter.match("GET", "/api/items/%73earch")
            assert encoded.operation_id == "get_item"
            assert encoded.path_values == {"item_id": "search"}
            nested = adapter.match("post", "/siren/items/one/commands/retry/")
            assert nested.operation_id == "retry_item"
            assert nested.path_values == {"item_id": "one"}
            generic = adapter.match("POST", "/api/items/one/commands/archive")
            assert generic.operation_id == "run_item_command"
            assert generic.path_values == {"item_id": "one", "command_name": "archive"}
            assert adapter.match("DELETE", "/api/items/search") is None

    def test_adapter_construction_rejects_indistinguishable_route_templates(self):
        adapter = siren_adapter(self.schema, source_path="/api", public_path="/siren")

        with pytest.raises(
            ModwireSirenError,
            match=r"Ambiguous Siren adapter templates for GET /api/items/\{\}",
        ):
            SirenAdapter(
                engine=adapter.engine,
                routes=(
                    {
                        "source_path": "/api/items/{item_id}",
                        "public_path": "/siren/items/{item_id}",
                        "method": "GET",
                        "operation_id": "get_item",
                    },
                    {
                        "source_path": "/api/items/{slug}",
                        "public_path": "/siren/items/{slug}",
                        "method": "GET",
                        "operation_id": "get_item_by_slug",
                    },
                ),
            )

    def test_adapter_projects_api_entry_points_and_keeps_explicit_root_commands(self):
        adapter = siren_adapter(self.schema, source_path="/api", public_path="/siren")

        root = adapter.respond(SirenAdapterRequest(
            operation_id="get_api_root",
            status=200,
            result={"status": "ready", "version": "runtime"},
            base_url="https://example.test",
            query=(("view", "full"),),
            policy=SirenAdapterPolicy(
                representation="root",
                capabilities=frozenset({"reindex"}),
            ),
        ))
        command = adapter.respond(SirenAdapterRequest(
            operation_id="get_api_root",
            status=200,
            result={"status": "ready"},
            base_url="https://example.test",
            policy=SirenAdapterPolicy(representation="command"),
        ))
        titled = adapter.respond(SirenAdapterRequest(
            operation_id="get_api_root",
            status=200,
            result={"status": "ready"},
            base_url="https://example.test",
            policy=SirenAdapterPolicy(representation="root", title="Live API"),
        ))

        assert root.payload == {
            "class": ["api", "entry-point"],
            "title": "Adapter API",
            "properties": {"status": "ready", "version": "4.0.0"},
            "actions": [
                {
                    "name": "reindex",
                    "title": "Reindex content",
                    "href": "https://example.test/siren/reindex",
                    "method": "POST",
                }
            ],
            "links": [
                {
                    "title": "Adapter API",
                    "rel": ["self"],
                    "href": "https://example.test/siren?view=full",
                },
                {
                    "rel": ["collection"],
                    "href": "https://example.test/siren/articles",
                },
            ],
        }
        assert command.payload["class"] == ["command-result"]
        assert command.payload["links"] == [
            {
                "title": "Read API entry point",
                "rel": ["self"],
                "href": "https://example.test/siren",
            }
        ]
        assert titled.payload["title"] == "Live API"
        assert titled.payload["links"][0]["title"] == "Live API"

        with pytest.raises(ModwireSirenError, match="Siren adapter response failed"):
            adapter.respond(SirenAdapterRequest(
                operation_id="get_article",
                status=200,
                result={"article_key": "one"},
                base_url="https://example.test",
                policy=SirenAdapterPolicy(representation="root"),
            ))

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
        adapter = siren_adapter(self.schema, source_path="/api", public_path="/api")
        calls = []
        original = JsonResponse({"article_key": "one", "title": "One"}, headers={"ETag": "one"})

        def handler(request):
            calls.append(request.path)
            if request.method == "DELETE":
                return HttpResponse(status=204)
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
            empty = middleware(factory.delete(
                "/api/articles/one",
                HTTP_ACCEPT="application/vnd.siren+json",
            ))

        assert ordinary is original
        assert ordinary["Vary"] == "Accept"
        assert siren.status_code == 200
        assert siren["Content-Type"] == "application/vnd.siren+json"
        assert "ETag" not in siren
        assert siren["Vary"] == "Accept"
        assert json.loads(siren.content)["class"] == ["article"]
        assert json.loads(validation.content)["properties"] == {
            "errors": [{"location": "article_key", "message": "Invalid"}],
            "status": 422,
        }
        assert json.loads(empty.content)["class"] == ["empty"]
        assert calls == [
            "/api/articles/one",
            "/api/articles/one",
            "/api/articles/invalid",
            "/api/articles/one",
        ]
        assert policy.calls == [
            ("get_article", 200),
            ("get_article", 422),
            ("delete_article", 204),
        ]

    @pytest.mark.parametrize(
        ("accept", "selected"),
        (
            ("application/vnd.siren+json;q=0, application/json", False),
            ("application/vnd.siren+json;q=0.8, application/json;q=0.9", False),
            ("application/*", False),
            ("*/*", False),
            ("", False),
            ("APPLICATION/VND.SIREN+JSON", True),
            ("application/*;q=0.8, application/vnd.siren+json;q=0.9", True),
            ("application/json;q=0.5, application/*;q=0.9", True),
            ("application/vnd.siren+json;q=0.8, application/json;q=0.8", True),
            ("application/json;q=0.8, application/vnd.siren+json;q=0.8", False),
            ("application/vnd.siren+json;q=0, */*;q=1", False),
        ),
    )
    def test_django_bridge_negotiates_quality_specificity_and_wildcards(self, accept, selected):
        if not settings.configured:
            settings.configure(DEFAULT_CHARSET="utf-8", ALLOWED_HOSTS=["testserver"])
        adapter = siren_adapter(self.schema, source_path="/api", public_path="/api")
        original = JsonResponse({"article_key": "one", "title": "One"})
        calls = []

        def handler(request):
            calls.append(request.path)
            return original

        middleware = SirenDjangoMiddleware(
            get_response=handler,
            adapter=adapter,
            policy=CapabilityPolicy(),
        )
        request = RequestFactory().get("/api/articles/one", HTTP_ACCEPT=accept)
        with override_settings(ALLOWED_HOSTS=["testserver"]):
            response = middleware(request)

        assert (response["Content-Type"] == "application/vnd.siren+json") is selected
        assert (response is not original) is selected
        assert calls == ["/api/articles/one"]

    def test_django_bridge_replaces_representation_headers_and_preserves_semantics(self):
        if not settings.configured:
            settings.configure(DEFAULT_CHARSET="utf-8", ALLOWED_HOSTS=["testserver"])
        adapter = siren_adapter(self.schema, source_path="/api", public_path="/api")
        original = JsonResponse(
            {"article_key": "one", "title": "One"},
            headers={
                "Accept-Ranges": "bytes",
                "Cache-Control": "private",
                "Content-Digest": "sha-256=:source:",
                "Content-Encoding": "gzip",
                "Content-Length": "42",
                "Content-Range": "bytes 0-41/42",
                "Content-Security-Policy": "default-src 'none'",
                "Digest": "sha-256=source",
                "ETag": '"json"',
                "Last-Modified": "Wed, 05 Aug 2026 00:00:00 GMT",
                "Location": "/api/articles/one",
                "RateLimit-Limit": "100",
                "Vary": "Origin, Cookie",
                "WWW-Authenticate": 'Bearer realm="api"',
                "X-Request-ID": "request-one",
            },
        )
        original.set_cookie("session", "one", httponly=True, samesite="Strict")

        def handler(request):
            return original

        middleware = SirenDjangoMiddleware(
            get_response=handler,
            adapter=adapter,
            policy=CapabilityPolicy(),
        )
        with override_settings(ALLOWED_HOSTS=["testserver"]):
            response = middleware(RequestFactory().get(
                "/api/articles/one",
                HTTP_ACCEPT="application/vnd.siren+json",
                HTTP_IF_NONE_MATCH='"json"',
            ))

        for name in (
            "Accept-Ranges",
            "Content-Digest",
            "Content-Encoding",
            "Content-Range",
            "Digest",
            "ETag",
            "Last-Modified",
        ):
            assert name not in response
        assert response["Content-Type"] == "application/vnd.siren+json"
        assert "Content-Length" not in response
        assert response["Vary"] == "Origin, Cookie, Accept"
        assert response["Cache-Control"] == "private"
        assert response["Content-Security-Policy"] == "default-src 'none'"
        assert response["Location"] == "/api/articles/one"
        assert response["RateLimit-Limit"] == "100"
        assert response["WWW-Authenticate"] == 'Bearer realm="api"'
        assert response["X-Request-ID"] == "request-one"
        assert response.cookies["session"].value == "one"
        assert response.cookies["session"]["httponly"] is True
        assert response.cookies["session"]["samesite"] == "Strict"

    def test_django_bridge_passes_ineligible_responses_through_without_decoding(self):
        if not settings.configured:
            settings.configure(DEFAULT_CHARSET="utf-8", ALLOWED_HOSTS=["testserver"])
        adapter = siren_adapter(self.schema, source_path="/api", public_path="/api")
        policy = CapabilityPolicy()
        factory = RequestFactory()
        cases = (
            ("/openapi.json", JsonResponse({"openapi": "3.1.1"})),
            ("/health", JsonResponse({"status": "ok"})),
            ("/missing", HttpResponse("<h1>Missing</h1>", status=404, content_type="text/html")),
            ("/api/articles/one", HttpResponse("<h1>Article</h1>", content_type="text/html")),
            ("/api/articles/one", HttpResponseRedirect("/login")),
            ("/api/articles/one", HttpResponse(status=304)),
            (
                "/api/articles/one",
                StreamingHttpResponse(iter((b'{"article_key":"one"}',)), content_type="application/json"),
            ),
            ("/api/articles/one", FileResponse(BytesIO(b"article"))),
            (
                "/api/articles/one",
                HttpResponse(
                    '{"class":["article"]}', content_type="application/vnd.siren+json"
                ),
            ),
        )
        calls = []
        responses = [response for _, response in cases]

        def handler(request):
            calls.append(request.path)
            return responses.pop(0)

        with override_settings(ALLOWED_HOSTS=["testserver"]):
            for path, response in cases:
                middleware = SirenDjangoMiddleware(
                    get_response=handler,
                    adapter=adapter,
                    policy=policy,
                )
                returned = middleware(factory.get(
                    path,
                    HTTP_ACCEPT="application/vnd.siren+json",
                ))

                assert returned is response
                if response.status_code == 304:
                    assert returned["Vary"] == "Accept"
                response.close()

        assert calls == [path for path, _ in cases]
        assert policy.calls == []

    def test_django_bridge_projects_matched_json_suffix_responses(self):
        if not settings.configured:
            settings.configure(DEFAULT_CHARSET="utf-8", ALLOWED_HOSTS=["testserver"])
        adapter = siren_adapter(self.schema, source_path="/api", public_path="/api")
        policy = CapabilityPolicy()
        calls = []
        problem = HttpResponse(
            '{"detail":"Missing"}',
            status=404,
            content_type="application/problem+json; charset=utf-8",
        )

        def handler(request):
            calls.append(request.path)
            return problem

        middleware = SirenDjangoMiddleware(get_response=handler, adapter=adapter, policy=policy)
        factory = RequestFactory()
        with override_settings(ALLOWED_HOSTS=["testserver"]):
            response = middleware(factory.delete(
                "/api/articles/missing",
                HTTP_ACCEPT="application/vnd.siren+json",
            ))

        assert response["Content-Type"] == "application/vnd.siren+json"
        assert json.loads(response.content)["properties"] == {"detail": "Missing", "status": 404}
        assert calls == ["/api/articles/missing"]
        assert policy.calls == [("delete_article", 404)]

    def test_django_bridge_projects_browser_discovery_from_the_api_root(self):
        if not settings.configured:
            settings.configure(DEFAULT_CHARSET="utf-8", ALLOWED_HOSTS=["testserver"])
        adapter = siren_adapter(self.schema, source_path="/api", public_path="/api")
        calls = []

        def handler(request):
            calls.append(request.path)
            return JsonResponse({"status": "ready"})

        middleware = SirenDjangoMiddleware(
            get_response=handler,
            adapter=adapter,
            policy=RootCapabilityPolicy(),
        )
        factory = RequestFactory()
        with override_settings(ALLOWED_HOSTS=["testserver"]):
            response = middleware(factory.get(
                "/api?view=full",
                HTTP_ACCEPT="application/vnd.siren+json",
            ))

        payload = json.loads(response.content)
        assert payload["class"] == ["api", "entry-point"]
        assert payload["properties"] == {"status": "ready", "version": "4.0.0"}
        assert payload["links"][0]["href"] == "http://testserver/api?view=full"
        assert payload["links"][1]["href"] == "http://testserver/api/articles"
        assert calls == ["/api"]

    def test_django_bridge_rejects_an_independent_public_mount(self):
        adapter = siren_adapter(self.schema, source_path="/api", public_path="/siren")
        policy = CapabilityPolicy()

        def handler(request):
            return JsonResponse({"article_key": "one"})

        with pytest.raises(ModwireSirenError, match="requires identical source and public paths"):
            SirenDjangoMiddleware(get_response=handler, adapter=adapter, policy=policy)

    def test_standard_django_loader_builds_one_fresh_adapter_without_application_middleware(self):
        if not settings.configured:
            settings.configure(DEFAULT_CHARSET="utf-8", ALLOWED_HOSTS=["testserver"])
        django_openapi_provider.calls = 0
        configuration = {
            "OPENAPI": (
                "framework_fixtures.django_openapi_provider.django_openapi_provider"
            ),
            "SOURCE_PATH": "/api",
            "PUBLIC_PATH": "/api",
            "POLICY": "framework_fixtures.django_siren_policy.django_siren_policy",
        }
        factory = RequestFactory()

        with override_settings(
            ALLOWED_HOSTS=["testserver"],
            MIDDLEWARE=["modwire_siren.SirenMiddleware"],
            MODWIRE_SIREN=configuration,
            ROOT_URLCONF="framework_fixtures.django_urls",
        ):
            handler = BaseHandler()
            handler.load_middleware()
            ordinary = handler.get_response(factory.get(
                "/api/articles/one",
                HTTP_ACCEPT="application/json",
            ))
            siren = handler.get_response(factory.get(
                "/api/articles/one",
                HTTP_ACCEPT="application/vnd.siren+json",
            ))

        assert ordinary["Content-Type"].startswith("application/json")
        assert json.loads(siren.content)["class"] == ["article"]
        assert siren["Content-Type"] == "application/vnd.siren+json"
        assert django_openapi_provider.calls == 1

        with override_settings(MODWIRE_SIREN=configuration):
            SirenMiddleware(lambda request: JsonResponse({"article_id": "two", "title": "Fresh"}))

        assert django_openapi_provider.calls == 2

    def test_standard_django_loader_rejects_incomplete_configuration_at_startup(self):
        with (
            override_settings(MODWIRE_SIREN={"OPENAPI": "missing"}),
            pytest.raises(ModwireSirenError, match=r"MODWIRE_SIREN\.POLICY"),
        ):
            SirenMiddleware(lambda request: JsonResponse({}))

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
