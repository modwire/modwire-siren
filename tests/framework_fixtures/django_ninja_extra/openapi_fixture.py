from typing import Any

from ninja_extra import NinjaExtraAPI

from .widget_controller import WidgetController


class DjangoNinjaExtraOpenApiFixture:
    def __init__(self) -> None:
        self.application = NinjaExtraAPI(title="Framework fixture", version="1")
        self.application.register_controllers(WidgetController)

    def document(self) -> dict[str, Any]:
        return self.application.get_openapi_schema(path_prefix="")
