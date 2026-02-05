# node-null-control

Control plane for a persona-less content operation: schemas, decision workflow, automation scripts, and build tooling for Ghost Network artifacts.

Start here:

- Mental model: [docs/00_mental_model.md](docs/00_mental_model.md)
- Rules/constitution: [docs/01_rules.md](docs/01_rules.md)
- Operations workflow: [docs/02_workflow.md](docs/02_workflow.md)
- Quickstart (dev + gates): [docs/QUICKSTART.md](docs/QUICKSTART.md)

This repo intentionally does **not** store raw media/working files (clips, renders, CapCut projects, audio, thumbnails). Keep those outside git.

## Repo map

- `products/` — product definitions, templates, and run inputs
- `scripts/` — build/release/packaging utilities (Python, dependency-minimal)
- `analytics/` — schema + decision logs
- `ops/` — governance configs (forbidden phrases, audit ignore lists, checklists)
- `build/` — generated outputs (smoke builds, release builds, weekly runs)
- `docs/` — rules + operations manuals

## Requirements

- Python `>=3.11` (CI uses `3.13`)
- Node `>=20` (for lint/format tooling)

## Setup

```bash
python -m venv .venv
. .venv/bin/activate  # PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"

npm install
```

## Common commands

- Validate schemas: `python scripts/validate_schemas.py`
- Run tests: `pytest`
- Lint Python: `ruff check .`
- Format Python: `black .`
- Lint JS: `npm run lint:js`
- Check JS formatting: `npm run format:js`

## Governance gates (CI-aligned)

- Forbidden phrase scan (configured in `ops/forbidden_phrases.txt`):

```bash
python scripts/scan_forbidden_phrases.py --paths build/smoke
```

- Product smoke checks (builds what is buildable, validates the rest):

```bash
python scripts/smoke_products.py --keep
```

## Building artifacts

Individual builders live under `scripts/build_*.py` (e.g. weekly brief, indices, reports, dashboards). Outputs land under `build/`.

For the Weekly Signal Brief, see the end-to-end flow in [docs/OPERATIONS.md](docs/OPERATIONS.md):

- Export weekly inputs into `products/weekly_signal_brief/runs/<WEEK_ID>/inputs/`
- Aggregate rollups: `python scripts/aggregate_weekly_inputs.py --run-json products/weekly_signal_brief/runs/<WEEK_ID>/run.json`
- Render brief: `python scripts/build_weekly_signal_brief.py --run products/weekly_signal_brief/runs/<WEEK_ID>/run.json --outdir build/weekly_signal_brief/<WEEK_ID>`

## Release builds (real deliverables)

Smoke builds default to dependency-light placeholders. Release builds opt into heavier artifacts (PDF packaging, dashboard bundling):

```bash
python scripts/release_products.py --pdf-adapter wkhtmltopdf --bundle-dashboard-webapp
```

If you don’t have `wkhtmltopdf` installed, keep `--pdf-adapter none` (placeholder PDFs), or provide a custom command.

## Forge / gateway UI

The public routing interface is a separate repo:

- https://github.com/CrisisCore-Systems/ghost-network-interface

This repo owns the *artifacts and control logic*; the interface repo owns the *privacy-first gateway*.

## Tooling notes

Typical stack:

- Scripts: ChatGPT
- Voice: ElevenLabs (neutral synthetic)
- Visuals: Runway / Pika / stock loops
- Edit: CapCut templates (auto subtitles + loop cut)
- Cross-post: Repurpose.io
- Schedule: Buffer
- Automations: Make.com / Zapier

Keep credentials outside the repo.

## Getting started (checklist)

1) Create accounts (TikTok / Shorts / Reels / FB Reels)
2) Build 1 CapCut master template (subtitles + loop ending)
3) Create Drive structure + naming conventions
4) Create the Google Sheet tracker
5) Start Week 1: controlled publishing + clean data collection

## Naming conventions

Short IDs:

`YYYY-MM-DD_platform_vertical_hookstyle_v01`

Example:

`2026-01-22_yt_AIThreat_H1_v01`

## License / compliance

Templates and analytics schema only.
No copyrighted assets, personal data, or credentials in this repo.

## Status

- Phase: **Ghost Network (Harvest)**
- Goal: **Extract the winning vertical + hook pattern**
- Next: **Brand Emergence (Forge) only after dominance**

## Forge (routing interface)

Neutral conversion interface (no personal branding):

- Forge node: [forge/README.md](forge/README.md)
- Deployment: [docs/VERCEL_DEPLOYMENT.md](docs/VERCEL_DEPLOYMENT.md)
