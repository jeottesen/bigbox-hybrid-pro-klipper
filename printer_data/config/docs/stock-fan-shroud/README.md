# Stock BigBox Hybrid part-cooling fan parts (from E3D's STEP files)

## Stock single-head fan mount (most likely the stock part) - two printed pieces
From `bigbox_v1.1.0.stp` (the assembled Hybrid). The E3D manual says to "fix the two parts together back to back" with an M3 8mm screw and square nut, fit the 40x40x20 blower with an M3x22 screw, and use 2 x M3x30 screws for the fan corners; the dual head needs two assemblies. These two parts touch back to back, the dual model has four of them, and their bottoms sit about 1.4mm above the nozzle tip height.

- `stock_fan_mount_front_plate_print.stl` (46.0 x 54.2 x 23.3 print size, 9.8 cm3): the plate with the window and four corner holes. Printed flat, no supports expected.
- `stock_fan_mount_back_plate_with_foot_print.stl` (46.0 x 54.2 x 23.6, 8.2 cm3): the back plate with a foot at the bottom. Printed flat with the foot pointing up.
- `*_installed.step`: the same parts in installed orientation, corner at the origin, millimetres.

Not verified: identification is from shape, position and the manual's description (the STEP files have no part names), so compare with a physical duct or the photos before printing, and expect to check how the blower sits in it. Your aftermarket duct is not this part.

## Hybrid Dual-head arch duct (NOT the single-head stock part)
From `Hybrid_v1.1.0..stp`: an arched duct that feeds both sides of a nozzle, 50.5 x 60.5 x 63.0 mm.
- `stock_fan_shroud_plain.stl/.step` - the duct alone.
- `stock_fan_shroud_with_bridge_bar.stl/.step` - the same with a curved cross bar merged in.
- `stock_fan_bridge_bar_maybe.stl/.step` - the bar alone (role not verified).
Useful as a reference for a wrap-around duct, not as the replacement for the part now on the printer.

Print notes: PETG at minimum near the heater block; ASA/ABS/PC if possible. Original designs (c) E3D; licence not checked.
