from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_TEXT_EXTS = {
    ".txt",
    ".md",
    ".csv",
    ".json",
    ".yml",
    ".yaml",
    ".html",
    ".js",
}


@dataclass(frozen=True)
class Match:
    path: Path
    phrase: str
    line_no: int
    line: str


def load_phrases(path: Path) -> list[str]:
    phrases: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        phrases.append(line)
    return phrases


def iter_target_files(paths: Iterable[Path], include_exts: set[str]) -> Iterable[Path]:
    for base in paths:
        if base.is_file():
            if base.suffix.lower() in include_exts:
                yield base
            continue

        if base.is_dir():
            for file_path in base.rglob("*"):
                if not file_path.is_file():
                    continue
                if file_path.name == ".gitkeep":
                    continue
                if file_path.suffix.lower() not in include_exts:
                    continue
                yield file_path


def scan_file(path: Path, phrases: list[str]) -> list[Match]:
    matches: list[Match] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return matches

    lowered_phrases = [(p, p.lower()) for p in phrases]
    for idx, line in enumerate(text.splitlines(), start=1):
        hay = line.lower()
        for original, needle in lowered_phrases:
            if needle in hay:
                matches.append(Match(path=path, phrase=original, line_no=idx, line=line.rstrip()))
    return matches


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan generated outputs for forbidden phrases")
    parser.add_argument(
        "--config",
        default="ops/forbidden_phrases.txt",
        help="Path to forbidden phrase list file",
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        default=["products"],
        help="Files/directories to scan (defaults to products)",
    )
    parser.add_argument(
        "--ext",
        nargs="*",
        default=sorted(DEFAULT_TEXT_EXTS),
        help="File extensions to include (defaults to common text formats)",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[1]
    config_path = (repo_root / args.config).resolve() if not Path(args.config).is_absolute() else Path(args.config)
    phrases = load_phrases(config_path)
    if not phrases:
        print("OK: no forbidden phrases configured")
        return 0

    targets = [(repo_root / p).resolve() if not Path(p).is_absolute() else Path(p) for p in args.paths]
    include_exts = {e if e.startswith(".") else f".{e}" for e in args.ext}

    all_matches: list[Match] = []
    for file_path in iter_target_files(targets, include_exts=include_exts):
        # Skip templates; this scanner is for rendered outputs.
        if "templates" in {part.lower() for part in file_path.parts}:
            continue
        all_matches.extend(scan_file(file_path, phrases))

    if all_matches:
        for m in all_matches:
            rel = m.path.relative_to(repo_root) if m.path.is_relative_to(repo_root) else m.path
            print(f"{rel}:{m.line_no}: {m.phrase}: {m.line}")
        return 2

    print("OK: forbidden phrase scan passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
