from typing import Any

from modwire_siren.contexts.shared import BaseState, ModwireSirenError, SirenMediaType

from ..values import ResponseDraft
from .components import ComponentResolver


class OpenApiResponseProjection(BaseState):
    components: ComponentResolver

    def responses(self, operation: dict[str, Any]) -> tuple[ResponseDraft, ...]:
        responses = operation.get("responses")
        if not isinstance(responses, dict) or not responses:
            raise ModwireSirenError("OpenAPI operation responses must be a non-empty object")
        projected: list[ResponseDraft] = []
        for status, value in responses.items():
            if not isinstance(status, str):
                raise ModwireSirenError("OpenAPI response status must be a string")
            response = self.components.response(value)
            content = response.get("content", {})
            if not content:
                projected.append(ResponseDraft(status=status, shape="empty"))
                continue
            if not isinstance(content, dict):
                raise ModwireSirenError(f"OpenAPI response content must be an object: {status}")
            for media_name, media in content.items():
                if not isinstance(media_name, str) or not isinstance(media, dict):
                    raise ModwireSirenError(f"OpenAPI response media type is invalid: {status}")
                schema = media.get("schema")
                if not isinstance(schema, dict):
                    raise ModwireSirenError(f"OpenAPI response schema is required: {status} {media_name}")
                definition = self.components.schema(schema)
                shape = definition.get("type")
                if shape == "array":
                    items = definition.get("items")
                    if not isinstance(items, dict):
                        raise ModwireSirenError(f"OpenAPI array response requires item schema: {status} {media_name}")
                    item_definition = self.components.schema(items)
                    if item_definition.get("type") != "object":
                        raise ModwireSirenError(
                            f"OpenAPI array response items must be objects: {status} {media_name}"
                        )
                    definition = definition | {"items": item_definition}
                elif shape != "object":
                    raise ModwireSirenError(
                        f"OpenAPI response schema must be an object or array: {status} {media_name}"
                    )
                projected.append(ResponseDraft(
                    status=status,
                    media_type=SirenMediaType.validate(media_name),
                    shape=shape,
                    definition=definition,
                ))
        return tuple(projected)
