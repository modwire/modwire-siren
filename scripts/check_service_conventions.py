import ast
from pathlib import Path


class ServiceConventionChecker:
    def run(self) -> int:
        root = Path(__file__).parents[1] / "src" / "modwire_siren"
        failures: list[str] = []
        for context in ("runtime", "compiler", "conformance"):
            for path in sorted((root / context).glob("**/*.py")):
                if path.name == "__init__.py":
                    continue
                failures.extend(self.check(path))
        if not failures:
            return 0
        print("\n".join(failures))
        return 1

    def check(self, path: Path) -> list[str]:
        source = path.read_text()
        tree = ast.parse(source, filename=str(path))
        classes = tuple(item for item in tree.body if isinstance(item, ast.ClassDef))
        failures: list[str] = []
        if "TYPE_CHECKING" in source:
            failures.append(f"{path}: TYPE_CHECKING is forbidden")
        if "create_sync_container" in source:
            failures.append(f"{path}: containers belong only in wiring.py")
        if "@injectable" in source and "services" not in path.parts:
            failures.append(f"{path}: injectables belong only in services")
        for node in classes:
            if any(
                isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and member.name == "__init__"
                for member in node.body
            ):
                failures.append(f"{path}: {node.name} must not declare __init__")
        if "state" in path.parts:
            for node in classes:
                decorators = tuple(ast.unparse(decorator) for decorator in node.decorator_list)
                if not any(decorator.startswith("dataclass") for decorator in decorators):
                    failures.append(f"{path}: {node.name} must be a dataclass")
        if "services" not in path.parts:
            return failures
        for node in classes:
            decorators = tuple(ast.unparse(decorator) for decorator in node.decorator_list)
            if not any(decorator.startswith("injectable") for decorator in decorators):
                failures.append(f"{path}: {node.name} must be @injectable")
            if "dataclass(frozen=True)" not in decorators:
                failures.append(f"{path}: {node.name} must be a frozen dataclass")
        return failures


raise SystemExit(ServiceConventionChecker().run())
