#!/usr/bin/env python3
"""Generate responsive WebP renditions for every source image in assets/.

Outputs go to assets/img/<slug>-<width>.webp and a manifest at
assets/img/manifest.json that tools/build.py reads for srcset + intrinsic size.
Source files are left untouched. Re-running only regenerates missing or stale files.

Usage: python3 tools/optimize_images.py [--force]
"""
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets"
OUT = SRC / "img"
WIDTHS = (480, 800, 1200, 1600, 2000)
SOURCE_EXT = {".png", ".jpg", ".jpeg", ".webp"}

# Images that carry baked-in text (infographics, certificates) need higher quality.
TEXT_HEAVY = re.compile(r"(infographic|catalog|showcase|certificat|collection|documents)", re.I)


def slugify(name: str) -> str:
    stem = Path(name).stem.lower()
    return re.sub(r"[^a-z0-9]+", "-", stem).strip("-")


def render(src: Path, force: bool) -> dict:
    slug = slugify(src.name)
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)
    has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
    if has_alpha:
        im = im.convert("RGBA")
        bbox = im.getchannel("A").getbbox()
        if bbox:
            im = im.crop(bbox)
    else:
        im = im.convert("RGB")

    w, h = im.size
    widths = sorted({x for x in WIDTHS if x < w} | {min(w, WIDTHS[-1])})
    quality = 84 if TEXT_HEAVY.search(src.name) else 74
    files = []
    for tw in widths:
        out = OUT / f"{slug}-{tw}.webp"
        if force or not out.exists() or out.stat().st_mtime < src.stat().st_mtime:
            th = round(h * tw / w)
            frame = im if tw == w else im.resize((tw, th), Image.LANCZOS)
            frame.save(out, "WEBP", quality=quality, method=6, alpha_quality=90)
        files.append({"w": tw, "file": out.name, "bytes": out.stat().st_size})
    return {"slug": slug, "width": w, "height": h, "alpha": has_alpha, "files": files}


def main() -> None:
    force = "--force" in sys.argv
    OUT.mkdir(exist_ok=True)
    manifest = {}
    for src in sorted(SRC.iterdir()):
        if src.is_file() and src.suffix.lower() in SOURCE_EXT:
            entry = render(src, force)
            manifest[src.name] = entry
            total = sum(f["bytes"] for f in entry["files"])
            print(f"{src.name:58} {src.stat().st_size // 1024:6} KB -> {len(entry['files'])} sizes, {total // 1024} KB total")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
