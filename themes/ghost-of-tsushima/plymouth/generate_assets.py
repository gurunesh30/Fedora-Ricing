#!/usr/bin/env python3
"""
Ghost of Tsushima - Plymouth Asset Generator
Generates all PNG animation frames for the boot theme.
Requires: Pillow (pip install Pillow)
"""

import math
import random
import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# Theme colors
NEAR_BLACK = (10, 10, 10, 255)
DARK_CHARCOAL = (20, 20, 20, 255)
GOLD = (200, 169, 100, 255)
GOLD_DIM = (160, 130, 70, 200)
GOLD_FAINT = (120, 100, 60, 120)
DEEP_RED = (139, 26, 26, 255)
WHITE = (250, 250, 251, 255)
LEAF_COLORS = [
    (180, 140, 60, 220),   # Golden brown
    (160, 120, 50, 200),   # Dark gold
    (140, 100, 40, 180),   # Deep amber
    (200, 160, 70, 210),   # Bright gold
    (120, 85, 35, 190),    # Shadow gold
    (170, 130, 55, 200),   # Mid gold
]


def create_background():
    """Create the misty mountain backdrop (1920x1080)."""
    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), NEAR_BLACK)
    draw = ImageDraw.Draw(img)

    # Gradient sky (dark to slightly lighter)
    for y in range(h):
        t = y / h
        r = int(10 + 15 * (1 - t))
        g = int(10 + 12 * (1 - t))
        b = int(10 + 18 * (1 - t))
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Mountain silhouettes (3 layers)
    mountains = [
        {"base_y": 700, "peaks": [(200, 350), (500, 280), (800, 320), (1100, 260), (1400, 300), (1700, 340)], "color": (18, 18, 22)},
        {"base_y": 750, "peaks": [(100, 420), (400, 380), (700, 400), (1000, 360), (1300, 390), (1600, 410), (1900, 380)], "color": (22, 22, 28)},
        {"base_y": 800, "peaks": [(150, 500), (350, 470), (600, 490), (850, 460), (1150, 480), (1450, 470), (1750, 490)], "color": (28, 28, 35)},
    ]

    for mtn in mountains:
        points = [(0, h)]
        for i, (px, py) in enumerate(mtn["peaks"]):
            points.append((px, py))
        points.append((w, h))
        draw.polygon(points, fill=mtn["color"])

    # Mist layers
    mist = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    mist_draw = ImageDraw.Draw(mist)
    for _ in range(40):
        mx = random.randint(0, w)
        my = random.randint(400, 800)
        mw = random.randint(200, 600)
        mh = random.randint(20, 60)
        alpha = random.randint(5, 20)
        mist_draw.ellipse([mx, my, mx + mw, my + mh], fill=(180, 180, 200, alpha))

    img = Image.alpha_composite(img, mist)

    # Subtle gold light rays from upper right
    rays = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ray_draw = ImageDraw.Draw(rays)
    for angle in range(-30, 10, 3):
        rad = math.radians(angle)
        x1, y1 = w - 100, 50
        x2 = x1 + int(math.cos(rad) * 1200)
        y2 = y1 + int(math.sin(rad) * 1200)
        ray_draw.line([(x1, y1), (x2, y2)], fill=(200, 170, 100, 6), width=8)

    img = Image.alpha_composite(img, rays)
    img.save(os.path.join(ASSETS_DIR, "background.png"))
    print("  Created background.png")


def create_leaf_frame(frame_idx, total_frames):
    """Create a single leaf animation frame."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    color = LEAF_COLORS[frame_idx % len(LEAF_COLORS)]
    # Rotation angle for this frame
    angle = (frame_idx / total_frames) * 360
    rad = math.radians(angle)

    # Leaf shape - elongated ellipse with stem
    cx, cy = size // 2, size // 2
    leaf_len = 22
    leaf_w = 8

    # Compute rotated leaf points
    points = []
    for t in range(0, 361, 15):
        tr = math.radians(t)
        # Leaf outline (heart-like shape)
        r = leaf_len * (1 - 0.3 * math.sin(tr)) * (0.5 + 0.5 * math.cos(tr))
        x = r * math.cos(tr)
        y = (r * 0.4) * math.sin(tr)
        # Rotate
        rx = x * math.cos(rad) - y * math.sin(rad)
        ry = x * math.sin(rad) + y * math.cos(rad)
        points.append((int(cx + rx), int(cy + ry)))

    if len(points) >= 3:
        draw.polygon(points, fill=color)

    # Stem line
    stem_x = cx + int(10 * math.cos(rad))
    stem_y = cy + int(10 * math.sin(rad))
    draw.line([(cx, cy), (stem_x, stem_y)], fill=(100, 80, 40, 180), width=1)

    # Vein line
    vx = cx - int(8 * math.cos(rad))
    vy = cy - int(8 * math.sin(rad))
    draw.line([(cx, cy), (vx, vy)], fill=(color[0] - 30, color[1] - 30, color[2] - 20, 150), width=1)

    return img


def create_wind_frame(frame_idx, total_frames):
    """Create a wind particle/streak frame."""
    w, h = 128, 32
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Wind streak - multiple thin horizontal lines with varying opacity
    phase = frame_idx / total_frames
    for i in range(5):
        y = 4 + i * 6
        x_offset = int(20 * math.sin(phase * math.pi * 2 + i * 0.5))
        length = 40 + int(30 * math.sin(phase * math.pi + i))
        alpha = int(60 + 40 * math.sin(phase * math.pi * 2 + i))
        x_start = 10 + x_offset
        x_end = x_start + length

        draw.line(
            [(x_start, y), (x_end, y)],
            fill=(200, 190, 170, alpha),
            width=1
        )

    # Subtle glow dots along streaks
    for i in range(3):
        y = 8 + i * 8
        x = 30 + int(40 * (frame_idx / total_frames))
        draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(220, 200, 160, 40))

    return img


def create_logo():
    """Create the Ghost mask logo watermark."""
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2

    # Ghost mask - stylized face shape
    # Outer mask shape (rounded triangle)
    mask_points = []
    for t in range(0, 360, 5):
        rad = math.radians(t - 90)
        # Modified circle to make a mask shape
        r = 80 + 20 * math.cos(2 * rad) + 10 * math.sin(rad)
        x = cx + int(r * math.cos(rad))
        y = cy + int(r * math.sin(rad))
        mask_points.append((x, y))

    # Draw mask fill
    draw.polygon(mask_points, fill=(240, 235, 225, 200))

    # Eye holes (dark)
    eye_y = cy - 10
    for ex in [cx - 25, cx + 25]:
        # Almond-shaped eyes
        eye_points = []
        for t in range(0, 360, 10):
            rad = math.radians(t)
            r = 12 + 5 * math.cos(2 * rad)
            x = ex + int(r * math.cos(rad))
            y = eye_y + int(r * 0.6 * math.sin(rad))
            eye_points.append((x, y))
        draw.polygon(eye_points, fill=(10, 10, 10, 230))

    # Mouth slit
    draw.line([(cx - 20, cy + 30), (cx + 20, cy + 30)], fill=(10, 10, 10, 180), width=2)

    # Red accent marks (Ghost of Tsushima style)
    for side in [-1, 1]:
        sx = cx + side * 35
        sy = cy + 5
        draw.line([(sx, sy - 15), (sx + side * 8, sy + 15)], fill=DEEP_RED, width=3)

    # Gold border glow
    for width_offset in range(3):
        alpha = 80 - width_offset * 25
        draw.polygon(mask_points, outline=(200, 169, 100, alpha))

    img.save(os.path.join(ASSETS_DIR, "logo.png"))
    print("  Created logo.png")


def main():
    print("Generating Ghost of Tsushima Plymouth assets...")

    print("  Generating leaf frames (12)...")
    for i in range(12):
        leaf = create_leaf_frame(i, 12)
        leaf.save(os.path.join(ASSETS_DIR, f"leaf-{i + 1:03d}.png"))
    print("  Created 12 leaf frames")

    print("  Generating wind particle frames (8)...")
    for i in range(8):
        wind = create_wind_frame(i, 8)
        wind.save(os.path.join(ASSETS_DIR, f"wind-particle-{i + 1:03d}.png"))
    print("  Created 8 wind particle frames")

    print("  Generating background...")
    create_background()

    print("  Generating logo...")
    create_logo()

    print(f"\nAll assets saved to {ASSETS_DIR}")
    print("Asset generation complete!")


if __name__ == "__main__":
    main()
