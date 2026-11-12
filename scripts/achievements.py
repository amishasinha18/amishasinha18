"""Draw the GitHub profile achievements as tiles.

Drawn rather than fetched because there is nothing to fetch: GitHub exposes profile
achievements through no API, only in the HTML of the profile page. assets/achievements.json
is therefore a hand-kept list, and it will go stale the day another badge is earned.

    python scripts/achievements.py
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "assets" / "achievements.json").read_text(encoding="utf-8"))

THEMES = {
    "dark":  {"ink": "#e8ecf2", "muted": "#7d8798", "line": "#1c212b", "panel": "#0d0f14", "accent": "#39d353"},
    "light": {"ink": "#14171d", "muted": "#666f7d", "line": "#e4e6ec", "panel": "#ffffff", "accent": "#1a7f37"},
}


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(t):
    badges = DATA["badges"]
    # One row of four. Two-by-two read as a grid of equal weight; in a row they
    # read as a strip of credentials, which is nearer what they are.
    tile_w, tile_h, gap = 206, 92, 12
    cols = 4
    rows = (len(badges) + cols - 1) // cols
    w = tile_w * cols + gap * (cols - 1) + 44
    h = 74 + rows * (tile_h + gap) + 10

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
           f'font-family="JetBrains Mono, ui-monospace, monospace">']
    out.append(f'<text x="22" y="30" fill="{t["ink"]}" font-size="15" font-weight="600">Achievements</text>')
    out.append(f'<text x="22" y="50" fill="{t["muted"]}" font-size="11">Earned on GitHub</text>')
    out.append(f'<line x1="22" y1="64" x2="{w-22}" y2="64" stroke="{t["line"]}" stroke-width="1"/>')

    for i, b in enumerate(badges):
        cx = 22 + (i % cols) * (tile_w + gap)
        cy = 78 + (i // cols) * (tile_h + gap)
        out.append(f'<rect x="{cx}" y="{cy}" width="{tile_w}" height="{tile_h}" rx="12" '
                   f'fill="{t["panel"]}" stroke="{t["line"]}" stroke-width="2"/>')
        # Glyph medallion, standing in for GitHub's own badge art, which is theirs.
        out.append(f'<circle cx="{cx+40}" cy="{cy+40}" r="22" fill="none" stroke="{t["accent"]}" stroke-width="2"/>')
        out.append(f'<text x="{cx+40}" y="{cy+46}" fill="{t["accent"]}" font-size="15" font-weight="600" '
                   f'text-anchor="middle">{esc(b["glyph"])}</text>')
        out.append(f'<text x="{cx+74}" y="{cy+36}" fill="{t["ink"]}" font-size="13" '
                   f'font-weight="600">{esc(b["name"])}</text>')
        if b.get("tier"):
            out.append(f'<text x="{cx+tile_w-14}" y="{cy+24}" fill="{t["accent"]}" font-size="11" '
                       f'text-anchor="end">{esc(b["tier"])}</text>')
        words, line, lines = b["what"].split(), "", []
        for word in words:
            if len(line) + len(word) + 1 <= 24:
                line = (line + " " + word).strip()
            else:
                lines.append(line); line = word
        if line:
            lines.append(line)
        for j, ln in enumerate(lines[:2]):
            out.append(f'<text x="{cx+74}" y="{cy+56+j*14}" fill="{t["muted"]}" font-size="9.5">{esc(ln)}</text>')

    out.append("</svg>")
    return chr(10).join(out)


def main():
    assets = ROOT / "assets"
    for theme, t in THEMES.items():
        (assets / f"achievements-{theme}.svg").write_text(card(t), encoding="utf-8")
    print(f"drew {len(DATA['badges'])} achievement tiles x {len(THEMES)} themes")


if __name__ == "__main__":
    main()
