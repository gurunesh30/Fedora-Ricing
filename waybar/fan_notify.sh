#!/usr/bin/env bash
# fan_notify.sh — Show fan speed notification

FAN1=$(cat /sys/class/hwmon/hwmon4/fan1_input 2>/dev/null || echo 0)
FAN2=$(cat /sys/class/hwmon/hwmon4/fan2_input 2>/dev/null || echo 0)

notify-send -t 3000 "Fan Speeds" "CPU Fan: ${FAN1} RPM\nGPU Fan: ${FAN2} RPM"
