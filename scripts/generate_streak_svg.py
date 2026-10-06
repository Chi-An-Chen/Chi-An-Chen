#!/usr/bin/env python3
"""Generate an animated GitHub-streak SVG (squares light up one by one).
Run fetch_contributions.py first; designed to run in a GitHub Action daily.
Usage: python generate_streak_svg.py [username] [output.svg]
"""
import sys, json, os, datetime, html

USER = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_PROFILE_USER", "Chi-An-Chen")
OUT  = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "contrib-heatmap.svg")

def get_data(user):
    # Use the same account-checked snapshot as stats.svg; never fall back to another user's data.
    snap = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "contributions.json")
    with open(snap) as f:
        d = json.load(f)
    if d.get("username", "").lower() != user.lower():
        raise ValueError("Contribution snapshot belongs to a different account; run fetch_contributions.py first.")
    if not d["days"] or not all("level" in x for x in d["days"]):
        raise ValueError("Invalid contribution snapshot; run fetch_contributions.py first.")
    return {"contributions": d["days"], "total": {"lastYear": d["total_contributions"]}}

data = get_data(USER)
contribs = data["contributions"]
total = data["total"]["lastYear"]

# ---- layout ----
CELL, GAP, RAD, LEFT, TOP = 13, 3, 2.5, 34, 24
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
FLASH = "#b4ffaa"
GRAY = "#7d8590"
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

n = len(contribs)
sd = datetime.date.fromisoformat(contribs[0]["date"])
lead_pad = (sd.weekday() + 1) % 7  # Sunday is row zero.
NW = (lead_pad + n + 6) // 7
W = LEFT + NW*(CELL+GAP) + 6
H = TOP + 7*(CELL+GAP) + 22

# timing (seconds)
REVEAL, DUR = 3.6, 0.55
maxorder = (NW-1) + 6*0.55

rects, labels = [], []
week_start = sd - datetime.timedelta(days=lead_pad)
last_m = None
for wk in range(NW):
    d = max(sd, week_start + datetime.timedelta(days=wk*7))
    if d.month != last_m:
        last_m = d.month
        labels.append(f'<text class="lbl" x="{LEFT+wk*(CELL+GAP)}" y="{TOP-8}">{MONTHS[d.month-1]}</text>')
for name, r in [("Mon",1),("Wed",3),("Fri",5)]:
    labels.append(f'<text class="lbl" x="2" y="{TOP+r*(CELL+GAP)+CELL-2}">{name}</text>')

for i, c in enumerate(contribs):
    day_index = (datetime.date.fromisoformat(c["date"]) - week_start).days
    wk, row, lvl = day_index//7, day_index%7, c["level"]
    x = LEFT + wk*(CELL+GAP); y = TOP + row*(CELL+GAP)
    delay = round((wk + row*0.55)/maxorder * REVEAL, 3)
    cls = "c g" if lvl >= 1 else "c e"
    rects.append(
        f'<rect class="{cls}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="{RAD}" '
        f'fill="{COLORS[lvl]}" style="animation-delay:{delay}s"/>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title description" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">
<title id="title">{html.escape(USER)} — GitHub contributions</title>
<desc id="description">{total:,} contributions from {contribs[0]["date"]} to {contribs[-1]["date"]}, from this account's public GitHub contribution calendar.</desc>
<style>
  text.lbl {{ fill:{GRAY}; font-size:13px; font-weight:600; }}
  text.total {{ fill:#e6edf3; font-size:15px; font-weight:700; }}
  .c {{ transform-box:fill-box; transform-origin:center; opacity:0; animation:pop {DUR}s ease-out both; }}
  .g {{ animation:pop {DUR}s ease-out both, flash {DUR+0.15}s ease-out both; }}
  @keyframes pop {{ 0%{{opacity:0;transform:scale(.2)}} 60%{{opacity:1;transform:scale(1.1)}} 100%{{opacity:1;transform:scale(1)}} }}
  @keyframes flash {{ 0%{{filter:brightness(2.4)}} 45%{{filter:brightness(2.4)}} 100%{{filter:brightness(1)}} }}
  @media (prefers-reduced-motion: reduce) {{ .c {{ opacity:1 !important; animation:none !important; }} }}
</style>
<rect width="{W}" height="{H}" fill="none"/>
{''.join(labels)}
{''.join(rects)}
<text class="total" x="{LEFT}" y="{H-6}">{total:,} contributions in the last year</text>
</svg>'''

open(OUT, "w").write(svg)
print(f"Wrote {OUT}: {n} days, {total:,} contributions, {len(svg)//1024} KB")
