#!/usr/bin/env python3
"""
Generate the browser-tab icon set into static/.

Hugo copies static/ to the site root, and files there override the theme's, so
running this is all that's needed — Blowfish already links the standard names
from every page.

    pip install pillow
    python3 scripts/make_favicons.py

Produces:
    static/favicon.ico              16/32/48 for the browser tab
    static/favicon-16x16.png
    static/favicon-32x32.png
    static/apple-touch-icon.png     180, full-bleed for iOS home screens
    static/android-chrome-192x192.png
    static/android-chrome-512x512.png
    static/favicon.svg              vector, stays crisp at any size
    static/site.webmanifest
    assets/img/logo.png             matching square logo for the site itself

Tweak GLYPH and the three colours below to restyle. A single bold letter is
used on purpose: at 16px anything more detailed turns to mush.
"""

from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("This script needs Pillow.  Install it with:  pip install pillow")

GLYPH = "Z"
NAVY = (23, 44, 78, 255)      # tile background
ICE = (232, 242, 255, 255)    # the letter
BLUE = (96, 165, 250, 255)    # accent bead, drawn at 48px and above
SITE_NAME = "Zhu Group"

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]

ROOT = Path(__file__).resolve().parent.parent
STATIC = ROOT / "static"
ASSETS = ROOT / "assets" / "img"


def font_for(size: int):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def mark(size: int, rounded: bool = True, glyph_frac: float = 0.62,
         dot: bool = True, pad: float = 0.0) -> Image.Image:
    """One icon. `pad` insets the artwork so Android/iOS masks don't crop it."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if rounded:
        d.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * 0.22), fill=NAVY)
    else:
        d.rectangle([0, 0, size - 1, size - 1], fill=NAVY)

    inner = size * (1 - 2 * pad)
    f = font_for(max(6, int(inner * glyph_frac)))
    bb = d.textbbox((0, 0), GLYPH, font=f)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    d.text(((size - w) / 2 - bb[0], (size - h) / 2 - bb[1]), GLYPH, font=f, fill=ICE)

    if dot and size >= 48:
        r = inner * 0.085
        cx, cy = size / 2 + inner * 0.275, size / 2 - inner * 0.265
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLUE)
    return img


def main() -> None:
    STATIC.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)

    # Browser tab: rounded tile, no accent bead (invisible at these sizes).
    mark(16, glyph_frac=0.72, dot=False).save(STATIC / "favicon-16x16.png")
    mark(32, glyph_frac=0.68, dot=False).save(STATIC / "favicon-32x32.png")
    mark(256, glyph_frac=0.64).save(STATIC / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

    # Home screens: full-bleed square, artwork kept inside the mask's safe zone.
    mark(180, rounded=False, glyph_frac=0.56, pad=0.10).save(STATIC / "apple-touch-icon.png")
    mark(192, rounded=False, glyph_frac=0.56, pad=0.10).save(STATIC / "android-chrome-192x192.png")
    mark(512, rounded=False, glyph_frac=0.56, pad=0.10).save(STATIC / "android-chrome-512x512.png")

    mark(512, glyph_frac=0.62).save(ASSETS / "logo.png")

    # Vector version. Browsers that support it prefer it over the PNGs, and it
    # stays sharp on any display. The glyph is a hand-built path so the file
    # doesn't depend on a font being installed on the viewer's machine.
    navy = "#%02x%02x%02x" % NAVY[:3]
    ice = "#%02x%02x%02x" % ICE[:3]
    (STATIC / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        '<rect width="100" height="100" rx="22" fill="%s"/>'
        '<path d="M26 24 H74 V38 L45 62 H74 V76 H26 V62 L55 38 H26 Z" fill="%s"/>'
        "</svg>" % (navy, ice)
    )

    hexcol = "#%02x%02x%02x" % NAVY[:3]
    (STATIC / "site.webmanifest").write_text(
        '{"name":"%s","short_name":"%s",'
        '"icons":[{"src":"/android-chrome-192x192.png","sizes":"192x192","type":"image/png","purpose":"any maskable"},'
        '{"src":"/android-chrome-512x512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}],'
        '"theme_color":"%s","background_color":"%s","display":"standalone"}'
        % (SITE_NAME, SITE_NAME, hexcol, hexcol)
    )
    print("wrote icons to", STATIC)


if __name__ == "__main__":
    main()
