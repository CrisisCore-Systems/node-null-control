import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


# Ensure repo root is importable even under pytest's importlib mode.
sys.path.insert(0, str(_repo_root()))

from scripts.validate_schemas import validate_repo_schemas  # noqa: E402


def test_all_json_schemas_are_valid() -> None:
    errors = validate_repo_schemas(_repo_root())
    assert not errors, "\n".join(errors)
