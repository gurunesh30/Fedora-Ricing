#!/bin/bash
# Ghost of Tsushima - Plymouth Theme Installer
# Run as root (sudo bash install-plymouth.sh)

set -euo pipefail

THEME_NAME="ghost-tsushima"
THEME_DIR="/usr/share/plymouth/themes/${THEME_NAME}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔══════════════════════════════════════════╗"
echo "║  Ghost of Tsushima - Plymouth Installer  ║"
echo "╚══════════════════════════════════════════╝"

# Check root
if [[ $EUID -ne 0 ]]; then
    echo "Error: This script must be run as root (sudo)"
    exit 1
fi

# Check assets exist
if [[ ! -f "${SCRIPT_DIR}/ghost-tsushima.plymouth" ]]; then
    echo "Error: ghost-tsushima.plymouth not found in ${SCRIPT_DIR}"
    exit 1
fi

if [[ ! -f "${SCRIPT_DIR}/ghost-tsushima.script" ]]; then
    echo "Error: ghost-tsushima.script not found in ${SCRIPT_DIR}"
    exit 1
fi

if [[ ! -d "${SCRIPT_DIR}/assets" ]]; then
    echo "Error: assets directory not found in ${SCRIPT_DIR}"
    echo "Run generate_assets.py first to create the animation frames"
    exit 1
fi

# Generate assets if missing
if [[ ! -f "${SCRIPT_DIR}/assets/background.png" ]]; then
    echo "Generating assets..."
    python3 "${SCRIPT_DIR}/generate_assets.py"
fi

# Backup current theme
CURRENT_THEME=$(plymouth-set-default-theme 2>/dev/null || echo "none")
echo "Current Plymouth theme: ${CURRENT_THEME}"

if [[ "${CURRENT_THEME}" != "none" && -f "/usr/share/plymouth/themes/${CURRENT_THEME}/${CURRENT_THEME}.plymouth" ]]; then
    echo "Backing up current theme..."
    cp "/usr/share/plymouth/themes/${CURRENT_THEME}/${CURRENT_THEME}.plymouth" \
       "/usr/share/plymouth/themes/${CURRENT_THEME}/${CURRENT_THEME}.plymouth.bak" 2>/dev/null || true
fi

# Create theme directory
echo "Installing theme to ${THEME_DIR}..."
mkdir -p "${THEME_DIR}/assets"

# Copy theme files
cp "${SCRIPT_DIR}/ghost-tsushima.plymouth" "${THEME_DIR}/"
cp "${SCRIPT_DIR}/ghost-tsushima.script" "${THEME_DIR}/"
cp "${SCRIPT_DIR}/assets/"*.png "${THEME_DIR}/assets/"

# Fix paths in .plymouth file (use installed path)
sed -i "s|ScriptFile=.*|ScriptFile=${THEME_DIR}/ghost-tsushima.script|" "${THEME_DIR}/ghost-tsushima.plymouth"
sed -i "s|ImageDir=.*|ImageDir=${THEME_DIR}/assets|" "${THEME_DIR}/ghost-tsushima.plymouth"

# Set as default theme and rebuild initramfs
echo "Setting ${THEME_NAME} as default Plymouth theme..."
plymouth-set-default-theme "${THEME_NAME}"

echo "Rebuilding initramfs (this may take a moment)..."
dracut -f

# Verify
echo ""
echo "Verification:"
plymouth-set-default-theme -l | grep "${THEME_NAME}" && echo "  Theme registered" || echo "  WARNING: Theme not found in list"

echo ""
echo "Installation complete!"
echo "Reboot to see the Ghost of Tsushima boot animation."
echo ""
echo "To test without rebooting:"
echo "  sudo plymouthd --mode=boot"
echo "  sudo plymouth --show-splash"
echo "  sudo plymouth quit"
echo "  sudo killall plymouthd"
