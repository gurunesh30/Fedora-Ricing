#!/bin/bash
# Ghost of Tsushima - GDM Theme Builder
# Compiles the GNOME Shell gresource binary
# Run from the themes/ghost-of-tsushima/ directory

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GDM_DIR="${SCRIPT_DIR}/gdm"

echo "╔══════════════════════════════════════════╗"
echo "║  Ghost of Tsushima - GDM Theme Builder   ║"
echo "╚══════════════════════════════════════════╝"

# Check dependencies
if ! command -v glib-compile-resources &>/dev/null; then
    echo "Error: glib-compile-resources not found"
    echo "Install with: sudo dnf install glib2-devel"
    exit 1
fi

# Generate background if missing
if [[ ! -f "${GDM_DIR}/background.png" ]]; then
    echo "Generating GDM background..."
    python3 "${SCRIPT_DIR}/generate_gdm_bg.py"
fi

# Verify all referenced files exist
echo "Verifying theme files..."
cd "${GDM_DIR}"
missing=0
for f in gnome-shell-dark.css gnome-shell-light.css gnome-shell-high-contrast.css \
         calendar-today.svg calendar-today-light.svg gnome-shell-start.svg \
         pad-osd.css workspace-placeholder.svg background.png; do
    if [[ ! -f "$f" ]]; then
        echo "  MISSING: $f"
        missing=1
    fi
done

if [[ $missing -eq 1 ]]; then
    echo "Error: Missing required files. Ensure all assets are in ${GDM_DIR}"
    exit 1
fi

echo "All files present."

# Compile gresource
echo "Compiling gnome-shell-theme.gresource..."
glib-compile-resources gnome-shell-theme.gresource.xml

if [[ -f gnome-shell-theme.gresource ]]; then
    size=$(stat -c%s gnome-shell-theme.gresource 2>/dev/null || stat -f%z gnome-shell-theme.gresource)
    echo "Build successful! (${size} bytes)"
    echo ""
    echo "To install: sudo bash install-gdm.sh"
else
    echo "Error: Build failed"
    exit 1
fi
