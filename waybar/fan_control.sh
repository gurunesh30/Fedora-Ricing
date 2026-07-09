#!/usr/bin/env bash
# fan_control.sh — MSI Cyborg A12U fan monitor (Waybar custom module)
# For fan speed control, install msi-ec module: sudo modprobe msi-ec

FAN1=0
FAN2=0
FAN3=0
FAN4=0

for name_file in /sys/class/hwmon/hwmon*/name; do
    if [ -f "$name_file" ] && [ "$(cat "$name_file")" = "msi_wmi_platform" ]; then
        DIR=$(dirname "$name_file")
        FAN1=$(cat "$DIR/fan1_input" 2>/dev/null || echo 0)
        FAN2=$(cat "$DIR/fan2_input" 2>/dev/null || echo 0)
        FAN3=$(cat "$DIR/fan3_input" 2>/dev/null || echo 0)
        FAN4=$(cat "$DIR/fan4_input" 2>/dev/null || echo 0)
        break
    fi
done

if [ "$FAN1" -gt 0 ] 2>/dev/null || [ "$FAN2" -gt 0 ] 2>/dev/null; then
    TEXT="󰈐 ${FAN1} ${FAN2}"
else
    TEXT="󰈐 0 0"
fi

TOOLTIP="Fan 1 (CPU): ${FAN1} RPM\nFan 2 (GPU): ${FAN2} RPM\nFan 3: ${FAN3} RPM\nFan 4: ${FAN4} RPM"

echo "{\"text\": \"$TEXT\", \"tooltip\": \"$TOOLTIP\"}"
