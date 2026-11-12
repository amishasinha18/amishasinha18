"""Render an image as a dot-matrix SVG.

Why a script and not an image model: this samples the pixels it is given and nothing
else. Re-running it with a different density is a different drawing of the same picture,
never a different picture. Every attempt to get here through generation changed the
subject as the price of changing the framing.

Alpha is respected. A transparent source emits no dots where it is transparent, so the
result floats on whatever background it lands on — which on GitHub means one file works
in both the light and dark themes with no second render.

    python scripts/dotify.py assets/source.webp -o assets/portrait \
        --cols 110 --color --equalize --detail 0.55
"""

import argparse
import pathlib
import sys

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is required:  python -m pip install Pillow")


def load(path, cols, equalize):
    """Open the image and reduce it to one sample per dot."""
    img = Image.open(path).convert("RGBA")

    # Sampling happens on the small grid, not the full image: one pixel per dot is
    # exactly the average that dot should represent, and PIL's box filter does the
    # averaging far better than sampling single pixels from the original would.
    rows = max(1, round(cols * img.height / img.width))
    small = img.resize((cols, rows), Image.BOX)

    if equalize:
        # Equalise luminance only. Running it per-channel shifts hue, which on this
        # artwork turned the reds orange.
        rgb = small.convert("RGB")
        lum = ImageOps.equalize(rgb.convert("L"))
        original = rgb.convert("L")
        # Scale each pixel by how much equalisation moved its luminance.
        px, lp, op = rgb.load(), lum.load(), original.load()
        for y in range(rows):
            for x in range(cols):
                o = op[x, y] or 1
                k = lp[x, y] / o
                r, g, b = px[x, y]
                px[x, y] = (min(255, int(r * k)), min(255, int(g * k)), min(255, int(b * k)))
        small = Image.merge("RGBA", (*rgb.split(), small.getchannel("A")))

    return small


def svg(small, cell, detail, colour, ink, gamma, flat, animate, stagger):
    """One <circle> per sampled cell, radius driven by how dark the cell is."""
    cols, rows = small.size
    px = small.load()
    w, h = cols * cell, rows * cell
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img" aria-label="dot matrix portrait">'
    ]

    if animate:
        # Rows fade in one after another, so the picture wipes in from the top.
        #
        # CSS inside an SVG still runs when the file is loaded through <img>, which is
        # how a README references it. Scripts and external fetches do not; keyframes
        # do. The delay sits on a <g> per row rather than on every circle — the same
        # effect from one class instead of twenty thousand.
        delays = "".join(f".r{y}{{animation-delay:{y * stagger:.3f}s}}" for y in range(rows))
        out.append(
            "<style>@keyframes dm{from{opacity:0}to{opacity:1}}"
            ".rw{animation:dm .45s ease-out both}" + delays +
            # Motion a reader cannot stop is a WCAG 2.2.2 failure. The honest fix for a
            # decorative wipe is to show the finished picture immediately.
            "@media(prefers-reduced-motion:reduce){.rw{animation:none}}</style>"
        )

    for y in range(rows):
        if animate:
            out.append(f'<g class="rw r{y}">')
        for x in range(cols):
            r, g, b, a = px[x, y]
            if a < 128:
                continue  # transparent: no dot, so the artwork floats

            if flat:
                # Every opaque cell gets the same dot and colour does the work.
                #
                # Sizing by darkness is right for a photograph and wrong for flat
                # illustration: on this artwork the near-black disc behind the figure
                # produced the fattest dots on the canvas and swallowed the red suit,
                # which is the one thing the picture is about.
                radius = (cell / 2) * detail
            else:
                # Darker cells get bigger dots. Luma weights are the usual perceptual
                # ones; a flat average makes reds vanish.
                luma = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
                weight = (1 - luma) ** gamma
                radius = (cell / 2) * detail * (0.25 + 0.75 * weight)
            if radius < 0.18:
                continue  # below this it is a speck that only adds file size

            cx, cy = x * cell + cell / 2, y * cell + cell / 2
            # Hex, not rgb(): "#1a2b3c" is 7 characters where "rgb(26,43,60)" is up to
            # 17, and with ten thousand circles that is most of the file size.
            fill = f"#{r:02x}{g:02x}{b:02x}" if colour else ink
            # Trim "12.0" to "12". Two characters per coordinate sounds like nothing
            # until it is multiplied by two coordinates and twenty thousand dots.
            out.append(f'<circle cx="{cx:g}" cy="{cy:g}" r="{round(radius, 1):g}" fill="{fill}"/>')

        if animate:
            out.append("</g>")

    out.append("</svg>")
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("image")
    p.add_argument("-o", "--out", default="assets/portrait", help="output path without extension")
    p.add_argument("--cols", type=int, default=110, help="dots across; density of the whole render")
    p.add_argument("--cell", type=float, default=10.0, help="px per cell in the SVG viewBox")
    p.add_argument("--detail", type=float, default=0.55, help="dot size vs its cell, 0-1")
    p.add_argument("--gamma", type=float, default=1.0, help=">1 thins midtones, <1 fattens them")
    p.add_argument("--color", "--colour", dest="colour", action="store_true", help="keep source colour")
    p.add_argument("--ink", default="#e8ecf2", help="dot colour when not --color")
    p.add_argument("--equalize", action="store_true", help="stretch contrast before sampling")
    p.add_argument("--flat", action="store_true", help="even dots; colour carries the image (illustration)")
    p.add_argument("--animate", action="store_true", help="fade the rows in, top to bottom")
    p.add_argument("--stagger", type=float, default=0.012, help="seconds between row fades")
    args = p.parse_args()

    src = pathlib.Path(args.image)
    if not src.exists():
        sys.exit(f"no such image: {src}")

    small = load(src, args.cols, args.equalize)
    markup = svg(small, args.cell, args.detail, args.colour, args.ink, args.gamma, args.flat,
                 args.animate, args.stagger)

    # Not with_suffix: it replaces everything after the LAST dot, so an output
    # path like "portrait-0.55" silently becomes "portrait-0.svg" and two runs
    # overwrite each other.
    out = pathlib.Path(args.out)
    if out.suffix.lower() != ".svg":
        out = out.with_name(out.name + ".svg")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(markup, encoding="utf-8")

    dots = markup.count("<circle")
    print(f"{out}  {small.size[0]}x{small.size[1]} grid  {dots} dots  {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
