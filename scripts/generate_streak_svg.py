#!/usr/bin/env python3
"""Render each day of the contribution snapshot as a sunrise above its horizon."""
from datetime import date, timedelta
from html import escape
import json
from math import sqrt
import os
from pathlib import Path
import sys

from glass_svg import themed_css

ROOT = Path(__file__).resolve().parent.parent
STEP = 18
MARGIN = 15


def render(snapshot, user):
    if snapshot.get("username", "").lower() != user.lower():
        raise ValueError("Contribution snapshot belongs to a different account; run fetch_contributions.py first.")
    days = snapshot["days"]
    if not days:
        raise ValueError("Empty contribution snapshot.")
    first = date.fromisoformat(days[0]["date"])
    sunday = first - timedelta(days=(first.weekday() + 1) % 7)
    previous = None
    for day in days:
        current = date.fromisoformat(day["date"])
        if previous is not None and current <= previous:
            raise ValueError("Invalid contribution order.")
        if type(day.get("level")) is not int or not 0 <= day["level"] <= 4:
            raise ValueError("Invalid contribution level.")
        if type(day.get("count")) is not int or day["count"] < 0:
            raise ValueError("Invalid contribution count.")
        previous = current

    peak = max(day["count"] for day in days)
    cols = (previous - sunday).days // 7 + 1
    width, height = (cols - 1) * STEP + 2*MARGIN, 6*STEP + 2*MARGIN
    rules = [('.sky', 'fill', 'base'), ('.horizon', 'stroke', 'quiet'),
             ('.active .horizon,.reflection', 'stroke', 'line'),
             ('.sun', 'fill', 'sun'), ('.peak', 'fill', 'peak')]
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">
<title id="title">{escape(user)} — contribution skyline</title>
<desc id="description">{snapshot['total_contributions']:,} contributions from {first} to {previous}. Weeks run left to right, Sunday first. Higher suns mean more contributions. Gold marks the highest daily count.</desc>
<style>{themed_css(rules)}
.horizon,.reflection{{fill:none;stroke-linecap:round}}
@media(prefers-reduced-motion:no-preference){{.sun{{animation:sunrise .85s cubic-bezier(.2,.65,.3,1) backwards}}}}
@keyframes sunrise{{from{{transform:translateY(12px)}}to{{transform:translateY(0)}}}}
</style>
<defs><clipPath id="skyline"><rect x="-8" y="-10" width="16" height="13.6"/></clipPath></defs>
<rect class="sky" width="{width}" height="{height}" rx="12"/>''']
    for day in days:
        offset = (date.fromisoformat(day["date"]) - sunday).days
        week, weekday = divmod(offset, 7)
        n = day["count"]
        state = 'day active' if n else 'day'
        parts.append(f'<g class="{state}" transform="translate({MARGIN+week*STEP} {MARGIN+weekday*STEP})">'
                     f'<title>{day["date"]}: {n} contributions</title>')
        if n:
            fraction = sqrt(n / peak)
            cy = 6.8 - 8.0*fraction
            sun_class = 'sun peak' if n == peak else 'sun'
            delay = .22 + .7 * week / max(cols - 1, 1)
            parts.append(f'<g clip-path="url(#skyline)"><circle class="{sun_class}" cy="{cy:.3f}" r="4.8" '
                         f'style="animation-delay:{delay:.3f}s"/></g>')
            half = 1 + 2*fraction
            parts.append(f'<path class="reflection" d="M{-half:.2f} 6h{2*half:.2f}" stroke-width=".72"/>')
        parts.append('<path class="horizon" d="M-6.4 4h12.8" stroke-width="1.2"/></g>')
    parts.append('</svg>')
    return '\n'.join(parts) + '\n'


if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_PROFILE_USER", "Chi-An-Chen")
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "contrib-heatmap.svg"
    snapshot = json.loads((ROOT / "data/contributions.json").read_text())
    output.write_text(render(snapshot, user))
    print(f"Wrote {output}: {len(snapshot['days'])} days")
