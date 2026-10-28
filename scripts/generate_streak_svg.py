#!/usr/bin/env python3
"""Generate a sunflower contribution SVG (oldest at center, newest at edge).
Run fetch_contributions.py first; designed to run in a GitHub Action daily.
Usage: python generate_streak_svg.py [username] [output.svg]
"""
import sys, json, os, datetime, html, math

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

# Golden-angle placement keeps chronological days evenly spread across the disk.
W, H, CX, CY, RADIUS = 480, 410, 240, 184, 128
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
n = len(contribs)
points = []
previous_date = None
for i, day in enumerate(contribs):
    date = datetime.date.fromisoformat(day["date"])
    level = day["level"]
    if (previous_date is not None and date <= previous_date) or type(level) is not int or not 0 <= level < len(COLORS):
        raise ValueError("Invalid contribution order or level; run fetch_contributions.py first.")
    previous_date = date
    angle = i * math.pi * (3 - math.sqrt(5))
    radius = RADIUS * math.sqrt((i + 0.5) / n)
    x, y = CX + radius * math.cos(angle), CY + radius * math.sin(angle)
    points.append(
        f'<circle class="day" cx="{x:.3f}" cy="{y:.3f}" r="3.584" fill="{COLORS[level]}">'
        f'<title>{date.isoformat()}: {day["count"]} contributions</title></circle>'
    )
legend = ''.join(f'<circle cx="{204+i*18}" cy="379" r="6" fill="{color}"/>'
                 for i, color in enumerate(COLORS))
last_checked = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec="microseconds")
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title description" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">
<metadata id="last-checked">Last checked: {last_checked}</metadata>
<title id="title">{html.escape(USER)} — GitHub contributions</title>
<desc id="description">{total:,} contributions from {contribs[0]["date"]} to {contribs[-1]["date"]}, from this account's public GitHub contribution calendar. One point per day, oldest at center and newest at edge. Brighter green indicates a higher contribution level.</desc>
<style>
  .background {{ fill:#f6f8fa; }}
  .heading {{ fill:#1f2328; font-size:20px; font-weight:500; }}
  .label {{ fill:#57606a; font-size:16px; }}
  @media (prefers-color-scheme: dark) {{
    .background {{ fill:#0d1117; }}
    .heading {{ fill:#e6edf3; }}
    .label {{ fill:#8b949e; }}
  }}
</style>
<rect class="background" width="{W}" height="{H}" rx="12"/>
<text class="heading" x="22" y="34">Contributions</text>
{''.join(points)}
<text class="label" x="240" y="346" text-anchor="middle">Past at center · Recent at edge</text>
<text class="label" x="185" y="385" text-anchor="end">Less</text>
{legend}
<text class="label" x="295" y="385">More</text>
</svg>'''

with open(OUT, "w") as f:
    f.write(svg)
print(f"Wrote {OUT}: {n} days, {total:,} contributions, {len(svg)//1024} KB")
