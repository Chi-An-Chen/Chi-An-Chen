"""Self-contained liquid-glass material shared by the three README images.

Visual reference: https://github.com/dashersw/liquid-glass-js (no JS dependency).
"""


def surface(width, height):
    """Paint soft color fields, refractive rims and nested glass inside the SVG."""
    radius, header = 40, 44
    return f'''<style>
svg{{--ink:#183b44;--muted:#48656d;--base:#d8e7e9;--tint:#fff;--edge:#fff;--accent:#087e65;--rule:#658e98;--shadow:#28525d;--aqua:#71d6c4;--blue:#7eafce;--warm:#f4e9cf;--empty:#a9bdc0;--low:#499987;--surface-top:.54;--tile-top:.62;--tile-mid:.24;--tile-end:.42}}
@media(prefers-color-scheme:dark){{svg{{--ink:#edf9fa;--muted:#cfdee3;--base:#102c35;--tint:#bce1e7;--edge:#e3fdff;--accent:#80ebc7;--rule:#9ac8d0;--shadow:#00171f;--aqua:#246d67;--blue:#355c7f;--warm:#53716f;--empty:#34535b;--low:#3a8f76;--surface-top:.20;--tile-top:.23;--tile-mid:.10;--tile-end:.20}}}}
.glass-ink,text[fill="#e6edf3"]{{fill:var(--ink)}}
.glass-label,text[fill="#7d8590"],text[fill="#94a3b6"],text[fill="#a1adbd"],text[fill="#c1ccd9"],text[fill="#97a6b8"],text[fill="#a2b0c2"],text[fill="#b8c5d5"],tspan[fill="#a2b0c2"]{{fill:var(--muted)}}
text[fill="#5fe3bb"],text[fill="#39d353"],text[fill="#f6ad55"]{{fill:var(--accent)}}
use[stroke="#5fe3bb"]{{stroke:var(--accent)}}
.glass-rule{{stroke:var(--rule);stroke-opacity:.2}}
.glass-tile{{fill:url(#glass-tile);stroke:url(#glass-edge);stroke-width:1.5;filter:url(#glass-depth)}}
.day,#legend circle{{stroke:var(--edge);stroke-opacity:.42;stroke-width:.8}}
.day[fill="#161b22"],#legend circle[fill="#161b22"]{{fill:url(#glass-day-0)}}
.day[fill="#0e4429"],#legend circle[fill="#0e4429"]{{fill:url(#glass-day-1)}}
.day[fill="#006d32"],#legend circle[fill="#006d32"]{{fill:url(#glass-day-2)}}
.day[fill="#26a641"],#legend circle[fill="#26a641"]{{fill:url(#glass-day-3)}}
.day[fill="#39d353"],#legend circle[fill="#39d353"]{{fill:url(#glass-day-4)}}
.b{{fill:url(#glass-bar);stroke:var(--edge);stroke-opacity:.35;stroke-width:1}}
.b[fill="#39d353"]{{fill:url(#glass-bar-peak)}}
</style>
<defs>
<linearGradient id="glass-surface" x1="0" y1="0" x2=".7" y2="1"><stop stop-color="var(--tint)" stop-opacity="var(--surface-top)"/><stop offset=".28" stop-color="var(--tint)" stop-opacity=".12"/><stop offset=".65" stop-color="var(--tint)" stop-opacity=".03"/><stop offset="1" stop-color="var(--tint)" stop-opacity=".25"/></linearGradient>
<linearGradient id="glass-edge" x1="0" y1="0" x2=".8" y2="1"><stop stop-color="var(--edge)" stop-opacity=".98"/><stop offset=".24" stop-color="var(--edge)" stop-opacity=".5"/><stop offset=".48" stop-color="var(--edge)" stop-opacity=".06"/><stop offset=".76" stop-color="var(--edge)" stop-opacity=".18"/><stop offset="1" stop-color="var(--edge)" stop-opacity=".85"/></linearGradient>
<linearGradient id="glass-tile" x1="0" y1="0" x2=".25" y2="1"><stop stop-color="var(--tint)" stop-opacity="var(--tile-top)"/><stop offset=".09" stop-color="var(--tint)" stop-opacity="var(--tile-mid)"/><stop offset=".55" stop-color="var(--tint)" stop-opacity=".10"/><stop offset=".92" stop-color="var(--tint)" stop-opacity=".18"/><stop offset="1" stop-color="var(--tint)" stop-opacity="var(--tile-end)"/></linearGradient>
<radialGradient id="glass-aqua"><stop stop-color="var(--aqua)" stop-opacity=".9"/><stop offset="1" stop-color="var(--aqua)" stop-opacity="0"/></radialGradient>
<radialGradient id="glass-blue"><stop stop-color="var(--blue)" stop-opacity=".8"/><stop offset="1" stop-color="var(--blue)" stop-opacity="0"/></radialGradient>
<radialGradient id="glass-warm"><stop stop-color="var(--warm)" stop-opacity=".8"/><stop offset="1" stop-color="var(--warm)" stop-opacity="0"/></radialGradient>
<linearGradient id="glass-ribbon" x1="0" y1="0" x2=".3" y2="1"><stop stop-color="var(--edge)" stop-opacity="0"/><stop offset=".48" stop-color="var(--edge)" stop-opacity=".04"/><stop offset=".51" stop-color="var(--edge)" stop-opacity=".28"/><stop offset=".62" stop-color="var(--edge)" stop-opacity=".03"/><stop offset="1" stop-color="var(--edge)" stop-opacity="0"/></linearGradient>
<radialGradient id="glass-day-0" cx=".32" cy=".22" r=".85"><stop stop-color="var(--edge)" stop-opacity=".7"/><stop offset=".42" stop-color="var(--empty)"/><stop offset="1" stop-color="var(--empty)" stop-opacity=".65"/></radialGradient>
<radialGradient id="glass-day-1" cx=".32" cy=".22" r=".85"><stop stop-color="#c3e8d7"/><stop offset=".42" stop-color="var(--low)"/><stop offset="1" stop-color="#24654f"/></radialGradient>
<radialGradient id="glass-day-2" cx=".32" cy=".22" r=".85"><stop stop-color="#c9f5cc"/><stop offset=".42" stop-color="#35a36c"/><stop offset="1" stop-color="#197b58"/></radialGradient>
<radialGradient id="glass-day-3" cx=".32" cy=".22" r=".85"><stop stop-color="#e0ffd4"/><stop offset=".42" stop-color="#65c57d"/><stop offset="1" stop-color="#289263"/></radialGradient>
<radialGradient id="glass-day-4" cx=".32" cy=".22" r=".85"><stop stop-color="#f4ffda"/><stop offset=".42" stop-color="#a2e77e"/><stop offset="1" stop-color="#4cb975"/></radialGradient>
<linearGradient id="glass-bar" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#72ceb0"/><stop offset=".45" stop-color="#2c9c83"/><stop offset="1" stop-color="#187565"/></linearGradient>
<linearGradient id="glass-bar-peak" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#bceca2"/><stop offset=".5" stop-color="#75ca8c"/><stop offset="1" stop-color="#339b78"/></linearGradient>
<filter id="glass-depth" x="-15%" y="-30%" width="130%" height="170%" color-interpolation-filters="sRGB">
<feDropShadow dx="0" dy="5" stdDeviation="5" flood-color="var(--shadow)" flood-opacity=".13" result="depth"/>
<feGaussianBlur in="SourceAlpha" stdDeviation=".7" result="soft-alpha"/>
<feOffset in="soft-alpha" dy="1.5" result="offset-alpha"/>
<feComposite in="SourceAlpha" in2="offset-alpha" operator="out" result="rim"/>
<feFlood flood-color="var(--edge)" flood-opacity=".8"/>
<feComposite in2="rim" operator="in" result="light"/>
<feMerge><feMergeNode in="depth"/><feMergeNode in="light"/></feMerge>
</filter>
<clipPath id="glass-clip"><rect x="1" y="1" width="{width-2}" height="{height-2}" rx="{radius}"/></clipPath>
</defs>
<!-- shortcut: SVG images cannot sample GitHub's backdrop; use WebGL only in a standalone web version. -->
<g clip-path="url(#glass-clip)">
<rect width="{width}" height="{height}" fill="var(--base)"/>
<ellipse cx="{width*.93}" cy="{height*.27}" rx="{width*.69}" ry="{height*.68}" fill="url(#glass-aqua)"/>
<ellipse cx="{width*.08}" cy="{height*.88}" rx="{width*.67}" ry="{height*.65}" fill="url(#glass-blue)"/>
<ellipse cx="{width*.10}" cy="0" rx="{width*.65}" ry="{height*.42}" fill="url(#glass-warm)"/>
<rect width="{width}" height="{height}" fill="url(#glass-surface)"/>
<path d="M{-width*.2} {height*.72}Q{width*.28} {height*.04} {width*1.15} {height*.38}L{width*1.15} {height*.82}Q{width*.35} {height*.36} {-width*.2} {height*1.08}Z" fill="url(#glass-ribbon)"/>
<rect x="4" y="4" width="{width-8}" height="{height-8}" rx="{radius-3}" fill="none" stroke="var(--shadow)" stroke-opacity=".1" stroke-width="6"/>
<rect x="7" y="7" width="{width-14}" height="{height-14}" rx="{radius-6}" fill="none" stroke="url(#glass-edge)" stroke-opacity=".55" stroke-width="1.5"/>
<path d="M16 {header}H{width-16}" class="glass-rule"/>
</g>
<rect x="1.5" y="1.5" width="{width-3}" height="{height-3}" rx="{radius}" fill="none" stroke="url(#glass-edge)" stroke-width="3"/>
<path d="M3 {radius+24}V{radius}Q3 3 {radius} 3H{width*.46}M{width-3} {height-radius-24}V{height-radius}Q{width-3} {height-3} {width-radius} {height-3}H{width*.68}" fill="none" stroke="var(--edge)" stroke-opacity=".7" stroke-width="2" stroke-linecap="round"/>
<rect x="{width/2-115}" y="7" width="230" height="31" rx="15.5" class="glass-tile"/>
<g stroke="var(--edge)" stroke-opacity=".7" stroke-width="1">
<circle cx="27" cy="23" r="5" fill="#eaa79c"/>
<circle cx="45" cy="23" r="5" fill="#e7cb8e"/>
<circle cx="63" cy="23" r="5" fill="#8bc9b4"/>
</g>'''
