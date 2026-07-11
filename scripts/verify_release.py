import re
import sys
import tarfile
import zipfile
from email.parser import BytesParser
from pathlib import Path

SEMVER_TAG = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


class ReleaseVerifier:
    @classmethod
    def metadata(cls, path: Path):
        if path.suffix == ".whl":
            with zipfile.ZipFile(path) as archive:
                member = next(name for name in archive.namelist() if name.endswith(".dist-info/METADATA"))
                return BytesParser().parsebytes(archive.read(member))
        with tarfile.open(path) as archive:
            member = next(item for item in archive.getmembers() if item.name.endswith("/PKG-INFO"))
            extracted = archive.extractfile(member)
            if extracted is None:
                raise RuntimeError(f"Missing metadata in {path}")
            return BytesParser().parse(extracted)

    @classmethod
    def run(cls, tag: str, directory: str) -> int:
        if SEMVER_TAG.fullmatch(tag) is None:
            raise SystemExit(f"Release tag must be strict SemVer vX.Y.Z, got {tag!r}")
        artifacts = sorted(
            path for path in Path(directory).iterdir() if path.suffix == ".whl" or path.name.endswith(".tar.gz")
        )
        if len(artifacts) != 2:
            raise SystemExit(f"Expected one wheel and one sdist, found: {[path.name for path in artifacts]}")
        for artifact in artifacts:
            metadata = cls.metadata(artifact)
            if metadata["Name"] != "modwire-siren" or metadata["Version"] != tag[1:]:
                raise SystemExit(f"Unexpected metadata in {artifact.name}: {metadata['Name']} {metadata['Version']}")
        return 0


if __name__ == "__main__":
    raise SystemExit(ReleaseVerifier.run(*sys.argv[1:]))
