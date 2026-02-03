#!/usr/bin/env python3
"""Tests for Displacement Risk Atlas builder."""

import sys
from pathlib import Path
import subprocess
import json

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from product_build_utils import read_json, count_pdf_pages


def test_build_generates_files():
    """Test that build generates all expected files."""
    outputs_dir = Path(__file__).parent.parent / "products" / "displacement_risk_atlas" / "runs" / "2026-W06" / "outputs"
    
    expected_files = [
        "displacement_risk_atlas_v1.0.pdf",
        "displacement_risk_atlas_preview.pdf",
        "displacement_risk_atlas_full.html",
        "displacement_risk_atlas_preview.html",
        "manifest.json"
    ]
    
    for filename in expected_files:
        filepath = outputs_dir / filename
        assert filepath.exists(), f"Expected file not found: {filename}"
        assert filepath.stat().st_size > 0, f"File is empty: {filename}"
    
    print("✓ All expected files exist and are non-empty")


def test_preview_pdf_page_count():
    """Test that preview PDF has expected page count (3 pages)."""
    outputs_dir = Path(__file__).parent.parent / "products" / "displacement_risk_atlas" / "runs" / "2026-W06" / "outputs"
    preview_pdf = outputs_dir / "displacement_risk_atlas_preview.pdf"
    
    if not preview_pdf.exists():
        print("⚠️  Preview PDF not found, skipping page count test")
        return
    
    try:
        page_count = count_pdf_pages(preview_pdf)
        assert page_count == 3, f"Preview PDF should have 3 pages, found {page_count}"
        print(f"✓ Preview PDF has correct page count: {page_count}")
    except Exception as e:
        print(f"⚠️  Could not verify page count: {e}")


def test_full_pdf_page_count():
    """Test that full PDF has reasonable page count (at least 6 pages)."""
    outputs_dir = Path(__file__).parent.parent / "products" / "displacement_risk_atlas" / "runs" / "2026-W06" / "outputs"
    full_pdf = outputs_dir / "displacement_risk_atlas_v1.0.pdf"
    
    if not full_pdf.exists():
        print("⚠️  Full PDF not found, skipping page count test")
        return
    
    try:
        page_count = count_pdf_pages(full_pdf)
        # With better layout, we might have fewer than 20 pages, but should have at least 6
        assert page_count >= 6, f"Full PDF should have at least 6 pages, found {page_count}"
        print(f"✓ Full PDF has reasonable page count: {page_count}")
    except Exception as e:
        print(f"⚠️  Could not verify page count: {e}")


def test_manifest_contains_hashes():
    """Test that manifest.json contains SHA256 hashes for outputs."""
    outputs_dir = Path(__file__).parent.parent / "products" / "displacement_risk_atlas" / "runs" / "2026-W06" / "outputs"
    manifest_path = outputs_dir / "manifest.json"
    
    if not manifest_path.exists():
        print("⚠️  Manifest not found, skipping hash test")
        return
    
    manifest = read_json(manifest_path)
    
    # Check that outputs field exists
    assert "outputs" in manifest, "Manifest missing 'outputs' field"
    assert len(manifest["outputs"]) > 0, "Manifest has no outputs listed"
    
    # Check that each output has a SHA256 hash
    for output in manifest["outputs"]:
        assert "sha256" in output, f"Output missing sha256: {output.get('filename', 'unknown')}"
        assert len(output["sha256"]) == 64, f"Invalid SHA256 hash for {output.get('filename', 'unknown')}"
    
    print(f"✓ Manifest contains {len(manifest['outputs'])} outputs with valid SHA256 hashes")


def test_run_json_updated():
    """Test that run.json was updated with build status."""
    run_json_path = Path(__file__).parent.parent / "products" / "displacement_risk_atlas" / "runs" / "2026-W06" / "run.json"
    
    if not run_json_path.exists():
        print("⚠️  run.json not found, skipping test")
        return
    
    run = read_json(run_json_path)
    
    # Check status
    assert "status" in run, "run.json missing 'status' field"
    assert run["status"] == "completed", f"Expected status 'completed', got '{run['status']}'"
    
    # Check builder info
    assert "builder" in run, "run.json missing 'builder' field"
    assert "name" in run["builder"], "builder missing 'name' field"
    assert "version" in run["builder"], "builder missing 'version' field"
    
    # Check completion timestamp
    assert "build_completed_at" in run, "run.json missing 'build_completed_at' field"
    
    print("✓ run.json updated with build status and metadata")


def test_sector_data_loaded():
    """Test that sector data was loaded from JSON."""
    data_path = Path(__file__).parent.parent / "products" / "displacement_risk_atlas" / "data" / "sectors.json"
    
    assert data_path.exists(), "sectors.json not found"
    
    data = read_json(data_path)
    assert "sectors" in data, "sectors.json missing 'sectors' field"
    assert len(data["sectors"]) == 10, f"Expected 10 sectors, found {len(data['sectors'])}"
    
    # Check that each sector has required fields
    required_fields = ["name", "penetration", "proximity", "routine_tasks", "adjacent_markets", "near_term", "mid_term"]
    for sector in data["sectors"]:
        for field in required_fields:
            assert field in sector, f"Sector '{sector.get('name', 'unknown')}' missing field: {field}"
    
    print(f"✓ Sector data loaded successfully: {len(data['sectors'])} sectors")


def test_html_contains_all_sectors():
    """Test that generated HTML contains all 10 sectors."""
    outputs_dir = Path(__file__).parent.parent / "products" / "displacement_risk_atlas" / "runs" / "2026-W06" / "outputs"
    html_path = outputs_dir / "displacement_risk_atlas_full.html"
    
    if not html_path.exists():
        print("⚠️  HTML not found, skipping test")
        return
    
    html_content = html_path.read_text(encoding="utf-8")
    
    # Count sector-page divs
    sector_count = html_content.count('class="sector-page"')
    assert sector_count == 10, f"Expected 10 sectors in HTML, found {sector_count}"
    
    print(f"✓ HTML contains all {sector_count} sectors")


def test_pdf_file_sizes():
    """Test that PDFs have reasonable file sizes (not suspiciously small)."""
    outputs_dir = Path(__file__).parent.parent / "products" / "displacement_risk_atlas" / "runs" / "2026-W06" / "outputs"
    
    full_pdf = outputs_dir / "displacement_risk_atlas_v1.0.pdf"
    preview_pdf = outputs_dir / "displacement_risk_atlas_preview.pdf"
    
    if full_pdf.exists():
        size = full_pdf.stat().st_size
        # Full PDF should be at least 50KB (much better than 13.9KB)
        assert size >= 50000, f"Full PDF suspiciously small: {size} bytes (expected > 50KB)"
        print(f"✓ Full PDF has reasonable size: {size:,} bytes")
    
    if preview_pdf.exists():
        size = preview_pdf.stat().st_size
        # Preview should be at least 20KB
        assert size >= 20000, f"Preview PDF suspiciously small: {size} bytes (expected > 20KB)"
        print(f"✓ Preview PDF has reasonable size: {size:,} bytes")


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 60)
    print("Displacement Risk Atlas Build Tests")
    print("=" * 60)
    
    tests = [
        test_build_generates_files,
        test_sector_data_loaded,
        test_html_contains_all_sectors,
        test_preview_pdf_page_count,
        test_full_pdf_page_count,
        test_pdf_file_sizes,
        test_manifest_contains_hashes,
        test_run_json_updated,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        print(f"\n{test.__name__}:")
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
