#!/usr/bin/env bash
#
# bundle_forge.sh - Create a minimal Forge deployment bundle
#
# This script creates a safe deployment bundle containing ONLY the public-facing
# Forge interface, preventing accidental publication of internal documentation.
#
# Output: site/ directory ready for static hosting (GitHub Pages, Netlify, etc.)
#
# Usage:
#   ./scripts/bundle_forge.sh [--output-dir DIR] [--include-api]
#
# Options:
#   --output-dir DIR    Output directory (default: site)
#   --include-api       Include api/ directory for Vercel serverless functions
#

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUTPUT_DIR="${REPO_ROOT}/site"
INCLUDE_API=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --include-api)
            INCLUDE_API=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--output-dir DIR] [--include-api]"
            echo ""
            echo "Create a minimal Forge deployment bundle."
            echo ""
            echo "Options:"
            echo "  --output-dir DIR    Output directory (default: site)"
            echo "  --include-api       Include api/ directory for Vercel"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

echo "=== Forge Bundle Script ==="
echo "Repository root: ${REPO_ROOT}"
echo "Output directory: ${OUTPUT_DIR}"
echo ""

# Validate we're in the right repo
if [[ ! -f "${REPO_ROOT}/forge/index.html" ]]; then
    echo "ERROR: forge/index.html not found. Are you in the right repository?" >&2
    exit 1
fi

# Safety check: ensure OUTPUT_DIR is within expected boundaries
# Prevent accidental deletion of critical directories
case "${OUTPUT_DIR}" in
    /|/home|/tmp|/var|/etc|/usr|/bin|/lib|/sbin)
        echo "ERROR: OUTPUT_DIR '${OUTPUT_DIR}' is a critical system directory. Refusing to proceed." >&2
        exit 1
        ;;
esac

# Ensure OUTPUT_DIR is either relative to REPO_ROOT or explicitly in a safe location
if [[ "${OUTPUT_DIR}" != "${REPO_ROOT}"/* && "${OUTPUT_DIR}" != /tmp/* ]]; then
    echo "ERROR: OUTPUT_DIR must be within the repository or /tmp/. Got: ${OUTPUT_DIR}" >&2
    exit 1
fi

# Clean output directory
if [[ -d "${OUTPUT_DIR}" ]]; then
    echo "Cleaning existing output directory..."
    rm -rf "${OUTPUT_DIR}"
fi

mkdir -p "${OUTPUT_DIR}"

# Copy Forge directory
echo "Copying forge/..."
cp -r "${REPO_ROOT}/forge" "${OUTPUT_DIR}/forge"

# Copy assets.json if it exists (needed for asset loading)
if [[ -f "${REPO_ROOT}/monetization/assets/assets.json" ]]; then
    echo "Copying monetization/assets/assets.json..."
    mkdir -p "${OUTPUT_DIR}/monetization/assets"
    cp "${REPO_ROOT}/monetization/assets/assets.json" "${OUTPUT_DIR}/monetization/assets/"
fi

# Optionally copy API directory for Vercel
if [[ "${INCLUDE_API}" == "true" ]]; then
    if [[ -d "${REPO_ROOT}/api" ]]; then
        echo "Copying api/..."
        cp -r "${REPO_ROOT}/api" "${OUTPUT_DIR}/api"
    else
        echo "WARNING: --include-api specified but api/ directory not found" >&2
    fi
fi

# Create a minimal index.html redirect at root
echo "Creating root index.html redirect..."
cat > "${OUTPUT_DIR}/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=forge/">
    <title>Redirecting...</title>
</head>
<body>
    <p>Redirecting to <a href="forge/">Forge</a>...</p>
</body>
</html>
EOF

# Create .nojekyll for GitHub Pages (prevents Jekyll processing)
touch "${OUTPUT_DIR}/.nojekyll"

# Verify the bundle
echo ""
echo "=== Bundle Contents ==="
find "${OUTPUT_DIR}" -type f | sort | while read -r file; do
    echo "  ${file#${OUTPUT_DIR}/}"
done

# Safety check: ensure no internal docs are included
echo ""
echo "=== Safety Verification ==="

# Check for directories that should NOT be in the bundle
UNSAFE_DIRS=(
    "docs"
    "analytics"
    "automation"
    "ops"
    "products"
    "scripts"
    ".github"
    ".git"
)

# Check for files at ROOT level that should NOT be in the bundle
# (forge/README.md is OK, but a root-level README.md is not)
UNSAFE_ROOT_FILES=(
    "LICENSE"
    "SECURITY.md"
    "pyproject.toml"
    "CODEOWNERS"
)

FOUND_UNSAFE=false

# Check for unsafe directories anywhere in the bundle
for dir in "${UNSAFE_DIRS[@]}"; do
    if find "${OUTPUT_DIR}" -type d -name "${dir}" 2>/dev/null | grep -v "^${OUTPUT_DIR}/forge/" | grep -q .; then
        echo "WARNING: Found internal directory: ${dir}" >&2
        FOUND_UNSAFE=true
    fi
done

# Check for unsafe files at the root level only (not inside forge/)
for file in "${UNSAFE_ROOT_FILES[@]}"; do
    if [[ -f "${OUTPUT_DIR}/${file}" ]]; then
        echo "WARNING: Found internal file at root: ${file}" >&2
        FOUND_UNSAFE=true
    fi
done

# Check for root-level README.md (forge/README.md is OK)
if [[ -f "${OUTPUT_DIR}/README.md" ]]; then
    echo "WARNING: Found root README.md (internal documentation)" >&2
    FOUND_UNSAFE=true
fi

if [[ "${FOUND_UNSAFE}" == "true" ]]; then
    echo ""
    echo "ERROR: Internal documentation found in bundle. Review the contents above." >&2
    exit 1
fi

echo "✓ No internal documentation detected in bundle."

# Summary
echo ""
echo "=== Bundle Complete ==="
echo "Output: ${OUTPUT_DIR}"
echo ""
echo "Deployment options:"
echo "  GitHub Pages: Push ${OUTPUT_DIR}/ to gh-pages branch or configure Pages to serve from site/"
echo "  Netlify:      Set publish directory to 'site'"
echo "  Vercel:       Use --include-api flag and deploy site/ as root"
echo ""
echo "To test locally:"
echo "  cd ${OUTPUT_DIR} && python -m http.server 8000"
echo "  Open http://localhost:8000/"
