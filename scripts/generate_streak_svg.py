#!/usr/bin/env python3
"""Render each day of the contribution snapshot as a sunrise above its horizon."""
from datetime import date, timedelta
from html import escape
import json
from math import sqrt
import os
from pathlib import Path
import sys

from glass_svg import RIM_RULES, SWATCHES, glass_plate, themed_css

ROOT = Path(__file__).resolve().parent.parent
COLUMN_STEP = 18
ROW_STEP = 26
MARGIN_X = 15
MARGIN_Y = 17
BAND_HEIGHT = 6 * ROW_STEP + 2 * MARGIN_Y
BAND_GAP = 8


def render(snapshot, user, *, compact=False):
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
    cols_per_band = (cols + 1) // 2 if compact else cols
    bands = (cols + cols_per_band - 1) // cols_per_band
    width = (cols_per_band - 1) * COLUMN_STEP + 2 * MARGIN_X
    height = bands * BAND_HEIGHT + (bands - 1) * BAND_GAP
    rules = [*RIM_RULES, ('.plate', 'fill', 'base'), ('.horizon', 'stroke', 'quiet'),
             ('.active .horizon,.reflection,.month', 'stroke', 'line'),
             ('.sun', 'fill', 'sun'), ('.peak', 'fill', 'peak')]
    swatches = SWATCHES.copy()
    for count in sorted({day["count"] for day in days if 0 < day["count"] < peak}):
        u = (count / peak) ** .52
        role = f"sun-{count}"
        swatches[role] = [tuple(a + (b-a)*u for a, b in zip(low, high))
                          for low, high in zip(SWATCHES["dawn"], SWATCHES["sun"])]
        rules.append((f".{role}", "fill", role))
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">
<title id="title">{escape(user)} — contribution skyline</title>
<desc id="description">{snapshot['total_contributions']:,} contributions from {first} to {previous}. Weeks run left to right in each band, Sunday first. Higher suns mean more contributions. Sun shading also follows the count. Gold marks peak days. Bottom ticks mark the first week of each month.</desc>
<style>{themed_css(rules, swatches)}
.horizon,.reflection{{fill:none;stroke-linecap:round}}
@media(prefers-reduced-motion:no-preference){{.sun{{animation:sunrise .85s cubic-bezier(.2,.65,.3,1) backwards}}}}
@keyframes sunrise{{from{{transform:translateY(18px)}}to{{transform:translateY(0)}}}}
</style>
<defs><clipPath id="skyline"><rect x="-8" y="-12" width="16" height="17"/></clipPath></defs>
{glass_plate(width, height, radius=17)}''']
    for day in days:
        offset = (date.fromisoformat(day["date"]) - sunday).days
        week, weekday = divmod(offset, 7)
        band, column = divmod(week, cols_per_band)
        top = band * (BAND_HEIGHT + BAND_GAP)
        x = MARGIN_X + column * COLUMN_STEP
        y = top + MARGIN_Y + weekday * ROW_STEP
        n = day["count"]
        state = 'day active' if n else 'day'
        parts.append(f'<g class="{state}" transform="translate({x} {y})">'
                     f'<title>{day["date"]}: {n} contributions</title>')
        if n:
            fraction = sqrt(n / peak)
            cy = 7.4 - 10.2*fraction
            sun_class = 'sun peak' if n == peak else f'sun sun-{n}'
            delay = .22 + .7 * week / max(cols - 1, 1)
            parts.append(f'<g clip-path="url(#skyline)"><circle class="{sun_class}" cy="{cy:.3f}" r="7.1" '
                         f'style="animation-delay:{delay:.3f}s"/></g>')
            half = 1.4 + 2.4*fraction
            parts.append(f'<path class="reflection" d="M{-half:.2f} 8h{2*half:.2f}" stroke-width=".72"/>')
        horizon = "M-7.2 5.6h14.4" if n else "M-2.5 5.6h5"
        parts.append(f'<path class="horizon" d="{horizon}" stroke-width="1.2"/></g>')
        if day["date"].endswith("-01"):
            parts.append(f'<path class="month" d="M{x} {top+BAND_HEIGHT-3}v-3"/>')
    parts.append('</svg>')
    return '\n'.join(parts) + '\n'


if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GH_PROFILE_USER", "Chi-An-Chen")
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "contrib-heatmap.svg"
    snapshot = json.loads((ROOT / "data/contributions.json").read_text())
    output.write_text(render(snapshot, user))
    if len(sys.argv) > 3 or len(sys.argv) == 1:
        mobile_output = Path(sys.argv[3]) if len(sys.argv) > 3 else ROOT / "contrib-heatmap-mobile.svg"
        mobile_output.write_text(render(snapshot, user, compact=True))
    print(f"Wrote {output}: {len(snapshot['days'])} days")
