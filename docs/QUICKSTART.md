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

## 5) Deployment

### Vercel (Automatic)

The repository is configured for automatic Vercel deployment on every push.

**Setup** (one-time):
1. Create a Vercel project and link this repository
2. Add GitHub Secrets: `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`
3. See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed instructions

**Usage**:
- Push to `main` → deploys to production
- Push to other branches → creates preview deployment
- Pull requests → creates preview deployment

### Manual Deployment

```bash
npm install -g vercel
vercel login
vercel          # Deploy preview
vercel --prod   # Deploy to production
```
