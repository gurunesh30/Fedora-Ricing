#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Ghost of Tsushima - Uninstaller
# Restores original Plymouth and GDM themes
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${SCRIPT_DIR}/backup"
PLYMOUTH_THEME="ghost-tsushima"

RED='\033[0;31m'
GOLD='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GOLD}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║    Ghost of Tsushima - Theme Uninstaller            ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}Error: This script must be run as root (sudo)${NC}"
    exit 1
fi

# ── Restore Plymouth ─────────────────────────────────────────

echo -e "${GOLD}[1/3] Restoring Plymouth theme...${NC}"

if [[ -f "${BACKUP_DIR}/plymouth-theme.plymouth.bak" ]]; then
    # Extract original theme name from backup
    ORIGINAL_NAME=$(grep "^Name=" "${BACKUP_DIR}/plymouth-theme.plymouth.bak" | cut -d= -f2 | tr ' ' '_' | tr '[:upper:]' '[:lower:]')

    # Try to find and restore the original theme
    if [[ -d "/usr/share/plymouth/themes/${ORIGINAL_NAME}" ]]; then
        plymouth-set-default-theme "${ORIGINAL_NAME}"
        echo -e "  ${GREEN}Restored Plymouth theme: ${ORIGINAL_NAME}${NC}"
    else
        # Fall back to spinner (Fedora default)
        plymouth-set-default-theme spinner
        echo -e "  ${GREEN}Restored default Plymouth theme (spinner)${NC}"
    fi
else
    # No backup, use default
    plymouth-set-default-theme spinner
    echo -e "  ${GREEN}Set Plymouth to default (spinner)${NC}"
fi

# Remove Ghost Tsushima Plymouth theme
rm -rf "/usr/share/plymouth/themes/${PLYMOUTH_THEME}"
echo "  Removed Ghost Tsushima Plymouth files"

# ── Restore GDM ──────────────────────────────────────────────

echo -e "${GOLD}[2/3] Restoring GDM theme...${NC}"

GDM_RESOURCE="/usr/share/gnome-shell/gnome-shell-theme.gresource"

if [[ -f "${BACKUP_DIR}/gnome-shell-theme.gresource.bak" ]]; then
    cp "${BACKUP_DIR}/gnome-shell-theme.gresource.bak" "${GDM_RESOURCE}"
    echo -e "  ${GREEN}Restored original GDM theme${NC}"
else
    echo -e "  ${RED}No GDM backup found. You may need to reinstall gnome-shell:${NC}"
    echo "    sudo dnf reinstall gnome-shell"
fi

# ── Rebuild initramfs ────────────────────────────────────────

echo -e "${GOLD}[3/3] Rebuilding initramfs...${NC}"
dracut -f
echo -e "  ${GREEN}initramfs rebuilt${NC}"

# ── Done ─────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}Uninstall complete!${NC}"
echo "  Reboot to see the restored themes."
echo ""
echo "  To reinstall Ghost of Tsushima theme:"
echo "    sudo bash ${SCRIPT_DIR}/install.sh"
