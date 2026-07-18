import argparse
import importlib
import inspect
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).parents[1]
START = "<!-- generated:public-api:start -->"
END = "<!-- generated:public-api:end -->"


class AnnotationText(str):
    def __repr__(self) -> str:
        return str(self)


@dataclass(frozen=True)
class PackageDocumentation:
    module: str
    readme: Path
    example: Path
    example_link: str


PACKAGES = (
    PackageDocumentation(
        "modwire_siren",
        ROOT / "README.md",
        ROOT / "examples/build_document.py",
        "examples/build_document.py",
    ),
    PackageDocumentation(
        "modwire_siren.profile",
        ROOT / "docs/siren-ui-profile/python-api.md",
        ROOT / "examples/profile.py",
        "../../examples/profile.py",
    ),
)


class DocumentationGenerator:
    @classmethod
    def render(cls, package: PackageDocumentation) -> str:
        module = importlib.import_module(package.module)
        rows = []
        for name in module.__all__:
            purpose = cls._purpose(name, getattr(module, name))
            operations = cls._operations(getattr(module, name))
            rows.append(f"| `{name}` | {purpose} | {operations} |")
        example = package.example.read_text().rstrip()
        return "\n".join(
            (
                START,
                "## Public API",
                "",
                f"The supported root imports below are generated from `{package.module}.__all__`.",
                "",
                "| Symbol | Purpose | Primary API |",
                "| --- | --- | --- |",
                *rows,
                "",
                "## Executable example",
                "",
                f"Source: [`{package.example.name}`]({package.example_link}). "
                "This file is executed by the test suite.",
                "",
                "```python",
                example,
                "```",
                END,
            )
        )

    @staticmethod
    def _purpose(name: str, value: object) -> str:
        if name == "__version__":
            return "Installed distribution version."
        documentation = inspect.getdoc(value)
        if not documentation:
            raise ValueError(f"Public symbol {name} must have a docstring")
        return documentation.splitlines()[0]

    @staticmethod
    def _operations(value: object) -> str:
        if not inspect.isclass(value):
            return "—"
        operations = []
        for name, member in value.__dict__.items():
            if name.startswith("_"):
                continue
            if isinstance(member, property):
                annotation = DocumentationGenerator._annotation(
                    inspect.signature(member.fget).return_annotation
                )
                operations.append(f"`{name}: {annotation}`")
                continue
            if not callable(getattr(value, name, None)):
                continue
            signature = DocumentationGenerator._signature(getattr(value, name))
            parameters = tuple(signature.parameters.values())
            if parameters and parameters[0].name in {"self", "cls"}:
                signature = signature.replace(parameters=parameters[1:])
            operations.append(f"`{name}{signature}`")
        return "<br>".join(operations) or "—"

    @staticmethod
    def _signature(value: object) -> inspect.Signature:
        signature = inspect.signature(value)
        parameters = tuple(
            parameter.replace(
                annotation=DocumentationGenerator._annotation(parameter.annotation),
                default=DocumentationGenerator._default(parameter.default),
            )
            for parameter in signature.parameters.values()
        )
        return signature.replace(
            parameters=parameters,
            return_annotation=DocumentationGenerator._annotation(
                signature.return_annotation
            ),
        )

    @staticmethod
    def _annotation(value: object) -> object:
        return AnnotationText(value) if isinstance(value, str) else value

    @staticmethod
    def _default(value: object) -> object:
        if value is inspect.Parameter.empty:
            return value
        if isinstance(value, str | int | float | bool | tuple | dict | type(None)):
            return value
        return AnnotationText(f"<{type(value).__module__}.{type(value).__qualname__}>")

    @classmethod
    def update(cls, package: PackageDocumentation, check: bool) -> bool:
        current = package.readme.read_text()
        generated = cls.render(package)
        if START not in current or END not in current:
            raise ValueError(f"Missing generated documentation markers in {package.readme}")
        prefix, remainder = current.split(START, 1)
        _, suffix = remainder.split(END, 1)
        expected = f"{prefix}{generated}{suffix}"
        if current == expected:
            return True
        if not check:
            package.readme.write_text(expected)
        return False

    @classmethod
    def run(cls, check: bool) -> int:
        stale = [package.readme for package in PACKAGES if not cls.update(package, check)]
        if check and stale:
            print("Generated documentation is stale:")
            for path in stale:
                print(f"- {path.relative_to(ROOT)}")
            print("Run `make docs` and commit the result.")
            return 1
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate public API and example sections in package READMEs.")
    parser.add_argument("--check", action="store_true", help="Fail instead of updating stale documentation.")
    raise SystemExit(DocumentationGenerator.run(parser.parse_args().check))
