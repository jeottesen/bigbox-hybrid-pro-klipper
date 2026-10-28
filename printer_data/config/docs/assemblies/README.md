# Assemblies: carriage + stock fan mount + 4020 blower + V6 hotend

Frame: the E3D Hybrid model's own coordinates in mm (X across the rods, Y along the rods, Z up). Hotend axis at X=-62.4, Y=308.0; nozzle tip Z=635.6.

Each STEP holds named, coloured parts: `carriage`, `front_plate`, `back_plate` (the two-piece stock fan mount), `blower_housing`, `blower_impeller` (owner's 4020 blower STEP), and the V6 hotend as `v6_nozzle`, `v6_block`, `v6_heatbreak`, `v6_heatsink` (hotend only, no 30mm fan).

- `assembly_stock_fan_mount_blower_ears_to_plate.step`: blower with its ear/hub face against the back plate (Y 344.2 to 364.2).
- `assembly_stock_fan_mount_blower_inlet_to_plate.step`: same position, blower turned around so the open inlet faces the plate windows.
- Placement basis: the blower's three ear holes (35mm square) match the mount's four hole pattern (-79.9/-44.9 in X, 650.1/685.1 in Z, centre Z=667.6), the foot under the mount ends where the blower back face ends, and the blower bottom (Z 647.4) rests on the foot. No volume overlaps were found between any pair of parts (checked with boolean intersections).
- Not verified: which way round the blower goes (the two files cover both), the V6 block orientation (its long side points away from the fan, -Y), and the carriage here is the E3D single-hotend carriage from `bigbox_v1.1.0.stp`, which may differ from the one on the printer.
- The arch duct from the Hybrid dual-head parts list is not assembled: the owner said it is the dual-head part. It can be added on request.
- `build_assembly.py` regenerates both (CadQuery; needs the source STEP files).
