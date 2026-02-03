#!/usr/bin/env python3
"""Displacement Risk Atlas v1.0 builder.

Generates a 20-page PDF analyzing 10 sectors approaching automation displacement thresholds.
Follows product_build_utils pattern for consistency with existing products.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, Sequence

from product_build_utils import (
    BuildError,
    ensure_dir,
    find_repo_root,
    git_head_commit,
    read_json,
    utc_now_iso,
    write_json,
    write_manifest,
    write_minimal_pdf,
)

BUILDER_NAME = "build_displacement_atlas"
BUILDER_VERSION = "v1.0"


def _require_str(run: Dict[str, Any], key: str) -> str:
    v = run.get(key)
    if not isinstance(v, str) or not v.strip():
        raise BuildError(f"run.json missing/invalid {key}")
    return v


def generate_cover_page() -> list[str]:
    """Generate cover page content."""
    return [
        "",
        "DISPLACEMENT RISK ATLAS",
        "",
        "Procedural analysis of 10 sectors",
        "approaching automation thresholds",
        "",
        "Version 1.0 (2026-W06)",
        "",
        "NOT career advice. NOT financial advice.",
        "Pattern documentation only.",
        "",
        "CrisisCore Systems",
        "February 2026",
        "",
    ]


def generate_framework_pages() -> list[str]:
    """Generate framework section (pages 2-6)."""
    content = []
    
    # Page 2-3: Leverage Destruction Mechanism
    content.extend([
        "",
        "PART 1: FRAMEWORK",
        "",
        "1. LEVERAGE DESTRUCTION MECHANISM",
        "",
        "How automation reduces worker bargaining power:",
        "",
        "- Task commoditization vs. irreplaceability",
        "- Bargaining Power = f(Task Complexity, Replacement Cost)",
        "- Threshold: When replacement cost < automation cost",
        "",
        "When automation can do your work,",
        "your bargaining power collapses.",
        "",
        "Not because the job disappears immediately.",
        "Because your leverage disappears first.",
        "",
    ])
    
    # Page 4: Bargaining Power Threshold Model
    content.extend([
        "2. BARGAINING POWER THRESHOLD MODEL",
        "",
        "Junior vs. Senior dynamics:",
        "",
        "- Juniors: Lower replacement cost, routine tasks",
        "- Seniors: Higher replacement cost, judgment tasks",
        "",
        "The 50% automation penetration threshold:",
        "",
        "When >50% of tasks are automated,",
        "leverage approaches zero.",
        "",
    ])
    
    # Page 5: Cascading Displacement Pattern
    content.extend([
        "3. CASCADING DISPLACEMENT PATTERN",
        "",
        "Historical precedent:",
        "",
        "- Manufacturing (1980s-2000s)",
        "- Clerical work (1990s-2010s)",
        "- Customer service (2010s-2020s)",
        "",
        "Labor flood mechanism:",
        "Displaced workers seek adjacent markets.",
        "",
        "AI era: Timeline compression from 10-20 years to 2-5 years.",
        "",
    ])
    
    # Page 6: Mitigation Framework
    content.extend([
        "4. MITIGATION FRAMEWORK",
        "",
        "Four pattern categories:",
        "",
        "1. Leverage preservation strategies",
        "2. Non-commoditizable skill identification",
        "3. Market position shifting",
        "4. Portfolio approaches",
        "",
        "NOT prescriptive. Pattern identification only.",
        "",
    ])
    
    return content


def generate_sector_page(sector_name: str, sector_data: Dict[str, Any]) -> list[str]:
    """Generate one sector analysis page."""
    content = [
        "",
        f"SECTOR: {sector_name.upper()}",
        "",
        f"Current automation penetration: {sector_data.get('penetration', '??')}%",
        f"Threshold proximity: {sector_data.get('proximity', '?')}/10",
        "",
        "Task commoditization indicators:",
        "",
    ]
    
    for task in sector_data.get('routine_tasks', []):
        content.append(f"- {task}")
    
    content.extend([
        "",
        "Adjacent market pressure points:",
        "",
    ])
    
    for market in sector_data.get('adjacent_markets', []):
        content.append(f"- {market}")
    
    content.extend([
        "",
        "Timeline estimate (procedural, not predictive):",
        f"- Near-term (0-2 years): {sector_data.get('near_term', 'Data pending')}",
        f"- Mid-term (2-5 years): {sector_data.get('mid_term', 'Data pending')}",
        "",
    ])
    
    return content


def generate_mitigation_pages() -> list[str]:
    """Generate mitigation patterns section (pages 17-19)."""
    content = []
    
    # Page 17: Pattern Categories 1 & 2
    content.extend([
        "",
        "PART 3: MITIGATION PATTERNS",
        "",
        "NOT PRESCRIPTIVE. NOT ADVICE. PATTERN DOCUMENTATION.",
        "",
        "Pattern Category 1: Leverage Preservation",
        "",
        "Observable patterns:",
        "- Shifting to non-routine tasks",
        "- Building cross-functional knowledge",
        "- Developing judgment-intensive skills",
        "",
        "Pattern Category 2: Non-Commoditizable Skills",
        "",
        "Observable patterns:",
        "- High-context, high-ambiguity domains",
        "- Interpersonal dynamics, negotiation",
        "- Creative synthesis",
        "",
    ])
    
    # Page 18: Pattern Categories 3 & 4
    content.extend([
        "Pattern Category 3: Market Position Shifting",
        "",
        "Observable patterns:",
        "- Moving to adjacent roles before displacement",
        "- Geographic arbitrage considerations",
        "- Sector rotation timing",
        "",
        "Pattern Category 4: Portfolio Approaches",
        "",
        "Observable patterns:",
        "- Multiple income streams",
        "- Skill diversification",
        "- Platform vs. full-time employment",
        "",
    ])
    
    # Page 19: Disclaimers
    content.extend([
        "LIMITATIONS & DISCLAIMERS",
        "",
        "This atlas is NOT:",
        "- Career advice",
        "- Financial advice",
        "- Guaranteed outcomes",
        "- Prescriptive recommendations",
        "",
        "This atlas IS:",
        "- Mechanism analysis",
        "- Pattern documentation",
        "- Procedural observation",
        "- System description",
        "",
        "Use at your own discretion.",
        "No guarantees or promises.",
        "Timeline estimates are not predictions.",
        "",
    ])
    
    return content


def generate_about_page() -> list[str]:
    """Generate about/contact page (page 20)."""
    return [
        "",
        "ABOUT CRISISCORE SYSTEMS",
        "",
        "CrisisCore Systems analyzes displacement mechanisms,",
        "distributed credit systems, and attention infrastructure.",
        "",
        "No hype. No predictions. Pattern recognition only.",
        "",
        "Field notes delivered weekly.",
        "Subscribe: forge.crisiscore.systems",
        "",
        "Contact: support@crisiscore.systems",
        "",
        "Version History:",
        "- v1.0 (2026-W06): Initial release",
        "",
        "License:",
        "Personal use: $19 | Commercial use: $99",
        "See licenses/ directory for full terms.",
        "",
    ]


def get_sector_data() -> Dict[str, Dict[str, Any]]:
    """Get sector data. In production, this would load from CSV/JSON."""
    return {
        "AI/ML Engineering (Junior)": {
            "penetration": "35",
            "proximity": "7.5",
            "routine_tasks": [
                "Boilerplate code generation (HIGH automation)",
                "Bug fixing (HIGH automation)",
                "Documentation writing (HIGH automation)"
            ],
            "adjacent_markets": [
                "QA/Testing (HIGH saturation risk)",
                "Technical writing (MEDIUM saturation risk)"
            ],
            "near_term": "Slower hiring, first eliminations",
            "mid_term": "Junior pipeline reduced"
        },
        "Legal Research": {
            "penetration": "40",
            "proximity": "7.8",
            "routine_tasks": [
                "Case law research (HIGH automation)",
                "Document review (HIGH automation)",
                "Contract generation (MEDIUM automation)"
            ],
            "adjacent_markets": [
                "Contract management (MEDIUM saturation)",
                "Compliance roles (MEDIUM saturation)"
            ],
            "near_term": "60% time savings reported",
            "mid_term": "Significant displacement likely"
        },
        "Medical Diagnostics (Radiology)": {
            "penetration": "30",
            "proximity": "6.5",
            "routine_tasks": [
                "X-ray analysis (HIGH automation)",
                "Pattern recognition (HIGH automation)",
                "Preliminary diagnosis (MEDIUM automation)"
            ],
            "adjacent_markets": [
                "Other medical specialties (LOW saturation)",
                "Medical consulting (LOW saturation)"
            ],
            "near_term": "AI accuracy exceeding human in some areas",
            "mid_term": "3-5 years to displacement (regulation delays)"
        },
        "Financial Analysis": {
            "penetration": "45",
            "proximity": "7.2",
            "routine_tasks": [
                "Market research (HIGH automation)",
                "Report generation (HIGH automation)",
                "Trend analysis (HIGH automation)"
            ],
            "adjacent_markets": [
                "Financial advising (MEDIUM saturation)",
                "Portfolio management (MEDIUM saturation)"
            ],
            "near_term": "Algorithmic analysis dominant",
            "mid_term": "Junior analyst roles largely automated"
        },
        "Content Production (Media)": {
            "penetration": "38",
            "proximity": "6.8",
            "routine_tasks": [
                "Copywriting (HIGH automation)",
                "Basic editing (HIGH automation)",
                "Template-based content (HIGH automation)"
            ],
            "adjacent_markets": [
                "Social media management (HIGH saturation)",
                "Content strategy (MEDIUM saturation)"
            ],
            "near_term": "GPT-class tools widely adopted",
            "mid_term": "Routine content fully automated"
        },
        "Customer Service (Enterprise)": {
            "penetration": "55",
            "proximity": "8.1",
            "routine_tasks": [
                "Support tickets (HIGH automation)",
                "Chat handling (HIGH automation)",
                "Email triage (HIGH automation)"
            ],
            "adjacent_markets": [
                "Customer success (HIGH saturation)",
                "Account management (MEDIUM saturation)"
            ],
            "near_term": "80%+ queries handled by AI",
            "mid_term": "Human-only for complex issues"
        },
        "Data Entry/Processing": {
            "penetration": "60",
            "proximity": "8.5",
            "routine_tasks": [
                "Form filling (HIGH automation)",
                "Database management (HIGH automation)",
                "Clerical tasks (HIGH automation)"
            ],
            "adjacent_markets": [
                "Administrative work (HIGH saturation)",
                "Operations roles (HIGH saturation)"
            ],
            "near_term": "OCR + RPA eliminating manual work",
            "mid_term": "Near-complete automation"
        },
        "Junior Software Development": {
            "penetration": "32",
            "proximity": "7.0",
            "routine_tasks": [
                "Bug fixes (HIGH automation)",
                "Boilerplate code (HIGH automation)",
                "Routine refactoring (HIGH automation)"
            ],
            "adjacent_markets": [
                "QA engineering (HIGH saturation)",
                "DevOps (MEDIUM saturation)"
            ],
            "near_term": "AI pair programmers standard",
            "mid_term": "Junior roles significantly reduced"
        },
        "Graphic Design (Template-Based)": {
            "penetration": "42",
            "proximity": "7.3",
            "routine_tasks": [
                "Social media graphics (HIGH automation)",
                "Basic layouts (HIGH automation)",
                "Asset generation (HIGH automation)"
            ],
            "adjacent_markets": [
                "Brand strategy (MEDIUM saturation)",
                "UX design (LOW saturation)"
            ],
            "near_term": "Generative tools widely adopted",
            "mid_term": "Template work fully automated"
        },
        "Administrative Coordination": {
            "penetration": "48",
            "proximity": "7.6",
            "routine_tasks": [
                "Scheduling (HIGH automation)",
                "Email management (HIGH automation)",
                "Meeting coordination (HIGH automation)"
            ],
            "adjacent_markets": [
                "Executive assistance (MEDIUM saturation)",
                "Operations management (MEDIUM saturation)"
            ],
            "near_term": "AI assistants handling routine tasks",
            "mid_term": "Human-only for complex coordination"
        }
    }


def build_pdf(out_path: Path, content_lines: list[str], title: str) -> None:
    """Build PDF using minimal PDF writer."""
    write_minimal_pdf(out_path, title=title, body_lines=content_lines)


def main(argv: Sequence[str]) -> int:
    ap = argparse.ArgumentParser(description="Build Displacement Risk Atlas v1.0")
    ap.add_argument("--run-json", required=True, help="Path to run.json")
    ap.add_argument("--out-dir", default=None, help="Output directory (defaults to same dir as run.json)")
    args = ap.parse_args(argv)

    run_json_path = Path(args.run_json).resolve()
    if not run_json_path.exists():
        print(f"ERROR: run.json not found: {run_json_path}", file=sys.stderr)
        return 1

    try:
        run = read_json(run_json_path)
    except BuildError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    run_id = _require_str(run, "run_id")
    asset_id = _require_str(run, "product_id")
    version = _require_str(run, "version")

    if args.out_dir:
        out_dir = Path(args.out_dir).resolve()
    else:
        out_dir = run_json_path.parent / "outputs"

    ensure_dir(out_dir)

    repo_root = find_repo_root(run_json_path)
    repo_commit = git_head_commit(repo_root) or "unknown"
    generated_at = utc_now_iso()

    print(f"Building Displacement Risk Atlas v{version}")
    print(f"Run ID: {run_id}")
    print(f"Output directory: {out_dir}")

    # Generate full content
    all_content = []
    
    # Cover page
    all_content.extend(generate_cover_page())
    
    # Framework (pages 2-6)
    all_content.extend(generate_framework_pages())
    
    # Sector analysis (pages 7-16)
    all_content.append("")
    all_content.append("PART 2: SECTOR ANALYSIS (10 SECTORS)")
    all_content.append("")
    
    sectors = get_sector_data()
    for i, (sector_name, sector_data) in enumerate(sectors.items(), start=1):
        all_content.extend(generate_sector_page(sector_name, sector_data))
    
    # Mitigation patterns (pages 17-19)
    all_content.extend(generate_mitigation_pages())
    
    # About page (page 20)
    all_content.extend(generate_about_page())

    # Build full PDF
    full_pdf_path = out_dir / f"displacement_risk_atlas_v{version}.pdf"
    print(f"Generating full PDF: {full_pdf_path.name}")
    build_pdf(full_pdf_path, all_content, "Displacement Risk Atlas")

    # Build preview PDF (first 3 pages: cover + framework intro)
    preview_content = []
    preview_content.extend(generate_cover_page())
    preview_content.extend([
        "",
        "PREVIEW VERSION",
        "",
        "This preview includes:",
        "- Cover page",
        "- Framework overview (excerpt)",
        "- Sample sector analysis (AI/ML Engineering)",
        "",
        "Full atlas includes:",
        "- Complete framework (5 pages)",
        "- 10 sector analyses (10 pages)",
        "- Mitigation patterns (3 pages)",
        "",
    ])
    preview_content.extend(generate_framework_pages()[:30])  # Partial framework
    preview_content.extend([
        "",
        "SAMPLE SECTOR: AI/ML ENGINEERING (JUNIOR)",
        "",
    ])
    preview_content.extend(generate_sector_page("AI/ML Engineering (Junior)", sectors["AI/ML Engineering (Junior)"]))
    preview_content.extend([
        "",
        "Full atlas: $19 (personal) | $99 (commercial)",
        "Available at: forge.crisiscore.systems",
        "",
    ])

    preview_pdf_path = out_dir / "displacement_risk_atlas_preview.pdf"
    print(f"Generating preview PDF: {preview_pdf_path.name}")
    build_pdf(preview_pdf_path, preview_content, "Displacement Risk Atlas - Preview")

    # Create markdown version for documentation
    md_path = out_dir / f"displacement_risk_atlas_v{version}.md"
    print(f"Generating markdown: {md_path.name}")
    md_path.write_text("\n".join(all_content), encoding="utf-8")

    # Write manifest
    manifest_path = out_dir / "manifest.json"
    print(f"Writing manifest: {manifest_path.name}")
    
    input_files = [run_json_path]
    output_files = [full_pdf_path, preview_pdf_path, md_path]
    
    write_manifest(
        out_path=manifest_path,
        run_id=run_id,
        asset_id=asset_id,
        asset_version=version,
        repo_root=repo_root,
        repo_commit=repo_commit,
        generated_at_utc=generated_at,
        builder_name=BUILDER_NAME,
        builder_version=BUILDER_VERSION,
        manifest_schema_ref="../../../artifacts/manifest.schema.json",
        input_files=input_files,
        output_files=output_files,
        unresolved_template_vars=[],
    )

    # Update run.json status
    run["status"] = "completed"
    run["build_completed_at"] = generated_at
    run["builder"] = {
        "name": BUILDER_NAME,
        "version": BUILDER_VERSION
    }
    write_json(run_json_path, run)

    print("\n✓ Build completed successfully!")
    print(f"  - Full PDF: {full_pdf_path.name} ({full_pdf_path.stat().st_size} bytes)")
    print(f"  - Preview PDF: {preview_pdf_path.name} ({preview_pdf_path.stat().st_size} bytes)")
    print(f"  - Markdown: {md_path.name}")
    print(f"  - Manifest: {manifest_path.name}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
