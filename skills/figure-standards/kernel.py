"""Helpers for the figure-standards skill.

Deliberately small: `figure-style` already ships the plotting helpers. These two
cover the one thing it asks for but does not provide - an actual colour-vision
deficiency simulation to test a palette against.
"""

OKABE_ITO = ("#000000", "#E69F00", "#56B4E9", "#009E73",
             "#F0E442", "#0072B2", "#D55E00", "#CC79A7")

OKABE_ITO_NAMES = ("black", "orange", "sky blue", "bluish green",
                   "yellow", "blue", "vermillion", "reddish purple")


def okabe_ito(n=8, include_black=True):
    """Okabe & Ito colour-universal-design qualitative palette (hex strings).

    Eight hues chosen to stay distinguishable under protanopia, deuteranopia and
    tritanopia. Source: Okabe M & Ito K, "Color Universal Design", jfly.uni-koeln.de.

    n               how many colours to return (max 8, or 7 without black)
    include_black   keep '#000000' as the first entry
    """
    pal = list(OKABE_ITO) if include_black else list(OKABE_ITO[1:])
    if n > len(pal):
        raise ValueError("okabe_ito: n=%d exceeds the %d available colours" % (n, len(pal)))
    return pal[:n]


def cvd_check(colors, kind="deuteranopia", delta_e_threshold=15.0, labels=None):
    """Simulate colour-vision deficiency and flag confusable pairs.

    Implements the Vienot, Brettel & Mollon (1999) linear dichromat approximation,
    then measures pairwise CIE76 dE in CIELAB on the simulated colours. Pairs below
    `delta_e_threshold` are reported as confusable.

    colors               list of '#rrggbb' strings
    kind                 'deuteranopia' | 'protanopia' | 'normal'
    delta_e_threshold    dE below which two colours are called confusable. 15 is a
                         working heuristic for distinct *categorical* series at
                         small mark sizes, not a standards-body value - tighten it
                         for large filled areas, loosen it for thick lines.
    labels               optional names, same order as `colors`, used in the report

    Returns {'kind', 'simulated', 'min_delta_e', 'confusable': [(a, b, dE), ...],
             'ok': bool}. `ok` is True when no pair falls below the threshold.
    """
    import numpy as np

    def to_linear(arr):
        return np.where(arr <= 0.04045, arr / 12.92, ((arr + 0.055) / 1.055) ** 2.4)

    def to_srgb(arr):
        arr = np.clip(arr, 0.0, 1.0)
        return np.where(arr <= 0.0031308, arr * 12.92, 1.055 * arr ** (1 / 2.4) - 0.055)

    def hex_to_rgb(h):
        h = h.lstrip("#")
        if len(h) != 6:
            raise ValueError("cvd_check: expected '#rrggbb', got %r" % h)
        return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)])

    def rgb_to_hex(rgb):
        v = np.clip(np.round(rgb * 255), 0, 255).astype(int)
        return "#%02x%02x%02x" % tuple(v)

    def rgb_to_lab(rgb_lin):
        m = np.array([[0.4124, 0.3576, 0.1805],
                      [0.2126, 0.7152, 0.0722],
                      [0.0193, 0.1192, 0.9505]])
        xyz = m @ rgb_lin
        white = np.array([0.95047, 1.0, 1.08883])
        t = xyz / white
        f = np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16.0 / 116.0)
        return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])

    # Vienot et al. 1999, sRGB-space dichromat projection matrices
    mats = {
        "protanopia":   np.array([[0.11238, 0.88762, 0.00000],
                                  [0.11238, 0.88762, 0.00000],
                                  [0.00401, -0.00401, 1.00000]]),
        "deuteranopia": np.array([[0.29275, 0.70725, 0.00000],
                                  [0.29275, 0.70725, 0.00000],
                                  [-0.02234, 0.02234, 1.00000]]),
        "normal":       np.eye(3),
    }
    if kind not in mats:
        raise ValueError("cvd_check: kind must be one of %s" % sorted(mats))

    names = list(labels) if labels is not None else list(colors)
    if len(names) != len(colors):
        raise ValueError("cvd_check: labels and colors must be the same length")

    sim_hex, labs = [], []
    for h in colors:
        lin = to_linear(hex_to_rgb(h))
        proj = mats[kind] @ lin
        sim_hex.append(rgb_to_hex(to_srgb(proj)))
        labs.append(rgb_to_lab(np.clip(proj, 0.0, 1.0)))

    confusable, min_de = [], float("inf")
    for i in range(len(labs)):
        for j in range(i + 1, len(labs)):
            de = float(np.linalg.norm(labs[i] - labs[j]))
            min_de = min(min_de, de)
            if de < delta_e_threshold:
                confusable.append((names[i], names[j], round(de, 1)))

    return {"kind": kind,
            "simulated": sim_hex,
            "min_delta_e": round(min_de, 1) if labs else None,
            "confusable": sorted(confusable, key=lambda r: r[2]),
            "ok": not confusable}
