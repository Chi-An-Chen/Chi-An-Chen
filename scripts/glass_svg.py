"""Shared, self-contained glass styling for the three README SVG images."""


def surface(width, height):
    """Paint glass-inspired lighting inside the image, without page-backdrop access."""
    radius, header = 32, 44
    return f'''<style>
svg{{--ink:#243343;--muted:#526576;--base:#e9eff3;--tint:#fff;--edge:#fff;--accent:#147561;--rule:#9eafba}}
@media(prefers-color-scheme:dark){{svg{{--ink:#eaf3f5;--muted:#a2b6c0;--base:#101b24;--tint:#d5edf4;--edge:#d9f5ff;--accent:#7cdbbe;--rule:#6c929d}}}}
.glass-ink,text[fill="#e6edf3"]{{fill:var(--ink)}}
.glass-label,text[fill="#7d8590"],text[fill="#94a3b6"],text[fill="#a1adbd"],text[fill="#c1ccd9"],text[fill="#97a6b8"],text[fill="#a2b0c2"],text[fill="#b8c5d5"]{{fill:var(--muted)}}
text[fill="#5fe3bb"],text[fill="#39d353"]{{fill:var(--accent)}}
use[stroke="#5fe3bb"]{{stroke:var(--accent)}}
.glass-rule{{stroke:var(--rule);stroke-opacity:.22}}
.glass-tile{{fill:url(#glass-tile);stroke:url(#glass-edge);stroke-width:1}}
</style>
<defs>
<linearGradient id="glass-surface" x1="0" y1="0" x2="1" y2="1"><stop stop-color="var(--tint)" stop-opacity=".14"/><stop offset=".45" stop-color="var(--tint)" stop-opacity=".025"/><stop offset="1" stop-color="var(--tint)" stop-opacity=".09"/></linearGradient>
<linearGradient id="glass-edge" x1="0" y1="0" x2=".8" y2="1"><stop stop-color="var(--edge)" stop-opacity=".65"/><stop offset=".35" stop-color="var(--edge)" stop-opacity=".10"/><stop offset=".8" stop-color="var(--edge)" stop-opacity=".08"/><stop offset="1" stop-color="var(--edge)" stop-opacity=".35"/></linearGradient>
<linearGradient id="glass-tile" x1="0" y1="0" x2=".4" y2="1"><stop stop-color="var(--tint)" stop-opacity=".16"/><stop offset="1" stop-color="var(--tint)" stop-opacity=".035"/></linearGradient>
<radialGradient id="glass-teal"><stop stop-color="#62bea8" stop-opacity=".20"/><stop offset="1" stop-color="#62bea8" stop-opacity="0"/></radialGradient>
<radialGradient id="glass-blue"><stop stop-color="#94acd8" stop-opacity=".17"/><stop offset="1" stop-color="#94acd8" stop-opacity="0"/></radialGradient>
<clipPath id="glass-clip"><rect x="1" y="1" width="{width-2}" height="{height-2}" rx="{radius}"/></clipPath>
</defs>
<g clip-path="url(#glass-clip)">
<rect width="{width}" height="{height}" fill="var(--base)"/>
<ellipse cx="{width*.85}" cy="{height*.18}" rx="{width*.65}" ry="{height*.55}" fill="url(#glass-teal)"/>
<ellipse cx="{width*.04}" cy="{height*.85}" rx="{width*.65}" ry="{height*.6}" fill="url(#glass-blue)"/>
<rect width="{width}" height="{height}" fill="url(#glass-surface)"/>
<path d="M0 {header}H{width}" class="glass-rule"/>
</g>
<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="{radius}" fill="none" stroke="url(#glass-edge)" stroke-width="2"/>
<path d="M{radius} 3H{width-radius}" fill="none" stroke="var(--edge)" stroke-opacity=".20"/>
<circle cx="24" cy="22" r="5" fill="#ff5f57"/>
<circle cx="42" cy="22" r="5" fill="#febc2e"/>
<circle cx="60" cy="22" r="5" fill="#28c840"/>'''
