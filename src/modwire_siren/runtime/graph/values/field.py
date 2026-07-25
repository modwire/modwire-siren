from modwire_siren.shared import BaseValue

from ....vocabulary import SirenFieldType


class SirenField(BaseValue):
    name: str
    type: SirenFieldType
