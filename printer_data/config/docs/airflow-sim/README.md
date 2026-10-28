# Cheap CPU airflow test of the stock single-head fan mount

Lattice-Boltzmann (D3Q19 BGK, Python + numba, 4 CPU cores, no GPU): `voxel.py` voxelises the assembly on a 1 mm grid, `lbm.py` runs it, `post.py` makes the maps and numbers. Run: `python voxel.py 1.0; python lbm.py grid_1.00.npz 4000 0.012 0.04 run1.npz 1000; python post.py run1.npz run1.png`. About 80 s for 4000 steps on 0.46M cells.

Model: a velocity inlet over the tray windows (blower outlet) scaled to 3 m/s at the windows (roughly 1 L/s, a guess from the vendor 3.2 CFM free-air rating), open sides, solid walls from the CAD, no silicone sock, no blower internals.

**Limits (read before trusting any number):** it is deliberately artificial. The viscosity is about 60x air to keep the solver stable at 1 mm cells, so the real jet would be sharper and more turbulent; the inlet flow is imposed, not set by the fan curve; walls about 1 mm thick are only one cell across; one orientation of the heater block. Treat it as a map of where the air goes, not a measurement.

Result for the stock mount (`run1_stock_fan_mount.png`): the air passes through the three windows into the tray, splits into side channels and a centre chevron, leaves the front edge at roughly 45 degrees downward and forward at about Y 318-325 (7-10 mm behind the nozzle axis) and passes below the tip; speed right at the nozzle is low, with a curtain of faster air on the fan side. About 71% of the outflow leaves downward and 28% forward; left and right of the nozzle are about equal (about 1.2 m/s in the tip zone).
