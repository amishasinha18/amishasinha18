"""Build two green terminal-style SVG cards from your real GitHub data:
  assets/numbers.svg       -> "at a glance" stats card
  assets/achievements.svg  -> achievements cards

Env: GITHUB_USER (default amishasinha18), GH_TOKEN (needs read:user; repo scope
adds private contribution counts). Run with --demo to use sample numbers.
Standard library only.
"""
import json
import os
import sys
import urllib.request
from datetime import date, timedelta
from html import escape

USER = os.environ.get("GITHUB_USER", "amishasinha18")
TOKEN = os.environ.get("GH_TOKEN", "")

# ---- EDIT THIS: only list achievements you actually have on your profile ----
ACHIEVEMENTS = [
    ("{}", "Galaxy Brain", "Accepted answer in a Discussion"),
    (">_", "Quickdraw", "Closed an issue or PR within 5 minutes"),
    ("!!", "YOLO", "Merged without review"),
]

G, BG, DIM, TXT, MUTE = "#2ea043", "#0d1117", "#30363d", "#e6edf3", "#8b949e"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"


def http(url, data=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "numbers-card", "Accept": "application/vnd.github+json"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch():
    user = http(f"https://api.github.com/users/{USER}")
    repos = http(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
    stars = sum(r["stargazers_count"] for r in repos if not r["fork"])
    q = ("query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{"
         "totalContributions weeks{contributionDays{date contributionCount}}}}}}")
    gq = http("https://api.github.com/graphql", json.dumps({"query": q, "variables": {"login": USER}}).encode())
    cal = gq["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = sorted((d["date"], d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"])
    longest = run = 0
    for _, c in days:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    counts = dict(days)
    d = date.today()
    if counts.get(d.isoformat(), 0) == 0:
        d -= timedelta(days=1)  # today may not have a commit yet
    current = 0
    while counts.get(d.isoformat(), 0) > 0:
        current += 1
        d -= timedelta(days=1)
    return [(stars, "Total stars"), (user["public_repos"], "Public repos"), (user["followers"], "Followers"),
            (cal["totalContributions"], "Contributions (1y)"), (current, "Current streak"), (longest, "Longest streak")]


def numbers_svg(stats):
    W, H = 640, 270
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="24" fill="{BG}" stroke="{DIM}" stroke-width="2"/>',
         f'<text x="26" y="46" fill="{G}" font-family="{FONT}" font-size="17" font-weight="bold">{escape(USER)}</text>',
         f'<text x="{W-26}" y="46" fill="{MUTE}" font-family="{FONT}" font-size="12" text-anchor="end">at a glance</text>',
         f'<line x1="26" y1="64" x2="{W-26}" y2="64" stroke="{DIM}"/>']
    for i, (val, label) in enumerate(stats):
        x, y = 26 + (i % 3) * 200, 120 + (i // 3) * 85
        o.append(f'<text x="{x}" y="{y}" fill="{TXT}" font-family="{FONT}" font-size="34" font-weight="bold">{val}</text>')
        o.append(f'<text x="{x}" y="{y+24}" fill="{MUTE}" font-family="{FONT}" font-size="12">{escape(label)}</text>')
    o.append("</svg>")
    return "".join(o)


def achievements_svg():
    n = len(ACHIEVEMENTS)
    CW, GAP = 210, 12
    W = n * CW + (n - 1) * GAP + 40
    H = 150
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<text x="20" y="26" fill="{TXT}" font-family="{FONT}" font-size="15" font-weight="bold">Achievements</text>',
         f'<text x="20" y="44" fill="{MUTE}" font-family="{FONT}" font-size="11">Earned on GitHub</text>']
    for i, (icon, name, desc) in enumerate(ACHIEVEMENTS):
        x = 20 + i * (CW + GAP)
        o.append(f'<rect x="{x}" y="58" width="{CW}" height="80" rx="12" fill="#0f1218" stroke="{DIM}" stroke-width="2"/>')
        o.append(f'<circle cx="{x+34}" cy="98" r="22" fill="none" stroke="{G}" stroke-width="2.5"/>')
        o.append(f'<text x="{x+34}" y="103" fill="{G}" font-family="{FONT}" font-size="14" font-weight="bold" text-anchor="middle">{escape(icon)}</text>')
        o.append(f'<text x="{x+66}" y="90" fill="{TXT}" font-family="{FONT}" font-size="12" font-weight="bold">{escape(name)}</text>')
        words, lines, cur = desc.split(), [], ""
        for w in words:
            if len(cur) + len(w) + 1 > 24 and cur:
                lines.append(cur)
                cur = w
            else:
                cur = f"{cur} {w}".strip()
        lines.append(cur)
        for j, ln in enumerate(lines[:2]):
            o.append(f'<text x="{x+66}" y="{107+j*13}" fill="{MUTE}" font-family="{FONT}" font-size="9.5">{escape(ln)}</text>')
    o.append("</svg>")
    return "".join(o)


if __name__ == "__main__":
    demo = "--demo" in sys.argv
    stats = [(3, "Total stars"), (25, "Public repos"), (1, "Followers"), (159, "Contributions (1y)"), (1, "Current streak"), (3, "Longest streak")] if demo else fetch()
    os.makedirs("assets", exist_ok=True)
    prefix = "/tmp/demo_" if demo else "assets/"
    open(prefix + "numbers.svg", "w", encoding="utf-8").write(numbers_svg(stats))
    open(prefix + "achievements.svg", "w", encoding="utf-8").write(achievements_svg())
    print("saved", prefix + "numbers.svg", prefix + "achievements.svg", stats)
