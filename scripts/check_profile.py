#!/usr/bin/env python3
"""Offline checks: correct account, shared contribution values and key fallback."""
import datetime
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch
import xml.etree.ElementTree as ET

import render_profile_svg as profile

ROOT = Path(__file__).resolve().parent.parent
USER = os.environ.get("GH_PROFILE_USER", "Chi-An-Chen")
NS = {"s": "http://www.w3.org/2000/svg"}
TOKEN_PATTERN = re.compile(r"\b(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})\b")

# Report the filename only; never print a suspected credential into public Action logs.
assert TOKEN_PATTERN.search("github_pat_" + "x" * 40)
assert TOKEN_PATTERN.search("ghp_" + "x" * 36)
publish_files = [ROOT / name for name in ("README.md", ".gitignore", "avi-ascii.svg", "stats.svg", "contrib-heatmap.svg")]
publish_files += list((ROOT / "data").glob("*.json")) + list((ROOT / "scripts").glob("*.py"))
publish_files += [p for p in (ROOT / ".github").rglob("*") if p.is_file()]
for path in publish_files:
    assert not TOKEN_PATTERN.search(path.read_text()), f"Possible GitHub key in {path.relative_to(ROOT)}; remove it before publishing."


def run(script, *args, cwd=ROOT):
    return subprocess.run([sys.executable, str(ROOT / "scripts" / script), *map(str, args)],
                          cwd=cwd, capture_output=True, text=True)


profile.check()
contrib = json.loads((ROOT / "data/contributions.json").read_text())
aggregate = json.loads((ROOT / "data/profile-data.json").read_text())
# The public snapshot must stay an aggregate; never publish raw repository metadata or credentials.
assert set(aggregate) == {
    "username", "display_name", "generated_at", "repository_count", "public_count", "private_count",
    "fork_count", "archived_count", "repositories_with_code", "includes_private", "total_bytes",
    "languages", "scope", "metric",
}
assert all(set(language) == {"name", "bytes", "repositories"} for language in aggregate["languages"])
assert contrib["username"].lower() == aggregate["username"].lower() == USER.lower()
assert contrib["total_contributions"] == sum(day["count"] for day in contrib["days"])
assert contrib["total_contributions"] == sum(month["total"] for month in contrib["monthly"])
assert aggregate["total_bytes"] == sum(lang["bytes"] for lang in aggregate["languages"])
readme = (ROOT / "README.md").read_text()
assert "./contributions.sh" in readme and "./links.sh" not in readme

graph = ET.parse(ROOT / "contrib-heatmap.svg").getroot()
stats = ET.parse(ROOT / "stats.svg").getroot()
card = ET.parse(ROOT / "avi-ascii.svg").getroot()
for svg in (graph, stats):
    assert USER.lower() in " ".join(svg.itertext()).lower()
    assert f'{contrib["total_contributions"]:,}' in " ".join(svg.itertext())
assert (ROOT / "avi-ascii.svg").read_text() == profile.render(aggregate)
assert card.attrib["viewBox"] == stats.attrib["viewBox"] == "0 0 840 880"
cells = [r for r in graph.findall("s:rect", NS) if r.get("class", "").startswith("c ")]
assert len(cells) == len(contrib["days"])
palette = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
for cell, day in zip(cells, contrib["days"]):
    row = (datetime.date.fromisoformat(day["date"]).weekday() + 1) % 7
    assert float(cell.attrib["y"]) == 24 + row * 16
    assert cell.attrib["fill"] == palette[day["level"]]

with tempfile.TemporaryDirectory() as temporary:
    tmp = Path(temporary)
    output = tmp / "preserved.svg"
    output.write_text("existing card")
    wrong = dict(contrib, username="another-account")
    snapshot = tmp / "wrong.json"
    snapshot.write_text(json.dumps(wrong))
    result = run("render_stats_svg.py", snapshot, output)
    assert result.returncode != 0 and "different account" in result.stderr
    assert output.read_text() == "existing card"
    result = run("generate_streak_svg.py", "another-account", output)
    assert result.returncode != 0 and "different account" in result.stderr
    assert output.read_text() == "existing card"

    # A calendar starting on Monday must still put Monday in row one.
    (tmp / "scripts").mkdir()
    (tmp / "data").mkdir()
    shutil.copy2(ROOT / "scripts/generate_streak_svg.py", tmp / "scripts")
    days = [{"date": "2026-10-05", "count": 1, "level": 1},
            {"date": "2026-10-06", "count": 0, "level": 0}]
    (tmp / "data/contributions.json").write_text(json.dumps({
        "username": USER, "days": days, "total_contributions": 1,
    }))
    result = subprocess.run([sys.executable, str(tmp / "scripts/generate_streak_svg.py"), USER, str(output)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    first = ET.parse(output).getroot().findall("s:rect", NS)[1]
    assert first.attrib["x"] == "34" and first.attrib["y"] == "40"

    # Auth errors must fail before touching the existing image or snapshot.
    output.write_text("existing card")
    with patch.object(sys, "argv", ["render_profile_svg.py", "--username", USER,
                                    "--output", str(output), "--snapshot", str(snapshot)]), \
         patch.dict(os.environ, {"GH_TOKEN": "invalid-test-key"}), \
         patch.object(profile, "api", side_effect=RuntimeError("Invalid token")):
        try:
            profile.main()
        except RuntimeError:
            pass
        else:
            raise AssertionError("Invalid key must fail.")
    assert output.read_text() == "existing card"
    assert json.loads(snapshot.read_text())["username"] == "another-account"

print(f"Integration check passed: {USER}, {contrib['total_contributions']:,} contributions, "
      f"{aggregate['repository_count']} repositories; SVGs, weekday alignment and stale-data guards agree.")
