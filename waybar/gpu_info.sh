#!/usr/bin/env bash
# gpu_info.sh — Dedicated GPU monitor for MSI Cyborg A12U (Waybar custom module)

GPU_TEMP="N/A"
GPU_UTIL="N/A"
GPU_MEM_USED="N/A"
GPU_MEM_TOTAL="N/A"
GPU_CLOCK="N/A"

if command -v nvidia-settings &>/dev/null; then
    GT=$(nvidia-settings -q GPUCoreTemp -t 2>/dev/null)
    [ -n "$GT" ] && GPU_TEMP="$GT"

    GU=$(nvidia-settings -q GPUUtilization -t 2>/dev/null)
    if [ -n "$GU" ]; then
        GPU_UTIL=$(echo "$GU" | grep -oP 'graphics=\K\d+')
        GPU_UTIL=${GPU_UTIL:-0}
    fi

    GMU=$(nvidia-settings -q UsedDedicatedGPUMemory -t 2>/dev/null)
    GMT=$(nvidia-settings -q TotalDedicatedGPUMemory -t 2>/dev/null)
    [ -n "$GMU" ] && GPU_MEM_USED="$GMU"
    [ -n "$GMT" ] && GPU_MEM_TOTAL="$GMT"

    GC=$(nvidia-settings -q GPUCurrentClockFreqs -t 2>/dev/null | head -1)
    [ -n "$GC" ] && GPU_CLOCK="$GC"
fi

# Color by utilization
if [ "$GPU_UTIL" != "N/A" ]; then
    if [ "$GPU_UTIL" -gt 80 ]; then
        CLASS="high"
    elif [ "$GPU_UTIL" -gt 40 ]; then
        CLASS="mid"
    else
        CLASS="low"
    fi
else
    CLASS="low"
fi

if [ "$GPU_UTIL" != "N/A" ] && [ "$GPU_UTIL" -gt 0 ] 2>/dev/null; then
    TEXT="󰢮 ${GPU_TEMP}°C ${GPU_UTIL}%"
else
    TEXT="󰢮 ${GPU_TEMP}°C"
fi

TOOLTIP="GPU (RTX 3050 6GB)\nTemp: ${GPU_TEMP}°C\nUtil: ${GPU_UTIL}%\nMemory: ${GPU_MEM_USED} / ${GPU_MEM_TOTAL} MB\nClock: ${GPU_CLOCK} MHz"

echo "{\"text\": \"$TEXT\", \"tooltip\": \"$TOOLTIP\", \"class\": \"$CLASS\"}"
