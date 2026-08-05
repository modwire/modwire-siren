from dataclasses import dataclass, field

from modwire_siren import SirenAdapterPolicy


@dataclass
class CapabilityPolicy:
    calls: list[tuple[str | None, int]] = field(default_factory=list)

    def select(self, operation_id, status, request, result):
        self.calls.append((operation_id, status))
        return SirenAdapterPolicy(capabilities=frozenset({"get_article"}))
