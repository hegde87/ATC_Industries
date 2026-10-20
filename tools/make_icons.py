#!/usr/bin/env python3
"""Generate favicons, touch icons, the web manifest and the default social image.

Usage: python3 tools/make_icons.py   (requires Pillow)
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "assets" / "icons"
GREEN, BLUE, TEAL, PAPER = (80, 176, 80), (32, 152, 240), (0, 152, 152), (255, 255, 255)

# Two offset rings from the logo mark, on a 64-unit grid.
SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="14" fill="#fff"/>
<ellipse cx="36.5" cy="31" rx="17" ry="22" fill="none" stroke="#2098f0" stroke-width="4.5"/>
<ellipse cx="28.5" cy="33" rx="17" ry="22" fill="none" stroke="#50b050" stroke-width="5"/>
</svg>
"""


def rings(size: int, radius: bool = True, pad: float = 0.0) -> Image.Image:
    scale = 8
    s = size * scale
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if radius:
        d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * 14 / 64), fill=PAPER)
    else:
        d.rectangle([0, 0, s, s], fill=PAPER)
    k = s / 64 * (1 - pad)
    off = s * pad / 2

    def ellipse(cx: float, cy: float, rx: float, ry: float, width: float, color: tuple) -> None:
        d.ellipse([off + (cx - rx) * k, off + (cy - ry) * k, off + (cx + rx) * k, off + (cy + ry) * k], outline=color, width=int(width * k))

    ellipse(36.5, 31, 17 + 2.25, 22 + 2.25, 4.5, BLUE)
    ellipse(28.5, 33, 17 + 2.5, 22 + 2.5, 5, GREEN)
    return im.resize((size, size), Image.LANCZOS)


def og_image() -> None:
    w, h = 1200, 630
    canvas = Image.new("RGB", (w, h), PAPER)
    hero = Image.open(ROOT / "assets" / "approved-orange-extrusion-hero.jpg").convert("RGB")
    target_w = 660
    ratio = max(target_w / hero.width, h / hero.height)
    hero = hero.resize((int(hero.width * ratio), int(hero.height * ratio)), Image.LANCZOS)
    left = (hero.width - target_w) // 2
    canvas.paste(hero.crop((left, 0, left + target_w, h)), (w - target_w, 0))
    logo = Image.open(ROOT / "assets" / "atc-logo-transparent.png").convert("RGBA")
    logo = logo.crop(logo.getbbox())
    logo.thumbnail((440, 260), Image.LANCZOS)
    canvas.paste(logo, ((w - target_w - logo.width) // 2, (h - logo.height) // 2), logo)
    ImageDraw.Draw(canvas).rectangle([0, h - 10, w - target_w, h], fill=TEAL)
    out = ROOT / "assets" / "img" / "og-default.jpg"
    canvas.save(out, quality=85, optimize=True, progressive=True)
    print("wrote", out.relative_to(ROOT))


def main() -> None:
    ICONS.mkdir(parents=True, exist_ok=True)
    (ICONS / "icon.svg").write_text(SVG)
    rings(180, radius=False, pad=0.12).convert("RGB").save(ICONS / "apple-touch-icon.png", optimize=True)
    rings(192).save(ICONS / "icon-192.png", optimize=True)
    rings(512).save(ICONS / "icon-512.png", optimize=True)
    rings(512, radius=False, pad=0.3).save(ICONS / "icon-maskable-512.png", optimize=True)
    rings(64).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    manifest = {
        "name": "ATC Industries",
        "short_name": "ATC",
        "description": "Engineering plastic components for OEMs since 1996.",
        "start_url": "/",
        "display": "browser",
        "background_color": "#f7fbfb",
        "theme_color": "#f7fbfb",
        "icons": [
            {"src": "/assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
            {"src": "/assets/icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }
    (ROOT / "site.webmanifest").write_text(json.dumps(manifest, indent=2) + "\n")
    print("wrote icons, favicon.ico, site.webmanifest")
    og_image()


if __name__ == "__main__":
    main()
