# Assembly B: owner-supplied "BB Dual with original Z Stop Position Part Fan Shroud" + V6 + carriage

All STL files share one coordinate frame (the E3D Hybrid model's frame, mm), so importing them together reproduces the assembly with no offsets. `assembly_all.stl` is the lot in one file; `preview.png` shows three views. (A STEP of the faceted shroud was 68 MB, so the parts are STL; the carriage and V6 can be regenerated as STEP with `build_B2.py`.)

Parts: `carriage.stl` (Hybrid carriage, Hybrid STEP solid #1), `shroud.stl` (the owner's file as supplied; it is already in this frame, bounds X -79..1.2, Y 283..358.5, Z 635.1..696.4), `v6.stl` (hotend only, at hotend slot 1: X -62.4, Y 308.0, tip Z 635.6), `sock_approx.stl` (box-shell stand-in, not the real sock).

What checks out (voxel overlap tests at 0.5 mm):
- The shroud overlaps the Hybrid carriage by **0 mm3**, so it was designed for that carriage (it touches the single-hotend carriage from `bigbox_v1.1.0`, which has extra tabs, by about 29 mm3).
- The V6 fits the shroud's C-ring at slot 1 in **exactly one** of four orientations tried (heater block long side toward -X, out through the ring's open side, zero overlap); the other three overlap by 31 to 53 mm3. That supports the nozzle position and the shroud's frame.
- The shroud is a thin-walled half ring around the nozzle with an arch over the top and two prongs 35 mm apart (Y 315 and 350) with a 26.8 mm gap between them.

Not known: **where and how the blower mounts**. Candidates are between the prongs or against the arch with the outlet feeding the slab at Z about 684 (X -10.6..-0.6, Y 311..353.6) or the tilted tube; none could be settled from the shape alone, so the blower is left out.

## Blower placement as shown by the owner (2026-10-29)
Three views from the owner's CAD (`owner_blower_placement_1_front3q.png`, `_2_face_on.png`, `_3_rear3q.png`; the dark blue part is the 4020 blower). What they show:
- The blower's flat round face with its four ears sits **in the shroud's large tilted ring** (the ring with the screw holes, the "arch"), the ears lining up with the ring's holes, with only a thin gap around the body (tight tolerance). The ring leans back, so the blower is tilted with it.
- The blower's **outlet is the flat bottom edge**, pointing down at the shroud's slab with the rectangular opening, which leads on to the C-ring around the nozzle (image 3 shows the outlet sitting over that opening).
- Earlier placement searches (`find_blower.py`, `place_blower_*.py`) used a simplified blower (disc, channel and box ears), not the owner's blower STEP, and the shroud is a faceted STL, so tight clearances showed up as overlaps of 180-290 mm3. That overlap does not mean the blower can't sit here.
