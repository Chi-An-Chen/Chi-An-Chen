#!/usr/bin/env python3
"""Render a GitHub profile SVG from every owned public/private repository.

No Python dependencies. GH_TOKEN enables private repositories; no key means public only.
Use --data to render a saved aggregate without calling GitHub.
"""
import argparse
import collections
import concurrent.futures
import datetime
import html
import json
import os
from pathlib import Path
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET


# Curated experience descriptions; statistics below refresh automatically.
EXPERIENCES = [
    ("Computer Vision", "Face ID / FacePAD", "Segmentation / detection", "vision"),
    ("Generative AI", "VLMs / virtual try-on", "Model fine-tuning", "spark"),
    ("RAG & Retrieval", "Document-grounded Q&A", "LangChain / LangGraph", "search"),
    ("Edge & Backend", "Go / Python services", "ONNX / TensorRT / Jetson", "chip"),
]
COLORS = {
    "Python": "#58a6ff", "HTML": "#f77655", "Jupyter Notebook": "#f6ad55",
    "JavaScript": "#f1e05a", "TeX": "#7ccf8a", "Go": "#00add8",
    "TypeScript": "#3178c6", "CSS": "#ab7df8", "Other": "#7c8798",
}


def api(endpoint, token=""):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "profile-experience-svg",
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request("https://api.github.com" + endpoint, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if token:
            detail = "verify token access; authenticated errors are not silently downgraded"
        else:
            detail = "public API may be rate-limited; retry later or set GH_TOKEN"
        raise RuntimeError(f"GitHub returned HTTP {error.code}; {detail}.") from None


def aggregate(user, repos, language_maps, include_private=True):
    if len(repos) != len(language_maps) or len({r["id"] for r in repos}) != len(repos):
        raise ValueError("Repository coverage is incomplete or contains duplicates.")
    if any(r["owner"]["login"].lower() != user["login"].lower() for r in repos):
        raise ValueError("Statistics must contain repositories owned by this account only.")
    totals, counts = collections.Counter(), collections.Counter()
    for languages in language_maps:
        if any(type(count) is not int or count < 0 for count in languages.values()):
            raise ValueError("Invalid GitHub language byte count.")
        totals.update({name: count for name, count in languages.items() if count})
        counts.update(name for name, count in languages.items() if count)
    public_count = sum(not repo["private"] for repo in repos)
    private_count = len(repos) - public_count if include_private else None
    if not include_private and any(repo["private"] for repo in repos):
        raise ValueError("Public fallback must never contain private repositories.")
    # Detect incomplete credentials when GitHub exposes the expected counts.
    if user.get("public_repos") is not None and public_count != user["public_repos"]:
        raise ValueError("Public repository coverage changed or is incomplete; rerun the fetch.")
    if include_private and user.get("owned_private_repos") is not None and private_count != user["owned_private_repos"]:
        raise ValueError("Private repository coverage is incomplete; grant access to all repositories.")
    return {
        "username": user["login"],
        "display_name": (user.get("name") or user["login"]).strip(),
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "repository_count": len(repos), "public_count": public_count, "private_count": private_count,
        "fork_count": sum(repo["fork"] for repo in repos),
        "archived_count": sum(repo["archived"] for repo in repos),
        "repositories_with_code": sum(any(languages.values()) for languages in language_maps),
        "includes_private": include_private,
        "total_bytes": sum(totals.values()),
        "languages": [
            {"name": name, "bytes": count, "repositories": counts[name]}
            for name, count in sorted(totals.items(), key=lambda pair: (-pair[1], pair[0]))
        ],
        "scope": ("All owned public and private repositories" if include_private else "Owned public repositories only") + ", including forks and archived repositories",
        "metric": "GitHub language bytes on each repository's default branch; not personal commit authorship",
    }


def collect(username):
    token = os.environ.get("GH_TOKEN", "").strip()
    include_private = bool(token)
    user = api("/user" if token else f"/users/{username}", token)
    if user["login"].lower() != username.lower():
        raise ValueError("GH_TOKEN belongs to a different account; pass its login with --username.")
    repos, page = [], 1
    endpoint = "/user/repos?affiliation=owner&visibility=all" if token else f"/users/{username}/repos?type=owner"
    while True:
        batch = api(f"{endpoint}&per_page=100&page={page}", token)
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    # Four requests at once are enough for a personal profile; no repository is skipped on errors.
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        language_maps = list(pool.map(lambda repo: api(f"/repos/{repo['full_name']}/languages", token), repos))
    return aggregate(user, repos, language_maps, include_private)


def render(data):
    include_private = data.get("includes_private", data["private_count"] is not None)
    expected_count = data["public_count"] + (data["private_count"] if include_private else 0)
    if expected_count != data["repository_count"]:
        raise ValueError("Public/private counts do not match the repository total.")
    languages = sorted(data["languages"], key=lambda item: (-item["bytes"], item["name"]))
    total = sum(item["bytes"] for item in languages)
    if total != data["total_bytes"] or any(item["bytes"] <= 0 for item in languages):
        raise ValueError("Language totals are invalid.")
    shown = languages[:5]
    if len(languages) > 5:
        shown.append({"name": "Other", "bytes": sum(item["bytes"] for item in languages[5:])})
    updated = datetime.datetime.fromisoformat(data["generated_at"].replace("Z", "+00:00"))
    updated = updated.astimezone(datetime.timezone(datetime.timedelta(hours=8)))
    parts = []

    def text(x, y, value, size=22, fill="#e6edf3", weight=400, anchor="start", extra=""):
        parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
                     f'font-weight="{weight}" text-anchor="{anchor}" {extra}>{html.escape(str(value))}</text>')

    parts.append('''<svg xmlns="http://www.w3.org/2000/svg" width="840" height="880" viewBox="0 0 840 880" role="img" aria-labelledby="title description" font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif">
<style>
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.enter{animation:appear .55s ease-out both}
.stagger{animation-delay:.14s}.later{animation-delay:.28s}
.scan{animation:reveal 1.1s cubic-bezier(.2,.7,.2,1) both;animation-delay:.35s;transform-origin:36px 688px}
@keyframes appear{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
@keyframes reveal{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@media(prefers-reduced-motion:reduce){.enter,.scan{animation:none!important;opacity:1;transform:none}}
</style>
<defs>
<linearGradient id="surface" x1="0" y1="0" x2=".7" y2="1"><stop stop-color="#111b25"/><stop offset="1" stop-color="#0d1117"/></linearGradient>
<radialGradient id="glow"><stop stop-color="#5fe3bb" stop-opacity=".07"/><stop offset="1" stop-color="#5fe3bb" stop-opacity="0"/></radialGradient>
<clipPath id="bar"><rect x="36" y="676" width="768" height="20" rx="10"/></clipPath>
<symbol id="vision" viewBox="0 0 32 32"><path d="M2 16s5-9 14-9 14 9 14 9-5 9-14 9S2 16 2 16Z"/><circle cx="16" cy="16" r="4"/></symbol>
<symbol id="spark" viewBox="0 0 32 32"><path d="m16 3 3.5 9.5L29 16l-9.5 3.5L16 29l-3.5-9.5L3 16l9.5-3.5Z"/></symbol>
<symbol id="search" viewBox="0 0 32 32"><rect x="4" y="3" width="16" height="23" rx="3"/><path d="M8 9h8M8 14h7M8 19h5"/><circle cx="22" cy="21" r="5"/><path d="m25.5 24.5 4 4"/></symbol>
<symbol id="chip" viewBox="0 0 32 32"><rect x="8" y="8" width="16" height="16" rx="3"/><path d="M12 3v5M20 3v5M12 24v5M20 24v5M3 12h5M3 20h5M24 12h5M24 20h5"/><rect x="12" y="12" width="8" height="8" rx="1"/></symbol>
</defs>''')
    parts.append(f'<title id="title">{html.escape(data["display_name"])} — development profile</title>')
    private_scope = f'{data["private_count"]} private' if include_private else "private repositories not included"
    description = f'{data["repository_count"]} owned repositories, {data["public_count"]} public, {private_scope}. '
    description += "Language percentages use GitHub code bytes across " + ("owned public and private repositories. " if include_private else "owned public repositories only. ")
    description += ", ".join(f'{item["name"]} {item["bytes"] / total * 100:.2f}%' for item in shown) if total else "No language data."
    parts.append(f'<desc id="description">{html.escape(description)}</desc>')
    parts.append('''<rect x=".5" y=".5" width="839" height="879" rx="16" fill="url(#surface)" stroke="#303b47"/>
<ellipse cx="720" cy="125" rx="300" ry="230" fill="url(#glow)"/>
<path d="M1 44h838" stroke="#2b3542"/>
<circle cx="24" cy="22" r="5" fill="#ff5f57"/><circle cx="42" cy="22" r="5" fill="#febc2e"/><circle cx="60" cy="22" r="5" fill="#28c840"/>
<path d="M36 344h768M36 606h768M36 834h768" stroke="#283341"/>''')
    text(420, 27, "~/github  /  experience.py", 15, "#94a3b6", anchor="middle", extra='class="mono"')
    parts.append('<g class="enter">')
    text(36, 88, "DEVELOPER / PROJECT EXPERIENCE", 17, "#5fe3bb", 600, extra='letter-spacing="1.8"')
    text(36, 149, data["display_name"], 56, weight=750)
    text(38, 185, "@" + data["username"], 23, "#a1adbd", extra='class="mono"')
    text(36, 223, "Computer vision · Generative AI · Edge systems", 23, "#c1ccd9")
    parts.append('</g><g class="enter stagger">')
    private_label = "PRIVATE" if include_private else "PRIVATE (NOT INCLUDED)"
    private_value = data["private_count"] if include_private else "—"
    for x, value, label in [(36, data["repository_count"], "REPOSITORIES"), (302, data["public_count"], "PUBLIC"), (568, private_value, private_label)]:
        parts.append(f'<rect x="{x}" y="246" width="236" height="77" rx="10" fill="#17212c"/>')
        text(x + 18, 286, value, 40, weight=650)
        text(x + 18, 317, label, 15 if include_private or x != 568 else 12, "#97a6b8", 600, extra='letter-spacing="1"')
    text(36, 373, "PROJECT EXPERIENCE", 18, "#a2b0c2", 600, extra='letter-spacing="1.5"')
    for index, (title, line1, line2, icon) in enumerate(EXPERIENCES):
        x, y = 36 + index % 2 * 392, 390 + index // 2 * 108
        parts.append(f'<rect x="{x}" y="{y}" width="376" height="96" rx="10" fill="#121c27" stroke="#263444"/>')
        parts.append(f'<use href="#{icon}" x="{x + 16}" y="{y + 16}" width="25" height="25" fill="none" stroke="#5fe3bb" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>')
        text(x + 52, y + 34, title, 24, weight=600)
        text(x + 16, y + 60, line1, 20, "#b8c5d5")
        text(x + 16, y + 85, line2, 20, "#b8c5d5")
    parts.append('</g><g class="enter later">')
    text(36, 634, "Languages", 29, weight=650)
    text(804, 634, f'{len(languages)} languages', 20, "#a2b0c2", anchor="end")
    text(36, 663, "Code share · public + private" if include_private else "Code share · PUBLIC ONLY / no key", 20, "#a2b0c2" if include_private else "#f6ad55")
    parts.append('<rect x="36" y="676" width="768" height="20" rx="10" fill="#283341"/>')
    parts.append('<g clip-path="url(#bar)"><g class="scan">')
    x = 36
    for index, item in enumerate(shown):
        width = 768 * item["bytes"] / total
        color = COLORS.get(item["name"], ["#ab7df8", "#56c8d8", "#fb8ea8"][index % 3])
        parts.append(f'<rect x="{x:.4f}" y="676" width="{width:.4f}" height="20" fill="{color}"/>')
        x += width
    parts.append('</g></g>')
    for index, item in enumerate(shown):
        x, y = 36 + index % 2 * 392, 731 + index // 2 * 39
        color = COLORS.get(item["name"], ["#ab7df8", "#56c8d8", "#fb8ea8"][index % 3])
        parts.append(f'<circle cx="{x + 7}" cy="{y - 7}" r="7" fill="{color}"/>')
        name = item["name"] if item["name"] != "Other" else f'Other ({len(languages) - 5})'
        text(x + 24, y, name, 23, weight=550)
        text(x + 366, y, f'{item["bytes"] / total * 100:.2f}%', 23, "#a2b0c2", anchor="end")
    if not total:
        text(36, 743, "No language data is available yet.", 23, "#a2b0c2")
    parts.append('</g>')
    text(36, 859, f'GitHub code bytes · {data["repositories_with_code"]}/{data["repository_count"]} repos with code', 17, "#a2b0c2")
    text(804, 859, updated.strftime("%Y-%m-%d %H:%M UTC+8"), 17, "#a2b0c2", anchor="end")
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def check():
    from unittest.mock import patch
    user = {"login": "example", "name": "Example & Co", "public_repos": 1, "owned_private_repos": 1}
    repos = [{"id": i, "private": bool(i), "owner": {"login": "example"}, "fork": False, "archived": False} for i in range(2)]
    data = aggregate(user, repos, [{"Python": 70, "C++": 10}, {"Go": 20}])
    assert data["total_bytes"] == 100 and data["private_count"] == 1
    assert data["languages"][0] == {"name": "Python", "bytes": 70, "repositories": 1}
    svg = render(data)
    root = ET.fromstring(svg)
    assert root.attrib["viewBox"] == "0 0 840 880" and "70.00%" in svg
    assert "Example &amp; Co" in svg and "<script" not in svg and "full_name" not in svg
    many = aggregate(user, repos, [{f"Language {i}": i for i in range(1, 8)}, {}])
    assert "Other (2)" in render(many)
    empty = aggregate(user, repos, [{}, {}])
    assert "No language data" in render(empty)
    public = aggregate({"login": "example", "public_repos": 1}, repos[:1], [{"Python": 10}], False)
    assert public["private_count"] is None and "PUBLIC ONLY / no key" in render(public)
    requests = []
    def fake_api(endpoint, token=""):
        requests.append((endpoint, token))
        if endpoint in ("/users/example", "/user"):
            return user
        if endpoint.startswith("/users/example/repos"):
            return [dict(repos[0], full_name="example/public")]
        if endpoint.startswith("/user/repos"):
            return [dict(repos[0], full_name="example/public"), dict(repos[1], full_name="example/private")]
        return {"Python": 10}
    with patch.dict(os.environ, {"GH_TOKEN": ""}), patch(__name__ + ".api", fake_api):
        assert collect("example")["private_count"] is None
    assert all(not token for _, token in requests) and not any("example/private" in path for path, _ in requests)
    requests.clear()
    with patch.dict(os.environ, {"GH_TOKEN": "test-key"}), patch(__name__ + ".api", fake_api):
        assert collect("example")["private_count"] == 1
    assert all(token == "test-key" for _, token in requests)
    try:
        aggregate(user, repos, [{}])
    except ValueError:
        pass
    else:
        raise AssertionError("Incomplete coverage must fail.")
    print("Check passed: public/private aggregation, no-key fallback, SVG escaping, Other grouping, and empty repositories.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", default="Chi-An-Chen", help="GitHub account; default: Chi-An-Chen.")
    parser.add_argument("--data", type=Path, help="Render an existing aggregate JSON without fetching GitHub.")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent.parent / "avi-ascii.svg")
    parser.add_argument("--snapshot", type=Path, help="Save aggregate JSON; never contains repository names.")
    parser.add_argument("--check", action="store_true", help="Run the small offline check.")
    args = parser.parse_args()
    if args.check:
        check()
        return
    data = json.loads(args.data.read_text()) if args.data else collect(args.username)
    if data["username"].lower() != args.username.lower():
        raise ValueError("Profile snapshot belongs to a different account; check --username.")
    svg = render(data)
    ET.fromstring(svg)
    args.output.write_text(svg, encoding="utf-8")
    if args.snapshot:
        args.snapshot.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    scope = "public + private" if data.get("includes_private", data["private_count"] is not None) else "public only (no key)"
    print(f'Updated {args.output}: {data["repository_count"]} repositories, {len(data["languages"])} languages, {scope}.')


if __name__ == "__main__":
    main()
