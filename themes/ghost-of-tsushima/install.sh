#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# Ghost of Tsushima - Master Installer
# Installs both Plymouth boot theme and GDM login screen theme
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
echo "║     Ghost of Tsushima - Fedora Theme Installer      ║"
echo "║     Wind & Leaves - Boot + Login Screen             ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ── Pre-flight checks ────────────────────────────────────────

if [[ $EUID -ne 0 ]]; then
    echo -e "${RED}Error: This script must be run as root (sudo)${NC}"
    exit 1
fi

if ! command -v plymouth-set-default-theme &>/dev/null; then
    echo -e "${RED}Error: Plymouth not found${NC}"
    exit 1
fi

if ! command -v glib-compile-resources &>/dev/null; then
    echo -e "${RED}Error: glib-compile-resources not found${NC}"
    echo "Install with: sudo dnf install glib2-devel"
    exit 1
fi

# ── Create backup directory ──────────────────────────────────

mkdir -p "${BACKUP_DIR}"

# ═══════════════════════════════════════════════════════════════
# PART 1: Plymouth Boot Theme
# ═══════════════════════════════════════════════════════════════

echo -e "${GOLD}[1/4] Installing Plymouth boot theme...${NC}"

# Generate assets if needed
if [[ ! -f "${SCRIPT_DIR}/plymouth/assets/background.png" ]]; then
    echo "  Generating Plymouth assets..."
    python3 "${SCRIPT_DIR}/plymouth/generate_assets.py"
fi

# Backup current Plymouth theme
CURRENT_PLYMOUTH=$(plymouth-set-default-theme 2>/dev/null || echo "none")
echo "  Current theme: ${CURRENT_PLYMOUTH}"

if [[ "${CURRENT_PLYMOUTH}" != "none" ]]; then
    PLYMOUTH_CONF="/usr/share/plymouth/themes/${CURRENT_PLYMOUTH}/${CURRENT_PLYMOUTH}.plymouth"
    if [[ -f "${PLYMOUTH_CONF}" ]]; then
        cp "${PLYMOUTH_CONF}" "${BACKUP_DIR}/plymouth-theme.plymouth.bak"
        echo "  Backed up current Plymouth theme"
    fi
fi

# Install Plymouth theme
PLYMOUTH_DEST="/usr/share/plymouth/themes/${PLYMOUTH_THEME}"
mkdir -p "${PLYMOUTH_DEST}/assets"
cp "${SCRIPT_DIR}/plymouth/ghost-tsushima.plymouth" "${PLYMOUTH_DEST}/"
cp "${SCRIPT_DIR}/plymouth/ghost-tsushima.script" "${PLYMOUTH_DEST}/"
cp "${SCRIPT_DIR}/plymouth/assets/"*.png "${PLYMOUTH_DEST}/assets/"

# Fix paths in .plymouth
sed -i "s|ScriptFile=.*|ScriptFile=${PLYMOUTH_DEST}/ghost-tsushima.script|" "${PLYMOUTH_DEST}/ghost-tsushima.plymouth"
sed -i "s|ImageDir=.*|ImageDir=${PLYMOUTH_DEST}/assets|" "${PLYMOUTH_DEST}/ghost-tsushima.plymouth"

plymouth-set-default-theme "${PLYMOUTH_THEME}"
echo -e "  ${GREEN}Plymouth theme installed${NC}"

# ═══════════════════════════════════════════════════════════════
# PART 2: GDM Login Screen Theme
# ═══════════════════════════════════════════════════════════════

echo -e "${GOLD}[2/4] Installing GDM login screen theme...${NC}"

# Generate GDM background if needed
if [[ ! -f "${SCRIPT_DIR}/gdm/background.png" ]]; then
    echo "  Generating GDM background..."
    python3 "${SCRIPT_DIR}/generate_gdm_bg.py"
fi

# Backup original GDM gresource
GDM_RESOURCE="/usr/share/gnome-shell/gnome-shell-theme.gresource"
if [[ -f "${GDM_RESOURCE}" ]]; then
    cp "${GDM_RESOURCE}" "${BACKUP_DIR}/gnome-shell-theme.gresource.bak"
    echo "  Backed up original GDM theme"
fi

# Build gresource
echo "  Compiling GDM gresource..."
cd "${SCRIPT_DIR}/gdm"
glib-compile-resources gnome-shell-theme.gresource.xml

if [[ ! -f gnome-shell-theme.gresource ]]; then
    echo -e "  ${RED}Error: GDM gresource compilation failed${NC}"
    exit 1
fi

# Install (cp, not mv, to preserve SELinux contexts)
cp "${SCRIPT_DIR}/gdm/gnome-shell-theme.gresource" "${GDM_RESOURCE}"
echo -e "  ${GREEN}GDM theme installed${NC}"

# ═══════════════════════════════════════════════════════════════
# PART 3: Rebuild initramfs
# ═══════════════════════════════════════════════════════════════

echo -e "${GOLD}[3/4] Rebuilding initramfs...${NC}"
dracut -f
echo -e "  ${GREEN}initramfs rebuilt${NC}"

# ═══════════════════════════════════════════════════════════════
# PART 4: Verification
# ═══════════════════════════════════════════════════════════════

echo -e "${GOLD}[4/4] Verifying installation...${NC}"

# Verify Plymouth
INSTALLED_PLYMOUTH=$(plymouth-set-default-theme 2>/dev/null || echo "error")
if [[ "${INSTALLED_PLYMOUTH}" == "${PLYMOUTH_THEME}" ]]; then
    echo -e "  ${GREEN}Plymouth theme: OK (${INSTALLED_PLYMOUTH})${NC}"
else
    echo -e "  ${RED}Plymouth theme: FAILED (got ${INSTALLED_PLYMOUTH})${NC}"
fi

# Verify GDM
if [[ -f "${GDM_RESOURCE}" ]]; then
    GDM_SIZE=$(stat -c%s "${GDM_RESOURCE}" 2>/dev/null || stat -f%z "${GDM_RESOURCE}")
    echo -e "  ${GREEN}GDM theme: OK (${GDM_SIZE} bytes)${NC}"
else
    echo -e "  ${RED}GDM theme: FAILED (file not found)${NC}"
fi

# ═══════════════════════════════════════════════════════════════
# Done
# ═══════════════════════════════════════════════════════════════

echo ""
echo -e "${GOLD}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GOLD}║          Installation Complete!                      ║${NC}"
echo -e "${GOLD}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo "  Reboot to see the Ghost of Tsushima boot animation"
echo "  and login screen theme."
echo ""
echo "  Backups saved to: ${BACKUP_DIR}"
echo "  To uninstall: sudo bash ${SCRIPT_DIR}/uninstall.sh"
echo ""
echo "  Test Plymouth without rebooting:"
echo "    sudo plymouthd --mode=boot"
echo "    sudo plymouth --show-splash"
echo "    sleep 5"
echo "    sudo plymouth quit"
echo "    sudo killall plymouthd"
echo ""
echo "  Recovery (if login breaks):"
echo "    Ctrl+Alt+F3 → sudo bash ${SCRIPT_DIR}/uninstall.sh"
