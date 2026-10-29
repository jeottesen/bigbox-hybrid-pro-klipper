# Cheap CPU airflow test of the stock single-head fan mount

Lattice-Boltzmann (D3Q19 BGK, Python + numba, 4 CPU cores, no GPU): `voxel.py` voxelises the assembly on a 1 mm grid, `lbm.py` runs it, `post.py` makes the maps and numbers. Run: `python voxel.py 1.0; python lbm.py grid_1.00.npz 4000 0.012 0.04 run1.npz 1000; python post.py run1.npz run1.png`. About 80 s for 4000 steps on 0.46M cells.

Model: a velocity inlet over the tray windows (blower outlet) scaled to 3 m/s at the windows (roughly 1 L/s, a guess from the vendor 3.2 CFM free-air rating), open sides, solid walls from the CAD, no silicone sock, no blower internals.

**Limits (read before trusting any number):** it is deliberately artificial. The viscosity is about 60x air to keep the solver stable at 1 mm cells, so the real jet would be sharper and more turbulent; the inlet flow is imposed, not set by the fan curve; walls about 1 mm thick are only one cell across; one orientation of the heater block. Treat it as a map of where the air goes, not a measurement.

Result for the stock mount (`run1_stock_fan_mount.png`): the air passes through the three windows into the tray, splits into side channels and a centre chevron, leaves the front edge at roughly 45 degrees downward and forward at about Y 318-325 (7-10 mm behind the nozzle axis) and passes below the tip; speed right at the nozzle is low, with a curtain of faster air on the fan side. About 71% of the outflow leaves downward and 28% forward; left and right of the nozzle are about equal (about 1.2 m/s in the tip zone).

## Run 2: with an approximate silicone sock
The supplied sock (Onset Engineering, Fusion 360 `.f3d`) holds its geometry in Autodesk's proprietary `.smb` format and could not be opened here, so `voxel.py 1.0 sock` adds a stand-in: an open-top box shell (23.5 x 19.5 mm, 1.5 mm walls, from 1.5 mm below the heater block to 1.5 mm above it) with a hole for the nozzle. Exporting that sock as STEP or STL would let it be used as is.

Tip zone (mean air speed within 10 mm of the nozzle axis, Z 633-640, at the same imposed flow): **no sock 0.87 m/s, approximate sock 0.78 m/s** (about 10% lower); front of the nozzle 0.76 vs 0.65 m/s; fan side 1.69 vs 1.67 m/s; share leaving downward / forward 71% / 28% vs 74% / 24%. The pattern is the same: the jet leaves behind the nozzle and passes below the tip, and the sock changes it only a little because the exit is 7-10 mm from the nozzle axis. Image: `run2_stock_fan_mount_with_approx_sock.png`.

## Run 3: finer grid (0.75 mm), approximate sock, lower artificial viscosity
`python voxel.py 0.75 sock; python lbm.py grid_0.75_sock.npz 6000 0.010 0.04 run3.npz 2000; python post.py run3.npz run3.png` (about 5 minutes on 4 CPU cores, 1.1M cells). A 0.5 mm attempt (3.7M cells) was killed twice while running in the background (the tool reported a restart; the machine's uptime shows it did not reboot, and the cause was not verified, memory on this 4 GB machine is the likely one), so it was not completed.

| Same imposed flow, tip zone (within 10 mm of the nozzle axis, Z 633-640) | 1.0 mm, sock | 0.75 mm, sock |
|---|---|---|
| mean air speed | 0.78 m/s | 0.92 m/s |
| front of the nozzle | 0.65 m/s | 0.76 m/s |
| fan side | 1.67 m/s | 2.32 m/s |
| left / right of the nozzle | 1.15 / 1.20 | 1.56 / 1.51 |
| leaving downward / forward | 74% / 24% | 73% / 26% |

The picture is unchanged: the air passes through the three tray windows, leaves the front edge at about 45 degrees downward and forward 7-10 mm behind the nozzle axis, and goes below the tip; air at the nozzle itself stays slow while the fan side gets a fast curtain. The finer, less viscous run makes the jets sharper (fan side 2.3 m/s) but does not move them. Image: `run3_075mm_with_approx_sock.png`. Same caveats as run 1 (imposed flow, still artificial viscosity of about 45x air, approximate sock).

## Hero Me baseline: what was established and what blocked it (not simulated)
Goal: a Hero Me (V6 + base + skirt + 4020 duct) baseline without the BigBox gantry, with the duct height set digitally using the Duct Offset Check gauge, then the same airflow test. Not run, because the Hero Me STL files are not in a shared assembly frame and the information needed to assemble them is in the paid assembly guide, not in the pack.
- **Established:** the gauge is a flat shim with two pads about 17 mm either side of the nozzle hole (X) and about 5 mm behind it (Y), 1.6 mm thick. The left and right 4020 ducts mirror about a plane that puts the nozzle axis at X about -142.4 in the `4020W` file frame (the right duct's bounds are the left duct's mirrored within 1 mm), and the left duct's tip landing area sits about 17 mm from that plane, matching the gauge pads, so the nozzle position in the duct frame is probably right. The duct tips then sit 1.6 mm above the nozzle tip, which in the duct frame (lowest point Z 5.87 for the W duct, 6.71 for the L duct) puts the nozzle tip at Z about 4.3 (W) or 5.1 (L).
- **Not established:** where the blower's outlet meets the duct (the duct's inlet face and its three ear holes could not be located reliably from the mesh), how the duct's mounting slots sit on the base, and the skirt's position (its screw holes are 28 mm from its nozzle notch, which does not match any hole pair found on the base). A simulation built on guessed inlet and mount positions would not be a fair baseline.
- **Ways to unblock:** the Hero Me assembly guide pages or an assembled Hero Me STEP, or the position of the blower relative to the duct (a photo of a built Hero Me duct from the side).

## Rough Hero Me-style run (owner asked for a best guess): result is NOT valid
Built `voxel_hero.py`: Hero Me 4020W left duct + V6 + approximate sock in the duct file's frame, nozzle at X -142.4, Y 22.0 (from the gauge and mirror symmetry), nozzle tip at Z 4.27 so the duct tips sit 1.6 mm above it, no base or skirt (their placement could not be established), flow injected inside the duct's slanted tube at Z 30 along the tube axis because the blower interface could not be found. Run at equal volumetric flow (about 0.39 L/s) against the stock mount (`lbm2.py`, viscosity 0.006 lattice units, same time step).
- **Result:** no air reaches the nozzle (all speeds near zero within 15 mm of the tip), and the duct pressurises (peak density 1.18 against 1.02 for the stock mount). The channel is connected from the inlet to the tip level in the voxel model at 1 mm, so the likely causes are the 1 mm grid being too coarse for the duct's thin passages and my guessed inlet. A 0.6 mm voxelisation leaks into the outside in the connectivity test, so the walls are not closed there either. This is a failure of the model, not a finding about the Hero Me duct. Image: `run4_hero_rough_INVALID.png`.
- **Stock mount at the same 0.39 L/s** (valid for comparison with future designs, same settings): mean speed within 10 mm of the nozzle axis 0.15 m/s in the tip zone (0.41 m/s just below the tip), `run4_stock_equal_flow.png`.

## Hero Me photos from the owner (2026-10-28) and why the Hero Me comparison still isn't valid
Photos of a Hero Me on an Ender 3 (yellow base, 4020 axial heatsink fan in the front, two blue 4020 ducts with a 4020 blower each) show: one blower on each side of the base with its round face outward, its outlet pointing down into the duct (the blowers look tilted about 30 degrees, matching the duct's tilted inlet face); the ducts are separate left and right parts, each with a tall slotted plate and a floor that sweeps in to the nozzle, with the tips close to the nozzle on both sides. This confirms the layout but not exact positions.
Why no valid run: the first rough attempt stalled (no flow past the duct's thin passages, pressure rising to about 40 mmH2O-equivalent), which points to channel details finer than the 1 mm grid, and the 0.5 mm and 0.6 mm grids are at or beyond what this machine handled (0.5 mm over the whole domain was killed twice, cause not verified). Also the artificial viscosity (about 30x air) inflates losses in narrow passages, so duct-versus-duct pressure comparisons are not trustworthy here. A fair Hero Me comparison would need a grid of about 0.3 mm around the duct, or a different solver. The stock-mount numbers at equal flow stay valid as a reference for comparing new designs of the same kind.

## Run 5: 0.5 mm grid (lower memory) and a correction: the earlier runs had no print bed
- The 0.5 mm run finished (`run5_050mm_with_approx_sock.png`; 2.7M cells, 8000 steps, about 20 minutes; the first two attempts were killed while voxelising because `trimesh.voxelized` used over 1 GB at that pitch, so `voxel_fine.py` now samples the surface in chunks and used about 150 MB). Same picture as the 1 mm and 0.75 mm runs with sharper jets (tip zone 1.83 m/s mean).
- **Correction:** runs 1 to 5 had no bed, so the jet simply continued below the nozzle tip, and I described it as "passing below the tip". In a real print the bed (or the top of the print) is a fraction of a millimetre under the tip, so that jet would hit the surface and spread along it. Run 6 adds a bed 0.3 mm under the tip (`post_bed.py`, 1 mm grid, same settings as run 2):

| Stock mount with a bed, air speed 0.3-3.3 mm above the bed, 3-20 mm from the nozzle | mean |
|---|---|
| +X side | 2.05 m/s |
| +Y (fan side) | 2.03 m/s |
| -X side | 1.92 m/s |
| **-Y (front of the nozzle)** | **0.12 m/s** |

So with a bed the stock mount does put fast air on the surface around the nozzle on three sides, and leaves the **front side** almost unserved (about 16x less). That, not "the jet misses the nozzle", is the better description of the stock mount's weakness in this model (same caveats: imposed flow, artificial viscosity, no real sock). Image: `run6_stock_with_bed.png`.

## New BB Dual shroud: blower position still undetermined
The shroud (owner file) fits the Hybrid carriage with zero overlap and the V6 at slot 1 in exactly one orientation (see `assemblies/bb-dual-shroud`). For the blower: putting it in the arch ring along X overlaps the shroud by 180-290 mm3 in all eight poses tried; a brute-force search over all 24 orientations and every position (`find_blower.py`) finds about 75,000 collision-free poses touching the shroud, and none whose outlet sits in a clearly enclosed mouth (best enclosure score 0.155), so the shape alone does not settle it. Not simulated.

## Run B: new BB Dual shroud with a guessed blower pose: result is NOT valid
The previous session built `voxel_B.py` (owner's shroud, Hybrid carriage, V6 at slot 1, approximate sock, bed 0.3 mm under the tip, 1 mm grid) with a blower body placed along the tilted screw-hole axis (`place_blower_tilt.py`) and flow injected at its outlet slot. The run finished but was never written up. Post-processed with `post_bed.py` (nozzle at X -62.4, Y 308.0, bed Z 635.3): **air speed within 25 mm of the nozzle, 0.3 to 5.3 mm above the bed, is 0.00 m/s in every sector.** The map (`runB_new_shroud_blower_guess_INVALID.png`) shows the jet dropping straight down at X about -20, beside the shroud, never entering its mouth.
- This is a failure of the guessed blower pose (the outlet is not coupled to the shroud), not a finding about the shroud. No comparison with the stock mount (front sector 0.12 m/s, other sides about 2 m/s) can be drawn from it.
- Still needed to unblock: where the blower sits relative to the shroud (a photo of the owner's shroud with the blower fitted, or the blower's mounting screw positions on the shroud).
