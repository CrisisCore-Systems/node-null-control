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
python scripts/scan_forbidden_phrases.py --paths build/smoke
```

Configure phrases in `ops/forbidden_phrases.txt`.

- Product smoke checks (builds what is buildable, validates the rest):

```bash
python scripts/smoke_products.py --keep
```

## 4) Release builds (real deliverables)

Smoke builds default to dependency-light placeholders. Release builds opt into heavier artifacts:

```bash
python scripts/release_products.py --pdf-adapter wkhtmltopdf --bundle-dashboard-webapp
```

If you don't have `wkhtmltopdf` installed, keep `--pdf-adapter none` (placeholder PDFs) or use a custom command:

```bash
python scripts/release_products.py --pdf-adapter command --pdf-cmd "wkhtmltopdf {html} {pdf}" --bundle-dashboard-webapp
```

Outputs land under `build/release/<product>/<run_id>/`.

## 5) Pre-commit hooks

```bash
pre-commit install
pre-commit run --all-files
```
