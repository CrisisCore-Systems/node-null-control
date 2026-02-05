#!/usr/bin/env python3
"""Tests for Vercel deployment configuration and static files."""

import json
from pathlib import Path


def test_public_preview_pdf_exists():
    """Verify that the preview PDF exists in the public directory."""
    repo_root = Path(__file__).parent.parent
    pdf_path = repo_root / "public" / "preview" / "displacement_risk_atlas_preview.pdf"

    assert pdf_path.exists(), f"Preview PDF not found at {pdf_path}"
    assert pdf_path.is_file(), f"Preview PDF path is not a file: {pdf_path}"

    # Check file size (should be around 44KB)
    file_size = pdf_path.stat().st_size
    assert file_size > 40_000, f"Preview PDF seems too small: {file_size} bytes"
    assert file_size < 100_000, f"Preview PDF seems too large: {file_size} bytes"

    print(f"✓ Preview PDF exists at {pdf_path} ({file_size:,} bytes)")


def test_vercel_json_valid():
    """Verify that vercel.json is valid JSON and has the preview headers."""
    repo_root = Path(__file__).parent.parent
    vercel_json_path = repo_root / "vercel.json"

    with open(vercel_json_path) as f:
        config = json.load(f)

    # Check that headers section exists
    assert "headers" in config, "vercel.json missing 'headers' section"

    # Find the /preview/(.*) header rule
    preview_rule = None
    for header_rule in config["headers"]:
        if header_rule.get("source") == "/preview/(.*)":
            preview_rule = header_rule
            break

    assert preview_rule is not None, "vercel.json missing /preview/(.*) header rule"

    # Verify expected headers
    headers = {h["key"]: h["value"] for h in preview_rule["headers"]}
    assert "Cache-Control" in headers, "Missing Cache-Control header for /preview/"
    assert "Content-Type" in headers, "Missing Content-Type header for /preview/"
    assert headers["Content-Type"] == "application/pdf", "Wrong Content-Type for /preview/"

    print("✓ vercel.json is valid and has correct preview headers")


def test_kit_form_has_redirect():
    """Verify that the Kit form in forge/index.html has the redirect URL."""
    repo_root = Path(__file__).parent.parent
    html_path = repo_root / "forge" / "index.html"

    with open(html_path) as f:
        content = f.read()

    # Check for the redirect URL in the data-options attribute
    assert "data-options" in content, "Kit form missing data-options attribute"
    assert "after_subscribe" in content, "Kit form missing after_subscribe configuration"
    assert '"action":"redirect"' in content, "Kit form not set to redirect action"
    assert "displacement_risk_atlas_preview.pdf" in content, "Kit form missing PDF redirect URL"
    assert "ghost-network-interface.vercel.app" in content, "Kit form missing Vercel domain"

    print("✓ Kit form has redirect URL configured")


if __name__ == "__main__":
    test_public_preview_pdf_exists()
    test_vercel_json_valid()
    test_kit_form_has_redirect()
    print("\n✓ All deployment tests passed!")
