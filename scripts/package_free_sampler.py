#!/usr/bin/env python3
"""Package the Node-Null Free Sampler Pack for distribution.

Creates a single zip containing:
- products/free_sampler/*
- A convenient top-level LICENSE.txt

It intentionally excludes:
- build/, dist/, .git/

Usage:
  python scripts/package_free_sampler.py --out dist/gumroad/free_sampler/node_null_free_sampler_v01.zip
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path
from typing import Iterable, List, Set

EXCLUDE_PREFIXES = ("build/", "dist/", ".git/")


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for candidate in [cur] + list(cur.parents):
        if (candidate / ".git").exists():
            return candidate
    return start.resolve()


def should_exclude(rel_posix: str) -> bool:
    return rel_posix.startswith(EXCLUDE_PREFIXES)


def iter_files(folder: Path) -> Iterable[Path]:
    for p in folder.rglob("*"):
        if p.is_file():
            yield p


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--out",
        default="dist/gumroad/free_sampler/node_null_free_sampler_v01.zip",
        help="Output zip path under repo root (default: dist/gumroad/free_sampler/node_null_free_sampler_v01.zip)",
    )
    args = ap.parse_args(argv)

    repo_root = find_repo_root(Path(__file__).parent)

    sampler_root = repo_root / "products" / "free_sampler"
    if not sampler_root.exists():
        raise SystemExit("Missing products/free_sampler")

    out_path = (repo_root / args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Hygiene: keep outputs under dist/
    try:
        out_rel = out_path.relative_to(repo_root).as_posix()
    except Exception:
        raise SystemExit("--out must be inside the repo")
    if not out_rel.startswith("dist/"):
        raise SystemExit("--out must be under dist/")

    included: Set[str] = set()
    license_path = sampler_root / "LICENSE_sampler_v01.txt"
    if not license_path.exists():
        raise SystemExit("Missing products/free_sampler/LICENSE_sampler_v01.txt")
    license_text = license_path.read_text(encoding="utf-8")

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in iter_files(sampler_root):
            rel = p.relative_to(repo_root).as_posix()
            if should_exclude(rel):
                continue
            if rel in included:
                continue
            z.write(p, arcname=rel)
            included.add(rel)

        # Convenience license at zip root.
        z.writestr("LICENSE.txt", license_text)

    print(f"Wrote: {out_rel} ({len(included)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
