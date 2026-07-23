from .rename_widget_payload import RenameWidgetPayload


class WidgetController:
    def list_widgets(self, page: int = 1) -> dict[str, list[dict[str, str]]]:
        return {"items": []}

    def get_widget(self, widget: str) -> dict[str, str]:
        return {"id": widget}

    def rename_widget(self, widget: str, payload: RenameWidgetPayload) -> dict[str, str]:
        return {"id": widget, "title": payload.title}
