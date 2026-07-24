from ..contracts import Contract
from ..vocabulary import SirenFieldType


class SirenField(Contract):
    name: str
    type: SirenFieldType
