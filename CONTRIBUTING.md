# Contributing

This repository is documentation-first and governance-heavy. Contributions should improve repeatability, auditability, and safety.

## Quick start (dev)

- Python: `>=3.11` (CI uses `3.13`)
- Node: `>=20` (for JS lint/format)

### Python setup

```bash
python -m venv .venv
. .venv/bin/activate  # (PowerShell: .venv\Scripts\Activate.ps1)
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Run:

- `ruff check .`
- `black .`
- `pytest`
- `python scripts/validate_schemas.py`

### JS setup

```bash
npm install
npm run lint:js
npm run format:js
```

## Pre-commit

Install hooks:

```bash
pip install -e ".[dev]"
pre-commit install
pre-commit run --all-files
```

Hooks included:

- Formatting/linting: `black`, `ruff`
- Secret scanning: `gitleaks`, `detect-private-key`
- PII heuristics: `scripts/precommit_pii_scan.py`

## Governance expectations

- Do not commit secrets, credentials, or PII.
- Do not commit generated artifacts under `build/` or run outputs under `products/*/runs/*/outputs/`.
- If adding templates, keep variables and metadata stable unless you version-bump.

## CI

CI runs on every push/PR:

- Python: `ruff`, `black --check`, `pytest`, schema validation, forbidden-phrase scan
- JS: `eslint`, `prettier --check`
