#!/usr/bin/env bash
# msi_fan_mode.sh — Toggle MSI fan modes (requires msi-ec kernel module)
# Usage: ./msi_fan_mode.sh [auto|silent|cool|boost]
# If no argument, cycles through modes.

MSI_EC_DIR="/sys/devices/platform/msi-ec"

if [ ! -d "$MSI_EC_DIR" ]; then
    notify-send -u critical "MSI EC Not Found" \
        "msi-ec module not loaded. Run: sudo modprobe msi-ec"
    exit 1
fi

FAN_MODE_FILE="$MSI_EC_DIR/fan_mode"
COOLER_BOOST_FILE="$MSI_EC_DIR/cooler_boost"

if [ ! -f "$FAN_MODE_FILE" ]; then
    notify-send -u critical "Fan Control Unavailable" \
        "Your kernel doesn't support MSI fan control via this interface."
    exit 1
fi

CURRENT=$(cat "$FAN_MODE_FILE")
MODE=${1:-}

if [ -z "$MODE" ]; then
    # Cycle through modes
    case "$CURRENT" in
        auto)      MODE="silent" ;;
        silent)    MODE="cool" ;;
        cool)      MODE="boost" ;;
        boost)     MODE="auto" ;;
        *)         MODE="auto" ;;
    esac
fi

# Validate mode
if [ "$MODE" != "auto" ] && [ "$MODE" != "silent" ] && [ "$MODE" != "cool" ] && [ "$MODE" != "boost" ]; then
    notify-send -u critical "Invalid Fan Mode" "Valid: auto, silent, cool, boost"
    exit 1
fi

# Apply
echo "$MODE" | sudo tee "$FAN_MODE_FILE" &>/dev/null

if [ $? -eq 0 ]; then
    case "$MODE" in
        auto)   ICON="󰾅" ;;
        silent) ICON="" ;;
        cool)   ICON="❄" ;;
        boost)  ICON="" ;;
    esac
    notify-send -t 3000 "Fan Mode: ${MODE^}" "${ICON} Fan mode set to ${MODE}"
else
    notify-send -u critical "Permission Denied" \
        "Run: echo '$MODE' | sudo tee $FAN_MODE_FILE"
fi
