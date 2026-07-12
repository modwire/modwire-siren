from collections.abc import Iterable

from ..error import SirenError
from .pointer import JsonPointer


class ReferenceValidator:
    def __init__(self, issues: Iterable[dict[str, str]] = ()):
        self._issues = list(issues)

    def require(
        self,
        names: Iterable[str],
        available: set[str],
        pointer: str,
        label: str,
    ) -> None:
        self._issues.extend(
            {
                "pointer": JsonPointer.join(pointer, name),
                "message": f"Profile references unknown Siren {label}: {name!r}",
            }
            for name in names
            if name not in available
        )

    def issue(self, pointer: str, message: str) -> None:
        self._issues.append({"pointer": pointer, "message": message})

    def require_value(
        self,
        name: str,
        available: set[str],
        pointer: str,
        label: str,
    ) -> None:
        if name not in available:
            self.issue(pointer, f"Profile references unknown Siren {label}: {name!r}")

    def finish(self) -> None:
        if self._issues:
            raise SirenError(
                "profile.invalid",
                "Siren UI profile contains invalid references",
                issues=tuple(self._issues),
            )
