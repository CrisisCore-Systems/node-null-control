from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
AWS_ACCESS_KEY_RE = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
PRIVATE_KEY_BLOCK_RE = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")


def luhn_ok(number: str) -> bool:
    digits = [int(c) for c in number if c.isdigit()]
    if len(digits) < 13:
        return False

    checksum = 0
    parity = len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d = d * 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


CC_CANDIDATE_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")


@dataclass(frozen=True)
class Finding:
    path: Path
    message: str


def scan_text(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []

    if PRIVATE_KEY_BLOCK_RE.search(text):
        findings.append(Finding(path=path, message="private key block detected"))

    if AWS_ACCESS_KEY_RE.search(text):
        findings.append(Finding(path=path, message="AWS access key id pattern detected"))

    if SSN_RE.search(text):
        findings.append(Finding(path=path, message="SSN pattern detected"))

    for m in CC_CANDIDATE_RE.finditer(text):
        raw = m.group(0)
        digits = "".join(c for c in raw if c.isdigit())
        if 13 <= len(digits) <= 19 and luhn_ok(digits):
            findings.append(Finding(path=path, message="possible credit card number detected (Luhn valid)"))
            break

    return findings


def main(argv: list[str]) -> int:
    file_args = [a for a in argv[1:] if a and not a.startswith("-")]
    if not file_args:
        return 0

    repo_root = Path(__file__).resolve().parents[1]

    findings: list[Finding] = []
    for raw in file_args:
        path = Path(raw)
        if not path.is_absolute():
            path = (repo_root / path).resolve()

        if not path.exists() or not path.is_file():
            continue

        # Skip known generated locations
        lowered_parts = {p.lower() for p in path.parts}
        if {"dist", "build"} & lowered_parts:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        findings.extend(scan_text(path, text))

    if findings:
        for f in findings:
            rel = f.path.relative_to(repo_root) if f.path.is_relative_to(repo_root) else f.path
            print(f"PII/secret risk: {rel}: {f.message}")
        print("If this is a false positive, remove/redact it, or move it to a non-tracked location.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
