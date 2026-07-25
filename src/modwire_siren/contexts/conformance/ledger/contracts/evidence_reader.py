from abc import ABC, abstractmethod
from pathlib import Path

from modwire_siren.shared import ModwireSirenError

from ..values import SirenBddFeature


class SirenBddEvidenceReader(ABC):
    @abstractmethod
    def read(self, cucumber_report: Path, feature_directory: Path) -> tuple[SirenBddFeature, ...]:
        raise ModwireSirenError
