from .values.action import SirenAction
from .values.document import SirenDocument
from .values.embedded_link import SirenEmbeddedLink
from .values.embedded_representation import SirenEmbeddedRepresentation
from .values.field import SirenField
from .values.field_value import SirenFieldValue
from .values.link import SirenLink

SirenDocument.model_rebuild(
    _types_namespace={
        "SirenAction": SirenAction,
        "SirenEmbeddedLink": SirenEmbeddedLink,
        "SirenEmbeddedRepresentation": SirenEmbeddedRepresentation,
        "SirenLink": SirenLink,
    }
)
SirenEmbeddedRepresentation.model_rebuild(
    _types_namespace={
        "SirenAction": SirenAction,
        "SirenEmbeddedLink": SirenEmbeddedLink,
        "SirenEmbeddedRepresentation": SirenEmbeddedRepresentation,
        "SirenLink": SirenLink,
    }
)

__all__ = [
    "SirenAction",
    "SirenDocument",
    "SirenEmbeddedLink",
    "SirenEmbeddedRepresentation",
    "SirenField",
    "SirenFieldValue",
    "SirenLink",
]
