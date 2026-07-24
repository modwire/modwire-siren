from abc import ABC, abstractmethod
from pathlib import Path

from ..values import SirenBddFeature


class SirenBddEvidenceReader(ABC):
    @abstractmethod
    def read(self, cucumber_report: Path) -> tuple[SirenBddFeature, ...]:
        raise NotImplementedError
