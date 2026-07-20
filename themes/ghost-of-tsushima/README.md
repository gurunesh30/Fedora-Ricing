# Ghost of Tsushima - Fedora Theme

Custom animated boot screen and login screen inspired by Ghost of Tsushima's wind & leaves aesthetic.

## Preview

**Boot Screen (Plymouth):**
- Falling golden leaves with wind-swept sine-wave drift
- Horizontal wind particle streaks
- Ghost mask logo with pulse animation
- Misty mountain backdrop with atmospheric fog

**Login Screen (GDM):**
- Dramatic mountain landscape with golden pampas grass
- Falling leaf particles
- Animated gold-glow clock
- User list with wind-sweep hover animations
- Password entry with animated gold border glow

## Requirements

- Fedora (tested on Fedora 44)
- Plymouth with script module support
- GNOME Shell 50+ / GDM 50+
- `glib2-devel` (for `glib-compile-resources`)
- Python 3 + Pillow (for asset generation)

## Quick Install

```bash
cd themes/ghost-of-tsushima/
sudo bash install.sh
reboot
```

## Manual Install

### Plymouth Boot Theme

```bash
# Generate assets
python3 plymouth/generate_assets.py

# Install
sudo cp -r plymouth/ /usr/share/plymouth/themes/ghost-tsushima/
sudo plymouth-set-default-theme -R ghost-tsushima
```

### GDM Login Screen Theme

```bash
# Generate background
python3 generate_gdm_bg.py

# Build gresource
cd gdm/
glib-compile-resources gnome-shell-theme.gresource.xml

# Install (backup first!)
sudo cp /usr/share/gnome-shell/gnome-shell-theme.gresource \
        /usr/share/gnome-shell/gnome-shell-theme.gresource.bak
sudo cp gnome-shell-theme.gresource \
        /usr/share/gnome-shell/gnome-shell-theme.gresource

# Restart GDM (logs you out!)
sudo systemctl restart gdm
```

## Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Near Black | `#0a0a0a` | Background base |
| Dark Charcoal | `#1a1a1a` | Dialog backgrounds |
| Gold | `#c8a964` | Accents, focus borders, clock |
| Deep Red | `#8b1a1a` | Action buttons, highlights |
| White | `#fafafb` | Text, clock, labels |

## Animations

### Plymouth (Boot)
| Animation | Description |
|-----------|-------------|
| Leaf drift | 20 leaf sprites with sine-wave horizontal sway |
| Wind streaks | Horizontal particle streaks |
| Logo pulse | Ghost mask fades in and pulses |
| Mist opacity | Atmospheric fog oscillation |

### GDM (Login)
| Animation | Duration | Description |
|-----------|----------|-------------|
| `ghostClockGlow` | 4s | Pulsing gold text-shadow on clock |
| `ghostFadeInUp` | 0.6s | Login dialog entrance (slide up + fade) |
| `ghostWindSweep` | 8-10s | Subtle horizontal drift on user items |
| `ghostFocusGlow` | 2s | Gold border glow on password entry |
| `ghostMistDrift` | 30s | Slow background-position parallax |
| `ghostSlideInRight` | 0.5s | "Not listed?" button entrance |

## File Structure

```
ghost-of-tsushima/
├── install.sh                  # Master installer
├── uninstall.sh                # Rollback script
├── build-gdm.sh               # GDM gresource builder
├── generate_gdm_bg.py         # GDM background generator
├── plymouth/
│   ├── ghost-tsushima.plymouth
│   ├── ghost-tsushima.script
│   ├── generate_assets.py
│   ├── install-plymouth.sh
│   └── assets/
│       ├── background.png
│       ├── logo.png
│       ├── leaf-001.png ... leaf-012.png
│       └── wind-particle-001.png ... wind-particle-008.png
├── gdm/
│   ├── gnome-shell-theme.gresource.xml
│   ├── gnome-shell-dark.css
│   ├── gnome-shell-light.css
│   ├── gnome-shell-high-contrast.css
│   ├── background.png
│   └── [original SVG assets]
└── backup/                     # Created by installer
```

## Uninstall

```bash
sudo bash uninstall.sh
reboot
```

## Recovery

If GDM breaks and you can't log in:

1. Switch to TTY: `Ctrl+Alt+F3`
2. Log in as root
3. Restore backup:
   ```bash
   sudo cp /path/to/backup/gnome-shell-theme.gresource.bak \
           /usr/share/gnome-shell/gnome-shell-theme.gresource
   sudo systemctl restart gdm
   ```

## Notes

- GNOME Shell updates will overwrite the GDM gresource. Re-run the installer after updates.
- The Plymouth theme persists across kernel updates (dracut rebuilds handle it).
- All images are procedurally generated - no external assets needed.

## Credits

Inspired by [Ghost of Tsushima](https://www.playstation.com/en-us/games/ghost-of-tsushima/) by Sucker Punch Productions.
