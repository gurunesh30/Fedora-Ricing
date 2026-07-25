#!/usr/bin/env bash
# MSI Control Center — Install Script
set -e

INSTALL_DIR="$HOME/.config/hypr/msi-control-center"
DESKTOP_DIR="$HOME/.local/share/applications"

echo "=== MSI Control Center Installer ==="
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python: $PYTHON_VER"

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install --user --upgrade PySide6 psutil 2>/dev/null || {
    echo "pip3 install failed, trying pip..."
    pip install --user --upgrade PySide6 psutil
}

# Copy .desktop file
echo ""
echo "Registering application launcher..."
mkdir -p "$DESKTOP_DIR"
cp "$INSTALL_DIR/msi-control-center.desktop" "$DESKTOP_DIR/"
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

# Make executable
chmod +x "$INSTALL_DIR/main.py"

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Launch from:"
echo "  • Rofi/Wofi: Search 'MSI Control Center'"
echo "  • Terminal:   python3 $INSTALL_DIR/main.py"
echo ""
echo "For full MSI EC fan control, install the msi-ec kernel module:"
echo "  https://github.com/BeardOverflow/msi-ec"
