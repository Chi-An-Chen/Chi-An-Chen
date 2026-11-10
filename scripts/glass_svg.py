"""Shared SVG palette, authored in OKLCH and exported as portable sRGB."""
from math import cos, radians, sin


def srgb(lightness, chroma, hue):
    """Convert an OKLCH swatch to hex so static SVG renderers get the same colors."""
    a, b = chroma * cos(radians(hue)), chroma * sin(radians(hue))
    l = (lightness + .3963377774*a + .2158037573*b)**3
    m = (lightness - .1055613458*a - .0638541728*b)**3
    s = (lightness - .0894841775*a - 1.291485548*b)**3
    rgb = (4.0767416621*l - 3.3077115913*m + .2309699292*s,
           -1.2684380046*l + 2.6097574011*m - .3413193965*s,
           -.0041960863*l - .7034186147*m + 1.7076147010*s)
    channels = []
    for value in rgb:
        value = max(0, min(1, value))
        encoded = 12.92*value if value <= .0031308 else 1.055*value**(1/2.4) - .055
        channels.append(round(encoded * 255))
    return '#%02x%02x%02x' % tuple(channels)


#                     dark                         light
SWATCHES = {
    "base":  ((.216, .022, 256), (.967, .009, 250)),
    "tile":  ((.275, .023, 255), (.935, .014, 250)),
    "rule":  ((.64, .030, 240),  (.63, .031, 245)),
    "quiet": ((.40, .023, 244),  (.63, .024, 244)),
    "line":  ((.54, .032, 245),  (.49, .033, 245)),
    "dawn":  ((.66, .065, 55),   (.55, .070, 55)),
    "sun":   ((.85, .090, 74),   (.43, .074, 65)),
    "peak":  ((.94, .078, 91),   (.36, .069, 75)),
    "ink":   ((.94, .010, 155),  (.25, .024, 244)),
    "muted": ((.77, .018, 175),  (.43, .028, 243)),
}


def themed_css(rules, swatches=SWATCHES):
    """Emit concrete colors, including a dark default for non-CSS-media renderers."""
    themes = []
    for i in range(2):
        themes.append('\n'.join(f'{selector}{{{prop}:{srgb(*swatches[role][i])}}}'
                                for selector, prop, role in rules))
    return themes[0] + '\n@media(prefers-color-scheme:light){' + themes[1] + '}'


RIM_RULES = [('.rim-tone', 'stop-color', 'rule'), ('.rim-base', 'stop-color', 'base')]


def glass_plate(width, height, *, radius):
    """Draw the common directional rim and the light fading in from that edge."""
    return f'''<defs>
<linearGradient id="rim" x2="95%" y2="75%">
<stop stop-color="#cfdae1" stop-opacity=".44"/><stop offset=".29" class="rim-tone" stop-opacity=".31"/>
<stop offset=".65" class="rim-base" stop-opacity=".16"/><stop offset="1" class="rim-tone" stop-opacity=".27"/>
</linearGradient>
<linearGradient id="wash" x2="95%" y2="75%">
<stop class="rim-tone" stop-opacity=".105"/><stop offset=".3" class="rim-tone" stop-opacity=".025"/>
<stop offset=".72" class="rim-base" stop-opacity="0"/>
</linearGradient>
</defs>
<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="{radius}" class="plate" stroke="url(#rim)" stroke-width="1.7"/>
<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="{radius}" fill="url(#wash)"/>'''


def surface(width, height):
    """Use one quiet edge light on the outer plate; keep the inner tiles matte."""
    labels = ['#7d8590', '#94a3b6', '#a1adbd', '#c1ccd9', '#97a6b8', '#a2b0c2', '#b8c5d5']
    rules = [
        ('.plate', 'fill', 'base'), ('.glass-tile', 'fill', 'tile'),
        ('.glass-rule', 'stroke', 'rule'),
        *RIM_RULES,
        ('text[fill="#e6edf3"]', 'fill', 'ink'),
        (','.join(f'text[fill="{c}"]' for c in labels) + ',tspan[fill="#a2b0c2"]', 'fill', 'muted'),
        ('text[fill="#5fe3bb"],text[fill="#39d353"]', 'fill', 'sun'),
        ('.b', 'fill', 'dawn'),
        ('use[stroke="#5fe3bb"]', 'stroke', 'sun'),
        ('text[fill="#f6ad55"],.b[fill="#39d353"]', 'fill', 'peak'),
    ]
    return f'''<style>{themed_css(rules)}
.glass-rule{{stroke-opacity:.55}}
</style>
{glass_plate(width, height, radius=30)}
<path d="M22 44H{width-22}" class="glass-rule"/>'''
