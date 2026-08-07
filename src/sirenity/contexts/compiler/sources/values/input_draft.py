from collections.abc import Mapping

from pydantic import JsonValue

from sirenity.contexts.shared import BaseValue, SirenMediaType

from .delegated_input_draft import DelegatedInputDraft


class InputDraft(BaseValue):
    media_type: SirenMediaType | None = None
    definition: Mapping[str, JsonValue] | None = None
    official_fields: tuple[str, ...] = ()
    delegated_inputs: tuple[DelegatedInputDraft, ...] = ()
