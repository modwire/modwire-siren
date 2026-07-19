from ..error import SirenError


class OpenApiError(SirenError):

    def __init__(self, detail: str):
        super().__init__("openapi.invalid", detail)
