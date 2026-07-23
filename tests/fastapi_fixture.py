from typing import Any

from fastapi import FastAPI


class FastApiOpenApiFixture:
    def __init__(self) -> None:
        self.application = FastAPI(title="Framework fixture", version="1")
        self.application.add_api_route("/api/v1/widgets", self.list_widgets, methods=["GET"])
        self.application.add_api_route("/api/v1/widgets/{widget}", self.get_widget, methods=["GET"])

    def list_widgets(self) -> dict[str, list[dict[str, str]]]:
        return {"items": []}

    def get_widget(self, widget: str) -> dict[str, str]:
        return {"id": widget}

    def document(self) -> dict[str, Any]:
        return self.application.openapi()
