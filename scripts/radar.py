"""Draw the skill radar and the language bars from assets/skills.json.

Two SVGs per chart, one per GitHub theme, because GitHub serves the README to both and
a single file tuned for one is unreadable on the other.

No third-party chart service. The usual ones are shared public instances; when they are
down the top of the profile is a row of broken images, and the owner is the last to know.

    python scripts/radar.py
"""

import json
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "assets" / "skills.json").read_text(encoding="utf-8"))

def esc(text):
    """XML-escape label text.

    Three axis names contain "&" — "Linux & systems" and friends. A bare ampersand is
    not well-formed XML, so the browser refuses the whole file and the chart renders as
    a broken image while every other asset on the page looks fine. Easy to misread as a
    path problem.
    """
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


THEMES = {
    "dark":  {"ink": "#e8ecf2", "muted": "#7d8798", "line": "#1c212b", "accent": "#39d353", "bg": "none"},
    "light": {"ink": "#14171d", "muted": "#666f7d", "line": "#e4e6ec", "accent": "#1a7f37", "bg": "none"},
}


def radar(theme, t):
    axes = DATA["radar"]
    n = len(axes)
    # Canvas is wider than tall and the web is small inside it: the labels sit outside
    # the outer ring, and the longest of them ran off a square canvas sized to the
    # ring. Sizing to the ring and not to the text is the usual way to lose the
    # ends of labels.
    size_w, size_h, cx, cy, r = 520, 420, 260, 205, 112

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size_w}" height="{size_h}" '
           f'viewBox="0 0 {size_w} {size_h}" font-family="JetBrains Mono, ui-monospace, monospace">']

    def point(i, frac):
        # Start at twelve o'clock and go clockwise, which is how people read a dial.
        a = -math.pi / 2 + (2 * math.pi * i / n)
        return cx + math.cos(a) * r * frac, cy + math.sin(a) * r * frac

    # Web rings
    for ring in (0.25, 0.5, 0.75, 1.0):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (point(i, ring) for i in range(n)))
        out.append(f'<polygon points="{pts}" fill="none" stroke="{t["line"]}" stroke-width="1"/>')

    # Spokes
    for i in range(n):
        x, y = point(i, 1.0)
        out.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{t["line"]}" stroke-width="1"/>')

    # The shape itself
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (point(i, a["score"] / 10) for i, a in enumerate(axes)))
    out.append(f'<polygon points="{pts}" fill="{t["accent"]}" fill-opacity="0.18" '
               f'stroke="{t["accent"]}" stroke-width="2" stroke-linejoin="round"/>')
    for i, a in enumerate(axes):
        x, y = point(i, a["score"] / 10)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{t["accent"]}"/>')

    # Labels, nudged outward and aligned so they never sit on the web
    for i, a in enumerate(axes):
        x, y = point(i, 1.28)
        anchor = "middle" if abs(x - cx) < 20 else ("start" if x > cx else "end")
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="{t["ink"]}" font-size="12" '
                   f'text-anchor="{anchor}" dominant-baseline="middle">{esc(a["axis"])}</text>')
        out.append(f'<text x="{x:.1f}" y="{y + 15:.1f}" fill="{t["muted"]}" font-size="10" '
                   f'text-anchor="{anchor}" dominant-baseline="middle">{a["score"]}/10</text>')

    out.append("</svg>")
    return "\n".join(out)


def languages(theme, t):
    """The language card, built like the dashboard card it is modelled on.

    Left: concentric arcs, one language per ring, each on its own radius so a short
    arc still reads — stacked on a single radius, everything after the first is
    hidden. Labels sit upper-left with a colour dot each. The centre reads a count,
    not a percentage: the percentages are in the table and repeating the largest one
    in the middle says nothing the eye has not already taken from the arcs.

    Right: the same rows as a table, because an arc is good for proportion and bad
    for a value you want to read exactly.

    Per-language colours are GitHub's own rather than the accent. They carry meaning
    the accent cannot, and a chart in one colour is a chart you have to decode.
    """
    langs = DATA["languages"]
    w, h = 580, 420
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
           f'viewBox="0 0 {w} {h}" font-family="JetBrains Mono, ui-monospace, monospace">']

    palette = ["#3572A5", "#89e051", "#00ADD8", "#dea584", "#f1e05a"]

    # ---- header -------------------------------------------------------------
    out.append(f'<text x="22" y="30" fill="{t["ink"]}" font-size="15" font-weight="600">Languages</text>')
    out.append(f'<text x="22" y="50" fill="{t["muted"]}" font-size="11">What I write by hand, not a byte count</text>')
    out.append(f'<line x1="22" y1="66" x2="{w-22}" y2="66" stroke="{t["line"]}" stroke-width="1"/>')

    # ---- dial ---------------------------------------------------------------
    cx, cy, outer, step = 136, 246, 84, 15

    def arc(r, frac):
        frac = max(0.0, min(0.999, frac))
        a0 = -math.pi / 2
        a1 = a0 + 2 * math.pi * frac
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        return f"M {x0:.1f} {y0:.1f} A {r} {r} 0 {1 if frac > 0.5 else 0} 1 {x1:.1f} {y1:.1f}"

    for i, l in enumerate(langs):
        r = outer - i * step
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["line"]}" stroke-width="9"/>')
        out.append(f'<path d="{arc(r, l["score"] / 100)}" fill="none" stroke="{palette[i % len(palette)]}" '
                   f'stroke-width="9" stroke-linecap="round"/>')

    out.append(f'<text x="{cx}" y="{cy - 4}" fill="{t["ink"]}" font-size="25" font-weight="600" '
               f'text-anchor="middle">{len(langs)}</text>')
    out.append(f'<text x="{cx}" y="{cy + 16}" fill="{t["muted"]}" font-size="11" '
               f'text-anchor="middle">languages</text>')

    # Ring key, upper-left of the dial, outermost ring first.
    for i, l in enumerate(langs):
        y = 104 + i * 17
        out.append(f'<text x="96" y="{y}" fill="{t["muted"]}" font-size="10" '
                   f'text-anchor="end">{esc(l["name"])}</text>')
        out.append(f'<circle cx="106" cy="{y - 3}" r="3.5" fill="{palette[i % len(palette)]}"/>')

    # ---- table --------------------------------------------------------------
    tx = 262
    out.append(f'<text x="{tx}" y="96" fill="{t["muted"]}" font-size="9" letter-spacing="1">LANGUAGE</text>')
    out.append(f'<text x="{w-22}" y="96" fill="{t["muted"]}" font-size="9" letter-spacing="1" '
               f'text-anchor="end">SHARE</text>')

    for i, l in enumerate(langs):
        y = 128 + i * 46
        out.append(f'<circle cx="{tx + 5}" cy="{y - 4}" r="4" fill="{palette[i % len(palette)]}"/>')
        out.append(f'<text x="{tx + 18}" y="{y}" fill="{t["ink"]}" font-size="12">{esc(l["name"])}</text>')
        out.append(f'<text x="{w-22}" y="{y}" fill="{t["ink"]}" font-size="12" '
                   f'text-anchor="end">{l["score"]}%</text>')
        bar_w = w - 22 - (tx + 18)
        out.append(f'<rect x="{tx + 18}" y="{y + 7}" width="{bar_w}" height="5" rx="2.5" fill="{t["line"]}"/>')
        out.append(f'<rect x="{tx + 18}" y="{y + 7}" width="{bar_w * l["score"] / 100:.1f}" height="5" '
                   f'rx="2.5" fill="{palette[i % len(palette)]}"/>')
        out.append(f'<text x="{tx + 18}" y="{y + 26}" fill="{t["muted"]}" font-size="9.5">{esc(l["note"])}</text>')

    # ---- footer -------------------------------------------------------------
    out.append(f'<line x1="22" y1="{h-40}" x2="{w-22}" y2="{h-40}" stroke="{t["line"]}" stroke-width="1"/>')
    out.append(f'<text x="22" y="{h-20}" fill="{t["muted"]}" font-size="9.5">'
               f'Self-rated · read off the public repos, not off a CV</text>')

    out.append("</svg>")
    return chr(10).join(out)


def main():
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    for theme, t in THEMES.items():
        (assets / f"radar-{theme}.svg").write_text(radar(theme, t), encoding="utf-8")
        (assets / f"langs-{theme}.svg").write_text(languages(theme, t), encoding="utf-8")
    print(f"drew radar-*.svg and langs-*.svg for {', '.join(THEMES)}")


if __name__ == "__main__":
    main()
