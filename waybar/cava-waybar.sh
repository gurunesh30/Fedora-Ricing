#!/usr/bin/env bash
# cava-waybar.sh — Cava audio visualizer for Waybar (continuous)

CAVA_PID_FILE="/tmp/cava-daemon.pid"
CAVA_OUT="/tmp/cava-bars.dat"
CAVA_CONFIG="/tmp/cava-waybar-config"

start_daemon() {
    SINK=$(pactl get-default-sink 2>/dev/null)
    MONITOR="${SINK}.monitor"
    cat > "$CAVA_CONFIG" <<EOF
[general]
bars = 8
framerate = 60
autosens = 1
[input]
method = pulse
source = ${MONITOR:-auto}
[output]
method = raw
raw_target = /dev/stdout
data_format = ascii
ascii_max_range = 8
bar_delimiter = 59
frame_delimiter = 10
EOF
    (cava -p "$CAVA_CONFIG" > "$CAVA_OUT" 2>/dev/null; rm -f "$CAVA_PID_FILE") &
    echo $! > "$CAVA_PID_FILE"
    sleep 0.8
}

if [ ! -f "$CAVA_PID_FILE" ] || ! kill -0 $(cat "$CAVA_PID_FILE") 2>/dev/null; then
    rm -f "$CAVA_OUT"
    start_daemon
fi

chars=(▁ ▂ ▃ ▄ ▅ ▆ ▇ █)

while true; do
    LINE=$(tail -1 "$CAVA_OUT" 2>/dev/null)
    LINE="${LINE%;}"

    if [ -n "$LINE" ]; then
        IFS=';' read -r -a bars <<< "$LINE"
        out=""
        for v in "${bars[@]}"; do
            v="${v//[^0-9]/}"
            [ -z "$v" ] && v=0
            idx=$(( v > 7 ? 7 : v ))
            out="${out}${chars[idx]}"
        done
        printf '{"text":"%s","tooltip":"Audio Visualizer"}\n' "$out"
    else
        printf '{"text":"▁▁▁▁▁▁▁▁","tooltip":"Audio Visualizer"}\n'
    fi

    sleep 0.1
done
