from ....vocabulary import SirenFieldType
from ...contracts import Contract


class SirenField(Contract):
    name: str
    type: SirenFieldType
