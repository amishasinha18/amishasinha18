"""Generate an animated CI/CD pipeline SVG (SMIL, works inside GitHub READMEs)."""
G, BG, DIM = "#2ea043", "#0d1117", "#30363d"
stages = ["code", "build", "test", "deploy"]
W, H, X0, GAP, Y = 760, 150, 100, 187, 80
dur = 6
els = []
for i in range(3):
    x1, x2 = X0 + i * GAP + 50, X0 + (i + 1) * GAP - 50
    els.append(f'<line x1="{x1}" y1="{Y}" x2="{x2}" y2="{Y}" stroke="{DIM}" stroke-width="3" stroke-dasharray="6 6"/>')
for i, name in enumerate(stages):
    cx = X0 + i * GAP
    t0 = i / 3 * 0.85
    a = max(t0 - 0.02, 0.0)
    b = min(t0 + 0.02, 0.97)
    c = min(t0 + 0.14, 0.98)
    kt = "0;" + ";".join(f"{v:.3f}" for v in (a, b, c)) + ";1"
    els.append(
        f'<rect x="{cx-50}" y="{Y-28}" width="100" height="56" rx="10" fill="{BG}" stroke="{DIM}" stroke-width="2">'
        f'<animate attributeName="stroke" values="{DIM};{DIM};{G};{DIM};{DIM}" keyTimes="{kt}" dur="{dur}s" repeatCount="indefinite"/></rect>')
    els.append(f'<text x="{cx}" y="{Y+5}" fill="{G}" font-family="monospace" font-size="16" text-anchor="middle">{name}</text>')
    els.append(f'<text x="{cx}" y="{Y+55}" fill="#8b949e" font-family="monospace" font-size="11" text-anchor="middle">{i+1:02d}</text>')
path = f"M{X0},{Y} L{X0+3*GAP},{Y}"
els.append(f'<circle r="7" fill="{G}"><animateMotion dur="{dur}s" repeatCount="indefinite" path="{path}" keyPoints="0;1;1" keyTimes="0;0.85;1" calcMode="linear"/>'
           f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.85;0.9;1" dur="{dur}s" repeatCount="indefinite"/></circle>')
els.append(f'<text x="{W/2}" y="26" fill="#8b949e" font-family="monospace" font-size="12" text-anchor="middle">$ git push &amp;&amp; automate everything</text>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><rect width="{W}" height="{H}" rx="12" fill="{BG}"/>' + "".join(els) + "</svg>"
open("assets/pipeline.svg", "w").write(svg)
print("saved assets/pipeline.svg")
