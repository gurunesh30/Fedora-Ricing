#!/usr/bin/env bash
# sys_info.sh — System info for MSI Cyborg A12U (Waybar custom module)

# CPU Temperature (coretemp for Intel)
CPU_TEMP="N/A"
for name_file in /sys/class/hwmon/hwmon*/name; do
    if [ -f "$name_file" ] && [ "$(cat "$name_file")" = "coretemp" ]; then
        DIR=$(dirname "$name_file")
        if [ -f "$DIR/temp1_input" ]; then
            CPU_TEMP=$(( $(cat "$DIR/temp1_input") / 1000 ))
        fi
        break
    fi
done

# CPU load (1 min average)
LOAD=$(awk '{printf "%d", $1 * 100}' /proc/loadavg 2>/dev/null)
LOAD=${LOAD:-0}

# FPS (monitor refresh rate)
FPS=$(hyprctl monitors 2>/dev/null | grep -oP '\d+(?:\.\d+)?(?=\s*Hz)' | head -1 | cut -d. -f1)
FPS=${FPS:-144}

# Color by CPU temp
if [ "$CPU_TEMP" != "N/A" ]; then
    if [ "$CPU_TEMP" -gt 80 ]; then
        CLASS="high"
    elif [ "$CPU_TEMP" -gt 60 ]; then
        CLASS="mid"
    else
        CLASS="low"
    fi
else
    CLASS="low"
fi

TEXT=" ${CPU_TEMP}°C 󰍹 ${FPS}Hz"

TOOLTIP="CPU: ${CPU_TEMP}°C (Package)\nLoad: ${LOAD}%\nRefresh Rate: ${FPS}Hz\nMemory: $(free -h | awk '/^Mem:/ {printf "%s / %s", $3, $2}')"

echo "{\"text\": \"$TEXT\", \"tooltip\": \"$TOOLTIP\", \"class\": \"$CLASS\"}"
