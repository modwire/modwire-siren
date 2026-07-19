from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class SirenRootRequest:

    self_href: str
    title: str = ""
    version: str = ""
    service_desc_href: str = ""
    extra_links: tuple[Mapping[str, Any], ...] = ()
