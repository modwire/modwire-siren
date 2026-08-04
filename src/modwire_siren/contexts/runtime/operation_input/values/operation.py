from collections.abc import Mapping

from pydantic import JsonValue

from modwire_siren.contexts.shared import BaseValue, SirenMediaType

from .delegated import SirenDelegatedInput


class SirenOperationInput(BaseValue):
    """Expose normalized input metadata for one compiled OpenAPI operation.

    `official_fields` names the values emitted as standard Siren action fields.
    `delegated_inputs` retains structured query values, headers, cookies, and body values for an
    adapter or transport. `definition` is the normalized request-body schema when one is declared.
    """

    media_type: SirenMediaType | None = None
    definition: Mapping[str, JsonValue] | None = None
    official_fields: tuple[str, ...] = ()
    delegated_inputs: tuple[SirenDelegatedInput, ...] = ()
