import fnmatch
import importlib
import pkgutil
from dataclasses import dataclass, field
from types import ModuleType

from wireup import create_sync_container

from .compiler import SirenApiService
from .runtime.engine import SirenEngineFactory


@dataclass(frozen=True)
class SirenServiceModuleDiscovery:
    package: str = "modwire_siren"

    def modules(self, patterns: tuple[str, ...]) -> list[ModuleType]:
        root = importlib.import_module(self.package)
        names = sorted(
            module.name
            for module in pkgutil.walk_packages(root.__path__, f"{root.__name__}.")
            if any(fnmatch.fnmatchcase(module.name, pattern) for pattern in patterns)
        )
        return [importlib.import_module(name) for name in names]


@dataclass(frozen=True)
class SirenApplicationContainer:
    discovery: SirenServiceModuleDiscovery = field(default_factory=SirenServiceModuleDiscovery)

    def engine_factory(self) -> SirenEngineFactory:
        return self.container().get(SirenEngineFactory)

    def api_service(self) -> SirenApiService:
        return self.container().get(SirenApiService)

    def container(self):
        return create_sync_container(injectables=self.discovery.modules(("modwire_siren.**.services",)))
