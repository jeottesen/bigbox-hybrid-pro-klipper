# Assembly: carriage + stock fan mount + 4020 blower + V6 hotend

`assembly_stock_fan_mount.step` - named, coloured parts: `carriage`, `front_plate`, `back_plate` (the two-piece stock fan mount), `blower_housing`, `blower_impeller` (owner's 4020 blower STEP), and the V6 hotend as `v6_nozzle`, `v6_block`, `v6_heatbreak`, `v6_heatsink` (hotend only, no 30mm fan). Frame: the E3D Hybrid model's own coordinates in mm (X across the rods, Y along the rods, Z up); hotend axis X=-62.4, Y=308.0, nozzle tip Z=635.6.

**Correction (2026-10-28):** the first version of this assembly had the blower turned with its outlet pointing UP. That was my error. It is fixed: the blower outlet faces down onto the mount's tray, its ear face is against the back plate (Y 344.2 to 364.2), and the outlet gap (X -70.9 to -43.6) lines up with the three slanted windows in the tray top (X -71 to -43, Y 346 to 362.5). That match leaves only one possible orientation, so there is no longer a second variant.

- Also consistent: the blower's three ear holes (35mm square) match the mount's hole pattern, and the blower rests on the mount's foot.
- No volume overlaps between any pair of parts (boolean check).
- Not verified: the V6 block orientation (long side points away from the fan, -Y), and the carriage is the E3D single-hotend carriage from `bigbox_v1.1.0.stp`.
- The arch duct from the dual-head parts list is not assembled (owner says it is the dual-head part).
- `build_assembly.py` regenerates it (CadQuery; needs the source STEP files).
