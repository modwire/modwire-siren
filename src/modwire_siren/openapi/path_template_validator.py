import re


class OpenApiPathTemplateValidator:
    def validate(self, path: str) -> None:
        if not path.startswith("/"):
            raise ValueError("Siren resource paths must be absolute OpenAPI paths")
        placeholders = re.findall(r"{([^}]+)}", path)
        converters = tuple(placeholder for placeholder in placeholders if ":" in placeholder)
        if converters:
            raise ValueError(
                "Siren resource paths must use OpenAPI template syntax such as "
                f"{{record_slug}}, not framework converter syntax: {list(converters)}"
            )
