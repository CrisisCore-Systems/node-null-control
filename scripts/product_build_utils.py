from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Sequence, Set, Tuple

VAR_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_\-\.]+)\s*}}")


class BuildError(RuntimeError):
    pass


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise BuildError(f"Failed to read JSON: {path} ({exc})")


def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head_commit(repo_root: Path) -> Optional[str]:
    try:
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(repo_root), stderr=subprocess.DEVNULL)
        return out.decode("utf-8").strip()
    except Exception:  # noqa: BLE001
        return None


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for candidate in [cur] + list(cur.parents):
        if (candidate / ".git").exists():
            return candidate
    return Path.cwd().resolve()


def extract_allowlist_vars(allowlist_path: Path) -> Set[str]:
    text = allowlist_path.read_text(encoding="utf-8")
    allowed: Set[str] = set()
    for match in re.finditer(r"`{{\s*([^}]+?)\s*}}`", text):
        allowed.add(match.group(1).strip())
    if not allowed:
        raise BuildError(f"No allowlisted variables found in {allowlist_path}")
    return allowed


def extract_template_vars(template_text: str) -> Set[str]:
    return set(VAR_PATTERN.findall(template_text))


def render_template(template_text: str, values: Dict[str, str]) -> Tuple[str, Set[str]]:
    unresolved: Set[str] = set()

    def repl(m: re.Match[str]) -> str:
        key = m.group(1)
        if key in values:
            return str(values[key])
        unresolved.add(key)
        return m.group(0)

    rendered = VAR_PATTERN.sub(repl, template_text)
    return rendered, unresolved


def join_list(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)


def flatten_values(obj: Any) -> Dict[str, str]:
    if not isinstance(obj, dict):
        return {}
    out: Dict[str, str] = {}
    for k, v in obj.items():
        if v is None:
            out[str(k)] = ""
        elif isinstance(v, (str, int, float, bool)):
            out[str(k)] = str(v)
        elif isinstance(v, list):
            out[str(k)] = join_list(v)
        else:
            out[str(k)] = json.dumps(v, ensure_ascii=False, sort_keys=True)
    return out


def _content_type_for(p: Path) -> str:
    ext = p.suffix.lower()
    if ext == ".md":
        return "text/markdown"
    if ext == ".html":
        return "text/html"
    if ext == ".css":
        return "text/css"
    if ext == ".json":
        return "application/json"
    if ext == ".csv":
        return "text/csv"
    if ext == ".zip":
        return "application/zip"
    if ext == ".pdf":
        return "application/pdf"
    return "application/octet-stream"


def write_manifest(
    *,
    out_path: Path,
    run_id: str,
    asset_id: str,
    asset_version: str,
    repo_root: Path,
    repo_commit: str,
    generated_at_utc: str,
    builder_name: str,
    builder_version: str,
    manifest_schema_ref: str,
    input_files: Sequence[Path],
    output_files: Sequence[Path],
    unresolved_template_vars: Sequence[str],
) -> None:
    inputs = []
    for p in input_files:
        rel = p.resolve().relative_to(repo_root.resolve()).as_posix()
        inputs.append({"name": p.name, "path": rel, "sha256": sha256_file(p)})

    outputs = []
    for p in output_files:
        outputs.append(
            {
                "type": p.suffix.lstrip(".") or "file",
                "filename": p.name,
                "sha256": sha256_file(p),
                "size_bytes": p.stat().st_size,
                "content_type": _content_type_for(p),
                "storage": None,
                "url": None,
                "release_asset_name": None,
            }
        )

    obj: Dict[str, Any] = {
        "schema_version": "v01",
        "manifest_schema_ref": manifest_schema_ref,
        "run_id": run_id,
        "week_id": run_id,
        "asset_id": asset_id,
        "asset_version": asset_version,
        "repo_commit": repo_commit,
        "generated_at_utc": generated_at_utc,
        "builder": {"name": builder_name, "version": builder_version},
        "inputs": inputs,
        "outputs": outputs,
        "unresolved_template_vars": list(unresolved_template_vars),
    }

    write_json(out_path, obj)


def validate_manifest_schema(manifest: Dict[str, Any], schema_path: Path) -> None:
    if not schema_path.exists():
        raise BuildError(f"Manifest schema not found: {schema_path}")

    try:
        import jsonschema  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise BuildError(
            "Missing dependency 'jsonschema' required for manifest validation. "
            "Install it (pip install jsonschema) or run via CI. "
            f"({exc})"
        )

    schema = read_json(schema_path)
    try:
        jsonschema.Draft202012Validator(schema).validate(manifest)
    except jsonschema.ValidationError as exc:  # type: ignore[attr-defined]
        path_str = "/".join(str(p) for p in exc.path) if exc.path else "(root)"
        raise BuildError(f"Manifest failed schema validation at {path_str}: {exc.message}")


def validate_json_against_schema(data: Any, schema_path: Path) -> None:
    if not schema_path.exists():
        raise BuildError(f"Schema not found: {schema_path}")

    try:
        import jsonschema  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise BuildError(
            "Missing dependency 'jsonschema' required for schema validation. "
            "Install it (pip install jsonschema) or run via CI. "
            f"({exc})"
        )

    schema = read_json(schema_path)
    try:
        validator_cls = jsonschema.validators.validator_for(schema)
        validator_cls.check_schema(schema)
        validator = validator_cls(schema, format_checker=jsonschema.FormatChecker())
        validator.validate(data)
    except jsonschema.ValidationError as exc:  # type: ignore[attr-defined]
        path_str = "/".join(str(p) for p in exc.path) if exc.path else "(root)"
        raise BuildError(f"Output failed schema validation at {path_str}: {exc.message}")
    except jsonschema.SchemaError as exc:  # type: ignore[attr-defined]
        raise BuildError(f"Invalid schema {schema_path}: {exc}")


def write_minimal_pdf(path: Path, *, title: str, body_lines: Iterable[str]) -> None:
    # Minimal PDF (single page, Helvetica). Good enough for CI artifact existence.
    lines = ["BT", "/F1 14 Tf", "72 760 Td", f"({title}) Tj", "0 -24 Td"]
    for line in body_lines:
        safe = str(line).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        lines.append(f"({safe}) Tj")
        lines.append("0 -18 Td")
    lines.append("ET")
    stream = "\n".join(lines).encode("utf-8")

    objects: list[bytes] = []

    def add_obj(b: bytes) -> int:
        objects.append(b)
        return len(objects)

    # 1: catalog
    catalog_id = add_obj(b"<< /Type /Catalog /Pages 2 0 R >>")
    # 2: pages
    pages_id = add_obj(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    # 3: page
    page_id = add_obj(
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"
    )
    # 4: content stream
    content_id = add_obj(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")
    # 5: font
    font_id = add_obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    assert catalog_id == 1 and pages_id == 2 and page_id == 3 and content_id == 4 and font_id == 5

    out = bytearray()
    out.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    offsets: list[int] = [0]
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out.extend(f"{i} 0 obj\n".encode("ascii"))
        out.extend(obj)
        out.extend(b"\nendobj\n")

    xref_start = len(out)
    out.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode("ascii"))

    out.extend(
        b"trailer\n<< /Size "
        + str(len(objects) + 1).encode("ascii")
        + b" /Root 1 0 R >>\nstartxref\n"
        + str(xref_start).encode("ascii")
        + b"\n%%EOF\n"
    )

    path.write_bytes(bytes(out))
