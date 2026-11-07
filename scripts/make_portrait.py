"""Turn a photo into a green dot-matrix portrait.

Usage:  python scripts/make_portrait.py path/to/photo.png
Output: assets/portrait.png
"""
import sys
from PIL import Image, ImageDraw, ImageEnhance, ImageOps

SRC = sys.argv[1] if len(sys.argv) > 1 else "photo.png"
OUT = "assets/portrait.png"
GRID = 90          # dots per side
CELL = 9           # pixels per dot cell
BG = (13, 17, 23)  # GitHub dark background

img = Image.open(SRC).convert("RGB")
w, h = img.size
side = min(w, h)
top = 0
img = img.crop(((w - side) // 2, top, (w - side) // 2 + side, top + side))
img = ImageEnhance.Contrast(img).enhance(1.25)
small = img.resize((GRID, GRID), Image.LANCZOS)
gray = ImageOps.equalize(small.convert("L"))

corner = [small.getpixel((i, j)) for i in range(4) for j in range(4)]
bgcol = tuple(sum(c[k] for c in corner) / len(corner) for k in range(3))
size = GRID * CELL
S = 2  # supersample for smooth dots
canvas = Image.new("RGB", (size * S, size * S), BG)
d = ImageDraw.Draw(canvas)
for y in range(GRID):
    for x in range(GRID):
        lum = (gray.getpixel((x, y)) / 255) ** 1.1
        # fade out the plain backdrop: pixels close to the corner colour go dark
        px = small.getpixel((x, y))
        dist = sum(((a - b) / 255) ** 2 for a, b in zip(px, bgcol)) ** 0.5
        t = min(1, max(0, (dist - 0.05) / 0.12))
        lum *= t * t * (3 - 2 * t)
        r = (0.12 + 0.88 * lum ** 0.9) * CELL * S / 2
        cx, cy = (x + 0.5) * CELL * S, (y + 0.5) * CELL * S
        col = (int(20 + 40 * lum), int(80 + 175 * lum), int(40 + 70 * lum))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
canvas = canvas.resize((size, size), Image.LANCZOS)
canvas.save(OUT)
print("saved", OUT, canvas.size)
