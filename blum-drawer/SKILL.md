---
name: blum-drawer
description: >-
  Size and generate a cut list for Blum undermount drawer boxes via a short
  interview. Use whenever building, sizing, or cutting drawers / drawer boxes
  for Blum Tandem Plus (BLUMOTION) or other undermount slides — "build a
  drawer", "drawer cut list", "size my drawer boxes", "how wide do I cut the
  drawer", including Shaper Origin box-joint construction. Woodworking, not code.
---

# Blum undermount drawer builder

Turns a cabinet opening into an exact drawer-box cut list. Drives a short
interview, then runs `scripts/drawer_calc.py` so the fraction math is never
wrong on real cuts. Defaults to the user's usual slide: **Blum Tandem Plus
BLUMOTION, full-extension soft-close, 1/2" plywood boxes**.

See `reference/blum-tandem-plus-specs.md` for the formula derivations and the
verified numbers these defaults come from.

## How it works (the one rule)

`inside_width = opening_width − 1.625"` (Blum's ~42mm). Everything else derives:
- `exterior_width = inside_width + 2 × material_thickness`
- Standard joinery → front/back = `inside_width` (captured between the sides)
- Box joints (Shaper Origin) → front/back = `exterior_width` (full corners)
- Sides = **nominal slide length** (what you bought, e.g. 21" — not a measured slide)
- Bottom floats in a 1/4"-deep groove on all four pieces: `+1/2"` on each inside dim

## Interview

Ask only what you don't already know; batch related questions. Accept fractions
like `27 3/32` or decimals. Don't re-ask anything the user already gave.

1. **Opening(s)** — width × height of each cabinet opening. For a bank of
   drawers sharing one width, take the width once + each height. Width is
   what matters most; height just sets the box height.
2. **Block runners / spacers?** — if the drawer must clear doors, hinges, or a
   face frame, subtract runner thickness from BOTH sides first:
   `effective_opening = measured_opening − 2 × runner_thickness`. Use the
   effective opening as the opening_width. (Island example: 1.25" runners.)
3. **Construction** — standard (front/back between the sides) or **Shaper Origin
   box joints** (full corners). This is the only thing that changes front/back length.
4. **Slide length** — nominal length bought (21" default). If you know the
   carcass depth, pass `carcass_depth` so it can warn if the slide won't fit.
5. **Box height** — per opening. Guidance: max = `opening_height − 13/16"`. For an
   applied/inset face that overhangs the box, pick a bit under the opening
   (the console used ~5" boxes behind 6" face openings). Confirm the number.
6. **Material** — defaults: 1/2" box sides, 1/4" bottom, 1/4"-deep grooves. Only
   ask if they're using something else.

## Run it

Build a JSON config and run from the skill dir (use `-I`; the script is ours but
the config may be anywhere):

```bash
python3 -I ~/.claude/skills/blum-drawer/scripts/drawer_calc.py /tmp/drawers.json
```

Config shape (per-drawer `construction` / `slide_length` / `opening_height`
optional, override the top-level default):

```json
{
  "construction": "standard",
  "slide_length": 21,
  "carcass_depth": 22.75,
  "drawers": [
    {"label": "top", "qty": 2, "opening_width": "27 3/32", "box_height": 6.25}
  ]
}
```

Top-level overrides when needed: `material_thickness`, `bottom_thickness`,
`groove_depth`, `slide_deduction` (default 1.625), `round_to` (16 or 32).

## Visual plans (3D + dimensioned drawings)

When the user wants to *see* it (or always, for a build), generate a
self-contained HTML plan sheet from the SAME config:

```bash
python3 -I ~/.claude/skills/blum-drawer/scripts/render_drawer.py CONFIG.json OUT.html
```

It produces an interactive three.js box (explode slider, per-drawer selector,
spin, dimension sprites) plus per-drawer dimensioned SVG shop drawings — FRONT
elevation, SIDE section, and an EXPLODED "cut these pieces" layout with every
measurement spelled out in fractions. Save it next to the project's other plans
(e.g. `plans/drawer-box-plans.html`) and save the config beside it so it's
reproducible. To screenshot headless for a quick look, Chrome needs a software
GL backend: `--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader`.

## Present

Show the script output (per-drawer + consolidated group-at-the-saw list). Then
remind: **dry-fit one box before batching**, and verify the bottom-groove height
off the box bottom edge + the rear-bracket setback against the Blum sheet for
that specific slide — those are the two things that vary by series and aren't in
the cut list. The rear-notch width is in the output (use the jig).
