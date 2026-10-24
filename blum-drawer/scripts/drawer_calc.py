#!/usr/bin/env python3
"""
Blum undermount drawer-box cut-list calculator.

Deterministic math so fractions are never wrong on real cuts. Encodes the
proven process from the user's own notes (Blum Tandem Plus BLUMOTION, 1/2"
plywood boxes), generalized to any material thickness and to Shaper-Origin
box-joint construction.

Core rule (from the notes, reconciled with the Blum spec sheet):
    inside_width  = opening_width - SLIDE_DEDUCTION   (default 1.625" ~= 42mm)
    exterior_width = inside_width + 2 * material_thickness
The "subtract 5/8" from the opening" shortcut in the notes == subtract 1.625"
to get inside width, then add back the two 1/2" sides (= opening - 5/8").

Joinery only changes the FRONT/BACK length:
    standard (front/back captured between sides): length = inside_width
    boxjoint (Shaper Origin finger joints, full corners): length = exterior_width
Sides are always the nominal slide length. The bottom is identical either way.

Usage:
    python3 drawer_calc.py config.json
    python3 drawer_calc.py -        # read JSON from stdin

Run with `python3 -I` if the config came from an untrusted/downloaded dir.
"""
import json
import sys
from fractions import Fraction

# --- defaults (overridable in the JSON config) ------------------------------
DEFAULTS = {
    "units": "in",
    "material_thickness": 0.5,   # drawer box sides/front/back (1/2" ply)
    "bottom_thickness": 0.25,    # 1/4" ply bottom
    "groove_depth": 0.25,        # 1/4"-deep groove for the bottom, all 4 sides
    "slide_deduction": 1.625,    # opening - this = inside width (Blum ~42mm)
    "construction": "standard",  # "standard" | "boxjoint"
    "slide_length": 21,          # NOMINAL slide length you bought (not measured)
    "carcass_depth": None,       # optional, for a fit sanity-check
    "round_to": 32,              # fraction denominator for display (16 or 32)
}

# Blum rear locking-device notch in the drawer BACK (bottom edge). You have a
# jig for this; these are the widths the notes call out so the cut list is complete.
NOTCH_STANDARD = 1.28   # notes
NOTCH_BOXJOINT = 1.78   # notes: +1/2" because the back runs full width


def parse_len(v):
    """Accept 25.469, '25 15/32', '25-15/32', '1 5/8', '5/8'."""
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace("-", " ")
    if " " in s:
        whole, frac = s.split(None, 1)
        return float(whole) + float(Fraction(frac))
    if "/" in s:
        return float(Fraction(s))
    return float(s)


def to_frac(x, denom=32):
    """Decimal inches -> ' 25 15/32' style string, rounded to nearest 1/denom."""
    f = Fraction(round(x * denom), denom)
    whole = int(f)
    rem = f - whole
    if rem == 0:
        return f'{whole}"'
    return f'{whole} {rem.numerator}/{rem.denominator}"' if whole else f'{rem.numerator}/{rem.denominator}"'


def dim(x, denom):
    return f'{to_frac(x, denom):<10} ({x:.4f})'


def compute(cfg):
    g = {**DEFAULTS, **cfg}
    t = parse_len(g["material_thickness"])
    bt = parse_len(g["bottom_thickness"])
    gd = parse_len(g["groove_depth"])
    ded = parse_len(g["slide_deduction"])
    denom = int(g["round_to"])

    out_drawers = []
    warnings = []
    for d in g["drawers"]:
        label = d.get("label", "?")
        qty = int(d.get("qty", 1))
        construction = d.get("construction", g["construction"])
        slide = parse_len(d.get("slide_length", g["slide_length"]))
        ow = parse_len(d["opening_width"])
        bh = parse_len(d["box_height"])

        inside_w = ow - ded
        exterior_w = inside_w + 2 * t
        fb_len = inside_w if construction == "standard" else exterior_w
        side_len = slide

        inside_depth = slide - 2 * t
        bottom_w = inside_w + 2 * gd           # spans between the sides
        bottom_d = inside_depth + 2 * gd       # spans between front & back
        notch = NOTCH_STANDARD if construction == "standard" else NOTCH_BOXJOINT

        cd = g.get("carcass_depth")
        if cd is not None and slide > parse_len(cd):
            warnings.append(f'[{label}] slide {slide}" exceeds carcass depth {cd}" — slide will not fit.')

        oh = d.get("opening_height")
        if oh is not None:
            max_h = parse_len(oh) - 0.8125  # opening height - 13/16"
            if bh > max_h:
                warnings.append(f'[{label}] box height {bh}" over max {max_h:.3f}" (opening_height - 13/16").')

        out_drawers.append({
            "label": label, "qty": qty, "construction": construction,
            "opening_width": ow, "inside_width": inside_w, "exterior_width": exterior_w,
            "box_height": bh, "slide_length": slide,
            "parts": {
                "sides":     {"qty": 2 * qty, "length": side_len, "height": bh, "thk": t},
                "frontback": {"qty": 2 * qty, "length": fb_len,  "height": bh, "thk": t},
                "bottom":    {"qty": 1 * qty, "width": bottom_w, "depth": bottom_d, "thk": bt},
            },
            "notch": notch,
        })
    return g, out_drawers, warnings, denom


def render(g, drawers, warnings, denom):
    t = parse_len(g["material_thickness"]); bt = parse_len(g["bottom_thickness"])
    gd = parse_len(g["groove_depth"]); ded = parse_len(g["slide_deduction"])
    L = []
    L.append("=" * 70)
    L.append("BLUM UNDERMOUNT DRAWER — CUT LIST")
    L.append("=" * 70)
    L.append(f'Material: {t}" box / {bt}" bottom   Groove: {gd}" deep   '
             f'Opening deduction: {ded}" (~42mm)')
    L.append("")

    for d in drawers:
        p = d["parts"]
        L.append(f'--- Drawer {d["label"]}  (x{d["qty"]}, {d["construction"]} joinery, '
                 f'{d["slide_length"]:g}" slides) ---')
        L.append(f'  opening width {to_frac(d["opening_width"], denom)}  ->  '
                 f'inside {to_frac(d["inside_width"], denom)} / '
                 f'exterior {to_frac(d["exterior_width"], denom)}')
        L.append(f'  SIDES      x{p["sides"]["qty"]:<3} {dim(p["sides"]["length"],denom)} long  x  '
                 f'{dim(p["sides"]["height"],denom)} high   ({t:g}")')
        L.append(f'  FRONT/BACK x{p["frontback"]["qty"]:<3} {dim(p["frontback"]["length"],denom)} long  x  '
                 f'{dim(p["frontback"]["height"],denom)} high   ({t:g}")')
        L.append(f'  BOTTOM     x{p["bottom"]["qty"]:<3} {dim(p["bottom"]["width"],denom)} wide  x  '
                 f'{dim(p["bottom"]["depth"],denom)} deep   ({bt:g}")')
        L.append(f'  rear notch in BACK: {d["notch"]}" wide (use your jig)')
        L.append("")

    # consolidated cut list grouped by part + dimension
    L.append("=" * 70)
    L.append("CONSOLIDATED (group identical pieces at the saw)")
    L.append("=" * 70)
    groups = {}
    for d in drawers:
        p = d["parts"]
        for key, dims in (
            ("SIDE",      (p["sides"]["length"], p["sides"]["height"], t)),
            ("FRONT/BACK",(p["frontback"]["length"], p["frontback"]["height"], t)),
            ("BOTTOM",    (p["bottom"]["width"], p["bottom"]["depth"], bt)),
        ):
            qty = p["sides"]["qty"] if key == "SIDE" else (
                p["frontback"]["qty"] if key == "FRONT/BACK" else p["bottom"]["qty"])
            gkey = (key, round(dims[0], 4), round(dims[1], 4), round(dims[2], 4))
            groups[gkey] = groups.get(gkey, 0) + qty
    for (key, a, b, thk), qty in sorted(groups.items()):
        unit = "long x _ high" if key != "BOTTOM" else "wide x _ deep"
        L.append(f'  {qty:>3} x  {key:<10} {to_frac(a,denom):<9} x {to_frac(b,denom):<9}  ({thk:g}")')

    if warnings:
        L.append("")
        L.append("!! WARNINGS")
        for w in warnings:
            L.append("   " + w)

    L.append("")
    L.append("BUILD NOTES")
    L.append("  - Side length = NOMINAL slide length you bought, not a measured slide.")
    L.append("  - Bottom groove: 1/4\" wide, 1/4\" deep, on all 4 pieces; bottom floats in it.")
    L.append("    (Box joints: run the groove with the Shaper before glue-up.)")
    L.append("  - Standard joinery: front/back are captured BETWEEN the sides.")
    L.append("  - Box joints: front/back run the FULL exterior width; notch is +1/2\" wider.")
    L.append("  - Verify groove height off the bottom edge + rear-bracket setback against")
    L.append("    the Blum sheet for your slide, and dry-fit ONE box before batching.")
    return "\n".join(L)


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    src = sys.argv[1]
    raw = sys.stdin.read() if src == "-" else open(src).read()
    cfg = json.loads(raw)
    g, drawers, warnings, denom = compute(cfg)
    print(render(g, drawers, warnings, denom))


if __name__ == "__main__":
    main()
