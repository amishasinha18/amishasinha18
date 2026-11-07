"""Build a green terminal-style 'top languages' card from public GitHub repos.

Reads GITHUB_USER (default amishasinha18) and optional GITHUB_TOKEN.
Writes assets/languages.svg. Uses only the Python standard library.
"""
import json
import os
import urllib.request
from collections import Counter
from html import escape

USER = os.environ.get("GITHUB_USER", "amishasinha18")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = "assets/languages.svg"


def api(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "lang-card"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


repos = api(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
repos = [r for r in repos if not r["fork"]]
totals = Counter()
for r in repos:
    try:
        totals.update(api(r["languages_url"]))
    except Exception as e:  # skip a repo if its languages cannot be read
        print("skip", r["name"], e)

top = totals.most_common(5)
grand = sum(totals.values()) or 1
G, BG, DIM, TXT = "#2ea043", "#0d1117", "#30363d", "#c9d1d9"
W, ROW = 480, 34
H = 90 + ROW * max(len(top), 1) + 30
parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
    f'<rect width="{W}" height="{H}" rx="12" fill="{BG}" stroke="{DIM}"/>',
    f'<text x="24" y="38" fill="{G}" font-family="monospace" font-size="16" font-weight="bold">Top languages</text>',
    f'<text x="24" y="58" fill="#8b949e" font-family="monospace" font-size="11">from {len(repos)} public repos, by code size</text>',
]
y = 90
for name, size in top:
    pct = size / grand * 100
    bar = max(2, 300 * pct / 100)
    parts += [
        f'<text x="24" y="{y}" fill="{TXT}" font-family="monospace" font-size="13">{escape(name)}</text>',
        f'<text x="{W-24}" y="{y}" fill="#8b949e" font-family="monospace" font-size="13" text-anchor="end">{pct:.1f}%</text>',
        f'<rect x="24" y="{y+8}" width="300" height="8" rx="4" fill="{DIM}"/>',
        f'<rect x="24" y="{y+8}" width="{bar:.1f}" height="8" rx="4" fill="{G}"/>',
    ]
    y += ROW
parts.append("</svg>")
os.makedirs("assets", exist_ok=True)
open(OUT, "w").write("".join(parts))
print("saved", OUT, [(n, f"{s/grand*100:.1f}%") for n, s in top])
