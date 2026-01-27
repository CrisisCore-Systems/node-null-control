from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import jsonschema


@dataclass(frozen=True)
class SchemaResult:
    path: Path
    ok: bool
    error: str | None = None


def _iter_schema_files(repo_root: Path) -> Iterable[Path]:
    candidates: list[Path] = []

    # Canonical artifact schema
    candidates.append(repo_root / "artifacts" / "manifest.schema.json")

    # Product template schemas
    candidates.extend((repo_root / "products").glob("**/templates/*schema*.json"))
    candidates.extend((repo_root / "products").glob("**/templates/*_schema.json"))

    # De-dupe + keep deterministic ordering
    seen: set[Path] = set()
    for path in sorted({p.resolve() for p in candidates}):
        if not path.exists() or not path.is_file():
            continue
        if path in seen:
            continue
        seen.add(path)
        yield path


def _load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_schema_file(path: Path) -> SchemaResult:
    try:
        schema = _load_json(path)
    except Exception as exc:  # noqa: BLE001
        return SchemaResult(path=path, ok=False, error=f"failed to parse JSON: {exc}")

    try:
        validator_cls = jsonschema.validators.validator_for(schema)
        validator_cls.check_schema(schema)
    except Exception as exc:  # noqa: BLE001
        return SchemaResult(path=path, ok=False, error=f"invalid JSON Schema: {exc}")

    return SchemaResult(path=path, ok=True)


def validate_repo_schemas(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for schema_path in _iter_schema_files(repo_root):
        result = validate_schema_file(schema_path)
        if not result.ok:
            errors.append(f"{schema_path.as_posix()}: {result.error}")

    if not errors and not any(True for _ in _iter_schema_files(repo_root)):
        errors.append("No schema files found to validate.")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate JSON Schemas in the repository")
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Path to repo root (defaults to auto-detect from this script location)",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[1]
    errors = validate_repo_schemas(repo_root)
    if errors:
        for err in errors:
            print(err)
        return 1

    print("OK: JSON schema validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
