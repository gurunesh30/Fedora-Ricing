#!/usr/bin/env bash
# gpu_notify.sh — Show GPU info notification

GPU_TEMP=$(nvidia-settings -q GPUCoreTemp -t 2>/dev/null || echo "N/A")
GPU_UTIL=$(nvidia-settings -q GPUUtilization -t 2>/dev/null || echo "N/A")
GPU_MEM_USED=$(nvidia-settings -q UsedDedicatedGPUMemory -t 2>/dev/null || echo "?")
GPU_MEM_TOTAL=$(nvidia-settings -q TotalDedicatedGPUMemory -t 2>/dev/null || echo "?")

notify-send -t 5000 "NVIDIA RTX 3050 6GB" \
    "Temp: ${GPU_TEMP}°C\nUtil: ${GPU_UTIL}\nMemory: ${GPU_MEM_USED}/${GPU_MEM_TOTAL} MB"
