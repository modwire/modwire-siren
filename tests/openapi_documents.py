SCHEMA = {
    "openapi": "3.1.1",
    "info": {"title": "Modwire", "version": "2"},
    "paths": {
        "/records": {"get": {"operationId": "list_records", "responses": {"200": {"description": "OK"}}}},
        "/records/{record_id}": {
            "parameters": [{"name": "record_id", "in": "path", "required": True, "schema": {"type": "string"}}],
            "get": {"operationId": "get_record", "responses": {"200": {"description": "OK"}}},
            "patch": {
                "operationId": "rename_record",
                "responses": {"200": {"description": "OK"}},
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["title"],
                                "properties": {"title": {"type": "string"}},
                            }
                        }
                    }
                },
            },
        },
    },
}

REFERENCED_SCHEMA = {
    "openapi": "3.1.1",
    "info": {"title": "Modwire", "version": "2"},
    "paths": {
        "/records": {
            "get": {
                "operationId": "list_records",
                "parameters": [{"$ref": "#/components/parameters/PageSize"}],
                "responses": {"200": {"description": "OK"}},
            }
        },
        "/records/{record_id}": {
            "parameters": [{"name": "record_id", "in": "path", "required": True, "schema": {"type": "string"}}],
            "patch": {
                "operationId": "rename_record",
                "requestBody": {"$ref": "#/components/requestBodies/RenameRecord"},
                "responses": {"200": {"description": "OK"}},
            },
        },
    },
    "components": {
        "parameters": {
            "PageSize": {
                "name": "page_size",
                "in": "query",
                "required": False,
                "schema": {"$ref": "#/components/schemas/PageSize"},
            }
        },
        "requestBodies": {
            "RenameRecord": {
                "required": True,
                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RenameRecord"}}},
            }
        },
        "schemas": {
            "PageSize": {"type": "integer"},
            "RenameRecord": {
                "type": "object",
                "required": ["title"],
                "properties": {"title": {"$ref": "#/components/schemas/Title", "type": "string"}},
            },
            "Title": {"type": "integer"},
        },
    },
}

ROUTE_POLICY_SCHEMA = {
    "openapi": "3.1.1",
    "info": {"title": "Routes", "version": "1"},
    "paths": {
        "/api/v2/labels": {
            "get": {"operationId": "list_labels", "responses": {"200": {"description": "OK"}}},
            "post": {"operationId": "create_label", "responses": {"201": {"description": "Created"}}},
        },
        "/api/v2/teams/{team}/records": {
            "parameters": [{"name": "team", "in": "path", "required": True, "schema": {"type": "string"}}],
            "get": {"operationId": "list_team_records", "responses": {"200": {"description": "OK"}}},
        },
        "/api/v2/teams/{team}/records/search": {
            "parameters": [{"name": "team", "in": "path", "required": True, "schema": {"type": "string"}}],
            "get": {"operationId": "search_team_records", "responses": {"200": {"description": "OK"}}},
        },
        "/api/v2/teams/{team}/records/{record}": {
            "parameters": [
                {"name": "team", "in": "path", "required": True, "schema": {"type": "string"}},
                {"name": "record", "in": "path", "required": True, "schema": {"type": "string"}},
            ],
            "get": {"operationId": "get_team_record", "responses": {"200": {"description": "OK"}}},
        },
        "/api/v2/teams/{team}/records/{record}/archive": {
            "parameters": [
                {"name": "team", "in": "path", "required": True, "schema": {"type": "string"}},
                {"name": "record", "in": "path", "required": True, "schema": {"type": "string"}},
            ],
            "post": {"operationId": "archive_team_record", "responses": {"204": {"description": "Archived"}}},
        },
        "/api/v2/teams/{team}/records/{record}/reports": {
            "parameters": [
                {"name": "team", "in": "path", "required": True, "schema": {"type": "string"}},
                {"name": "record", "in": "path", "required": True, "schema": {"type": "string"}},
            ],
            "get": {"operationId": "list_record_reports", "responses": {"200": {"description": "OK"}}},
        },
    },
}

PARAMETER_MEDIA_SCHEMA = {
    "openapi": "3.1.1",
    "info": {"title": "Fields", "version": "1"},
    "paths": {
        "/records": {
            "parameters": [
                {"name": "page", "in": "query", "required": False, "schema": {"type": "integer"}},
            ],
            "get": {
                "operationId": "list_records",
                "parameters": [
                    {"name": "page", "in": "query", "required": True, "schema": {"type": "string"}},
                ],
                "responses": {"200": {"description": "OK"}},
            },
        },
        "/records/{record_id}": {
            "parameters": [{"name": "record_id", "in": "path", "required": True, "schema": {"type": "string"}}],
            "patch": {
                "operationId": "replace_record",
                "requestBody": {
                    "content": {
                        "text/plain": {"schema": {"type": "string"}},
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["title"],
                                "properties": {"title": {"type": "string"}},
                            }
                        },
                    }
                },
                "responses": {"200": {"description": "OK"}},
            },
        },
    },
}
