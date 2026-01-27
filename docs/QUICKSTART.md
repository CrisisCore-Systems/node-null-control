# Quick start

## 1) Clone + environment

- Python `>=3.11` (CI uses `3.13`)
- Node `>=20`

```bash
python -m venv .venv
. .venv/bin/activate  # (PowerShell: .venv\Scripts\Activate.ps1)
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

```bash
npm install
```

## 2) Common commands

- Validate schemas: `python scripts/validate_schemas.py`
- Run tests: `pytest`
- Lint Python: `ruff check .`
- Format Python: `black .`
- Lint JS: `npm run lint:js`
- Check JS formatting: `npm run format:js`

## 3) Governance gates

- Forbidden phrase scanning (for rendered outputs):

```bash
python scripts/scan_forbidden_phrases.py --paths products
```

Configure phrases in `ops/forbidden_phrases.txt`.

## 4) Pre-commit hooks

```bash
pre-commit install
pre-commit run --all-files
```
