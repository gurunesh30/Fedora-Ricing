#!/usr/bin/env python3
"""
Ghost of Tsushima - GDM Background Generator
Creates the login screen background with atmospheric effects.
Requires: Pillow (pip install Pillow)
"""

import math
import random
import os
from PIL import Image, ImageDraw, ImageFilter

GDM_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gdm")
os.makedirs(GDM_DIR, exist_ok=True)


def create_gdm_background():
    """
    Create a dramatic Ghost of Tsushima login screen background.
    More detailed than the Plymouth version - features:
    - Dramatic mountain landscape
    - Golden pampas grass fields
    - Wind-swept atmosphere
    - Falling leaf particles
    - Warm golden hour lighting
    """
    w, h = 1920, 1080
    img = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # ── Sky gradient (deep dark to warm horizon) ──────────────
    for y in range(h):
        t = y / h
        if t < 0.4:
            # Upper sky: near-black to dark blue-grey
            r = int(8 + 12 * (t / 0.4))
            g = int(8 + 10 * (t / 0.4))
            b = int(12 + 15 * (t / 0.4))
        elif t < 0.6:
            # Horizon band: warm golden glow
            ht = (t - 0.4) / 0.2
            r = int(20 + 40 * math.sin(ht * math.pi))
            g = int(18 + 28 * math.sin(ht * math.pi))
            b = int(27 + 15 * math.sin(ht * math.pi))
        else:
            # Lower: dark ground
            r = int(12 - 4 * ((t - 0.6) / 0.4))
            g = int(12 - 4 * ((t - 0.6) / 0.4))
            b = int(15 - 5 * ((t - 0.6) / 0.4))
        draw.line([(0, y), (w, y)], fill=(max(r, 0), max(g, 0), max(b, 0), 255))

    # ── Moon (subtle, upper right) ────────────────────────────
    moon_x, moon_y = w - 300, 120
    moon_r = 40
    for r_offset in range(moon_r + 15, 0, -1):
        alpha = int(180 * (1 - r_offset / (moon_r + 15)) ** 2)
        if r_offset <= moon_r:
            alpha = min(220, alpha + 60)
        draw.ellipse(
            [moon_x - r_offset, moon_y - r_offset, moon_x + r_offset, moon_y + r_offset],
            fill=(220, 215, 200, alpha)
        )

    # ── Mountain layers ───────────────────────────────────────
    mountains = [
        # Far mountains (darkest, highest)
        {"base_y": 550, "peaks": [
            (0, 400), (150, 320), (350, 280), (550, 350), (750, 250),
            (950, 300), (1150, 270), (1350, 330), (1550, 290), (1750, 310), (1920, 380)
        ], "color": (14, 14, 18)},
        # Mid mountains
        {"base_y": 620, "peaks": [
            (0, 480), (200, 430), (400, 400), (650, 450), (850, 380),
            (1050, 420), (1250, 390), (1500, 440), (1700, 410), (1920, 460)
        ], "color": (18, 18, 24)},
        # Near mountains
        {"base_y": 700, "peaks": [
            (0, 560), (180, 520), (380, 540), (600, 500), (800, 530),
            (1000, 510), (1200, 545), (1400, 520), (1600, 540), (1920, 555)
        ], "color": (22, 22, 30)},
    ]

    for mtn in mountains:
        points = [(0, h)]
        points.extend(mtn["peaks"])
        points.append((w, h))
        draw.polygon(points, fill=mtn["color"])

    # ── Pampas grass field (golden, lower third) ──────────────
    field_top = 700
    for y in range(field_top, h):
        t = (y - field_top) / (h - field_top)
        # Golden-brown base with depth
        r = int(35 + 25 * (1 - t))
        g = int(28 + 18 * (1 - t))
        b = int(15 + 8 * (1 - t))
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # ── Individual grass blades ───────────────────────────────
    grass_img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    grass_draw = ImageDraw.Draw(grass_img)

    random.seed(42)  # Reproducible
    for _ in range(800):
        gx = random.randint(0, w)
        gy = random.randint(field_top + 20, h - 20)
        gh = random.randint(15, 45)
        lean = random.uniform(-8, 8)  # Wind lean
        alpha = random.randint(80, 180)
        brightness = random.randint(100, 180)

        # Grass blade as a thin line
        color = (brightness, int(brightness * 0.75), int(brightness * 0.35), alpha)
        grass_draw.line(
            [(gx, gy), (gx + lean, gy - gh)],
            fill=color,
            width=1
        )

    img = Image.alpha_composite(img, grass_img)

    # ── Mist layers ───────────────────────────────────────────
    mist = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    mist_draw = ImageDraw.Draw(mist)

    # Horizontal mist bands
    for _ in range(25):
        mx = random.randint(-200, w)
        my = random.randint(350, 650)
        mw = random.randint(300, 800)
        mh = random.randint(15, 40)
        alpha = random.randint(4, 14)
        mist_draw.ellipse([mx, my, mx + mw, my + mh], fill=(160, 155, 140, alpha))

    # Lower mist near grass
    for _ in range(15):
        mx = random.randint(-100, w)
        my = random.randint(680, 750)
        mw = random.randint(200, 500)
        mh = random.randint(10, 25)
        alpha = random.randint(6, 16)
        mist_draw.ellipse([mx, my, mx + mw, my + mh], fill=(180, 170, 140, alpha))

    mist = mist.filter(ImageFilter.GaussianBlur(radius=8))
    img = Image.alpha_composite(img, mist)

    # ── Golden light rays from upper right ────────────────────
    rays = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ray_draw = ImageDraw.Draw(rays)

    for angle in range(-40, 15, 2):
        rad = math.radians(angle)
        x1, y1 = w - 200, 80
        x2 = x1 + int(math.cos(rad) * 1400)
        y2 = y1 + int(math.sin(rad) * 1400)
        ray_draw.line([(x1, y1), (x2, y2)], fill=(200, 170, 100, 4), width=12)

    rays = rays.filter(ImageFilter.GaussianBlur(radius=3))
    img = Image.alpha_composite(img, rays)

    # ── Falling leaves (small particles) ──────────────────────
    leaves = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    leaf_draw = ImageDraw.Draw(leaves)

    leaf_colors = [
        (180, 140, 60, 140),
        (160, 120, 50, 120),
        (200, 160, 70, 130),
        (140, 100, 40, 110),
    ]

    for _ in range(60):
        lx = random.randint(0, w)
        ly = random.randint(100, 600)
        size = random.randint(2, 5)
        color = random.choice(leaf_colors)
        # Small diamond/leaf shape
        leaf_draw.polygon([
            (lx, ly - size),
            (lx + size, ly),
            (lx, ly + size),
            (lx - size, ly)
        ], fill=color)

    img = Image.alpha_composite(img, leaves)

    # ── Ghost mask silhouette (very subtle, center-upper) ─────
    ghost = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ghost_draw = ImageDraw.Draw(ghost)

    gcx, gcy = w // 2, 280
    ghost_size = 120

    # Faint circular glow
    for r in range(ghost_size + 40, 0, -1):
        alpha = int(8 * (1 - r / (ghost_size + 40)) ** 2)
        ghost_draw.ellipse(
            [gcx - r, gcy - r, gcx + r, gcy + r],
            fill=(200, 170, 100, alpha)
        )

    ghost = ghost.filter(ImageFilter.GaussianBlur(radius=5))
    img = Image.alpha_composite(img, ghost)

    # ── Vignette ──────────────────────────────────────────────
    vignette = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vig_draw = ImageDraw.Draw(vignette)

    for i in range(100):
        t = i / 100
        alpha = int(80 * t * t)
        margin = int((1 - t) * min(w, h) * 0.5)
        vig_draw.rectangle(
            [margin, margin, w - margin, h - margin],
            outline=(0, 0, 0, alpha),
            width=max(1, int(min(w, h) * 0.01))
        )

    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=20))
    img = Image.alpha_composite(img, vignette)

    # ── Final output ──────────────────────────────────────────
    output_path = os.path.join(GDM_DIR, "background.png")
    img.save(output_path, "PNG")
    print(f"GDM background saved to {output_path}")
    return output_path


if __name__ == "__main__":
    print("Generating Ghost of Tsushima GDM background...")
    create_gdm_background()
    print("Done!")
