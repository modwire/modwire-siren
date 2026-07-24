import ast
from pathlib import Path


class ServiceConventionChecker:
    def run(self) -> int:
        root = Path(__file__).parents[1] / "src" / "modwire_siren"
        failures: list[str] = []
        for context in ("runtime", "compiler"):
            for path in sorted((root / context).glob("**/services/*.py")):
                if path.name == "__init__.py":
                    continue
                failures.extend(self.check(path))
        if not failures:
            return 0
        print("\n".join(failures))
        return 1

    def check(self, path: Path) -> list[str]:
        tree = ast.parse(path.read_text(), filename=str(path))
        failures: list[str] = []
        for node in (item for item in tree.body if isinstance(item, ast.ClassDef)):
            decorators = tuple(ast.unparse(decorator) for decorator in node.decorator_list)
            if not any(decorator.startswith("injectable") for decorator in decorators):
                failures.append(f"{path}: {node.name} must be @injectable")
            if "dataclass(frozen=True)" not in decorators:
                failures.append(f"{path}: {node.name} must be a frozen dataclass")
            if any(
                isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef)) and member.name == "__init__"
                for member in node.body
            ):
                failures.append(f"{path}: {node.name} must not declare __init__")
        return failures


raise SystemExit(ServiceConventionChecker().run())
