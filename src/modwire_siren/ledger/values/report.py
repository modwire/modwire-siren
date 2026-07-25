from dataclasses import dataclass

from .feature import SirenBddFeature
from .finding import SirenFinding


@dataclass(frozen=True)
class SirenConformanceReport:
    findings: tuple[SirenFinding, ...]
    features: tuple[SirenBddFeature, ...]
