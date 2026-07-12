from ..error import SirenError


class OpenApiError(SirenError):
    """Report invalid or incomplete OpenAPI data used for Siren projection."""

    def __init__(self, detail: str):
        super().__init__("openapi.invalid", detail)
