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
    "base":  ((.205, .014, 222), (.967, .009, 165)),
    "tile":  ((.248, .014, 215), (.938, .011, 168)),
    "rule":  ((.42, .021, 195), (.77, .020, 178)),
    "quiet": ((.48, .020, 185), (.66, .025, 178)),
    "line":  ((.66, .043, 174), (.49, .047, 175)),
    "sun":   ((.83, .062, 168), (.48, .074, 168)),
    "peak":  ((.83, .094, 80),  (.49, .088, 70)),
    "ink":   ((.94, .010, 155), (.25, .024, 204)),
    "muted": ((.77, .018, 175), (.43, .028, 193)),
}


def themed_css(rules):
    """Emit concrete colors, including a dark default for non-CSS-media renderers."""
    themes = []
    for i in range(2):
        themes.append('\n'.join(f'{selector}{{{prop}:{srgb(*SWATCHES[role][i])}}}'
                                for selector, prop, role in rules))
    return themes[0] + '\n@media(prefers-color-scheme:light){' + themes[1] + '}'


def surface(width, height):
    """Use one quiet edge light on the outer plate; keep the inner tiles matte."""
    labels = ['#7d8590', '#94a3b6', '#a1adbd', '#c1ccd9', '#97a6b8', '#a2b0c2', '#b8c5d5']
    rules = [
        ('.plate', 'fill', 'base'), ('.glass-tile', 'fill', 'tile'),
        ('.glass-rule,.plate-edge', 'stroke', 'rule'),
        ('text[fill="#e6edf3"]', 'fill', 'ink'),
        (','.join(f'text[fill="{c}"]' for c in labels) + ',tspan[fill="#a2b0c2"]', 'fill', 'muted'),
        ('text[fill="#5fe3bb"],text[fill="#39d353"],.b', 'fill', 'sun'),
        ('use[stroke="#5fe3bb"]', 'stroke', 'sun'),
        ('text[fill="#f6ad55"],.b[fill="#39d353"]', 'fill', 'peak'),
    ]
    return f'''<style>{themed_css(rules)}
.glass-rule{{stroke-opacity:.55}}.plate-edge{{stroke-opacity:.65}}
</style>
<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="30" class="plate plate-edge"/>
<path d="M6 19Q12 1 32 1H{width*.37:.1f}" fill="none" stroke="white" stroke-opacity=".12"/>
<path d="M22 44H{width-22}" class="glass-rule"/>'''
