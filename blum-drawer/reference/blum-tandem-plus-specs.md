# Blum undermount drawer — verified specs & formula derivations

Source of truth for the `blum-drawer` skill. Numbers below are from the user's
own built-and-working drawers (entertainment-console build + kitchen island +
coffee cabinet) cross-checked against the Blum spec sheet.

## The slide (default)

**Blum Tandem Plus BLUMOTION, 21" undermount, full extension, soft-close,
100 lb.** Kit ships with the slides, soft-close/BLUMOTION, locking devices, rear
mounting brackets, and screws (608N / 606P). Nominal lengths: 9, 12, 15, 18, 21.

> The console build used **Movento 760H** instead. Movento may use a different
> opening deduction than the 1.625" below — treat `slide_deduction` as
> series-specific and verify on that slide's sheet.

## The one constant: 1.625" (~42 mm)

Blum's chart says **inside drawer width = cabinet opening − 42 mm**. 42 mm =
1.654"; the user rounds to **1.625" (1⅝")** and it works. So:

```
inside_width   = opening_width − 1.625
exterior_width = inside_width + 2 × material_thickness
```

The notes' shortcut "subtract 5/8" from the opening to get the exterior width"
is the same thing for 1/2" material: `−1.625 + 2×0.5 = −0.625 = −5/8"`. Proof
(Example #3): `27.094 − 1.625 = 25.469"` front/back — matches the notes exactly.

## Joinery is the only fork

| Part        | Standard (notes)             | Shaper box joints          |
|-------------|------------------------------|----------------------------|
| Sides       | nominal slide length         | nominal slide length       |
| Front/back  | `inside_width`               | `exterior_width` (full)    |
| Bottom      | identical                    | identical                  |
| Rear notch  | 1.28"                        | 1.78" (+1/2")              |

Standard = front/back captured between the sides. Box joints = all four corners
interlock, so front/back run the full exterior width. With box joints, cut the
bottom groove on the Shaper before glue-up.

## Bottom (1/4" ply, floats in 1/4"-deep grooves all four sides)

```
bottom_width = inside_width  + 2 × 0.25   (= inside_width + 1/2")
bottom_depth = (slide − 2t)  + 2 × 0.25   (= slide − 2t + 1/2")
```

Box depth = side length = nominal slide length, so inside depth = `slide − 2t`.
Example #3 (9" slides, 1/2"): `9 − 1 + 0.5 = 8.5"` deep;
`25.469 + 0.5 = 25.969" = 25 31/32"` wide. Both match the notes.

## Height

Max box height = `opening_height − 13/16"` (Blum 20 mm top clearance). For an
applied/inset drawer face that overhangs the box, the box is usually a bit
shorter than the opening (console: ~5" boxes behind 6" face openings). Box
height is a design choice bounded by that max.

## Block runners / spacers

To clear doors, hinges, or a face frame, add runner strips on each cabinet wall,
then compute off the reduced opening:
`effective_opening = measured_opening − 2 × runner_thickness` (island: 1.25" runners).

## Still verify per slide (not in the cut list)

- Bottom-groove **height off the box bottom edge** (undermount engagement).
- Rear mounting-bracket **setback/height**.
- Dry-fit **one** box before batching a bank of drawers.
