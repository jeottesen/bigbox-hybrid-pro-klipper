# Hero Me Gen7.4 (Release 4) Feasibility

Analysis of the Hero Me Gen7.4 printhead (Release 4, July 2023; docs "Read Me First V4.1", "Printer-Component Support V4.1", Change Log V1.6, plus the STL pack) against this printer.
Source files are not stored in this repo (STL pack is ~255 MB extracted); re-download from https://www.printables.com/model/39322.

## Verdict

**Probably yes, with one custom part.** Every component except the X-carriage mount is supported. The BigBox is not on the supported printer list (115+ models), so there is no ready-made *Gantry Adapter* for its X carriage. That adapter is the only piece that must be designed or adapted.

## Part-by-part

| Area | Current | Hero Me fit | Notes |
|---|---|---|---|
| Hotend | E3D V6, 1.75mm, 0.6mm nozzle | **Supported** | Base max hotend width 26.8mm; V6 fits. Use the *E3D V6 / Revo Six / Dragonfly BMO* **Collar Mount V3** + matching **Collar Skirt V2** (`Hotend Mounts/Hotends`, `Hotend Mounts/Skirts`). 1/1.5/2/2.5mm collar spacers are included for height tuning. |
| Heatsink fan | 30x30x10 24V axial | **Mismatch** | Hero Me heatsink fan is 4010 (or 4020) axial. Swap to a 4010 24V — this is already on the upgrade plan (3-wire tach 4010). |
| Part-cooling fan | 4020 blower, 24V | **Supported** | `Part Cooling Ducts/Standard Ducts/4020 fans` (Single 4020L/4020W, Left/Right V3; dual also available). "Long Ducts" and "Tall Ducts" variants exist for different nozzle protrusion. Duct clearance with a 0.6mm nozzle should be checked with `Options/HMG7 Duct Offset Check`. |
| Extruder | Hobb-Goblin gear on Wantai 42BYGHMB09L20P4.5-17-X (0.9°, 1.7A) | **Needs a supported extruder** | Hobb-Goblin is not in the list. Supported direct-drive options: Bondtech BMG (and clones), BMG-M, Orbiter 1.5/2.0, Sherpa Mini/Micro, Titan, LGX, etc. Whether the current extruder is carriage-mounted or Bowden should be confirmed; Hero Me is designed for direct drive but has a Bowden base cap/riser too (`Options/HMG7 Bowden Base Cap`, `6mm Bowden Riser`). Switching extruder changes `rotation_distance`. |
| Z probe | BTT Eddy Duo (was IR, bracket at x_offset -65) | **No dedicated mount** | Closest are the Beacon3D mounts (`ABL Mounts/Beacon3D ABL Sensor`; same flat-coil-PCB style sensor, 17-21mm mounts + spacers). Eddy Duo PCB dimensions differ from Beacon, so expect to adapt/design a bracket. Benefit: the probe would sit much closer to the nozzle than the current -65mm offset, restoring usable bed area. Re-run Eddy calibration after any move. |
| Accelerometer | none (planned ADXL345) | **Supported** | 14 mounts in `ADXL345 Mounts`. |
| Cable mgmt | -- | Optional | 22 towers/tubes in `Cable Management`. |
| X carriage | **unknown, needs measuring** | **Not listed** | See below. |

## The X-carriage question

Hero Me attaches to a printer through a *Gantry Adapter* (`Gantry Adapters/<brand>`) which bolts to the carriage and presents a standard interface to the *Base*. Options, in order of effort:

1. **Universal Base V2** (`Base/HMG7.2 Universal Base V2.stl`, 41.6 x 51.2 x 38.5mm) plus a custom adapter modelled to the BigBox carriage hole pattern. Precedent: `Seckit SK-GO` (also an unusual carriage) uses a custom base + adapter.
2. If the BigBox X axis is smooth rods with LM8UU-type bearings, the **i3 Clone 8mm Linear Rod** adapter or X carriage (`Gantry Adapters/Reprap i3 - Prusa- Clones`; adapter 40 x 28 x 12mm, carriage 22 x 66 x 52mm) may be adaptable or a good starting point. *Not verified that the BigBox matches this.*
3. Replace the carriage with a Hero Me-compatible one (also needs belt clamp design for the BigBox belt layout).

## What is needed to finish this

- Photos of the X carriage from front, back and top, with the hotend/extruder removed if possible.
- Measurements: X rod/rail diameter and spacing, carriage bearing type, mounting hole pattern and thread size, belt attachment style, and available Z clearance below the carriage.
- Confirm whether the extruder is currently on the carriage (direct) or elsewhere (Bowden), and its stepper body length.
- Hotend: actual nozzle-tip to carriage-mount distance, and whether the heater block is stock E3D V6 size.
- Confirm part-cooling blower model (some 4020 blowers differ in outlet width; L vs W duct variants depend on this).

## Klipper-side changes after a swap

- New probe `x_offset`/`y_offset` and `z_offset`; `bed_mesh` and `z_tilt` bounds in `printer.cfg` follow from the new offset. Eddy calibration must be redone.
- Extruder `rotation_distance` and pressure advance if the extruder changes.
- Possibly a new hotend fan config (4010 tach, see upgrade plan).
- Added carriage mass: re-run input shaping, ideally with the ADXL345.

## Addendum: findings from the BigBox STEP files

Source: `STEP.zip` (`Hybrid_v1.1.0.`, `bigbox_dual_v1.0.0`, `transit_brackets_1.1.0`, `bigbox_v1.1.0`, `BB_FRAME_M3_NUT_TRAP`), parsed with CadQuery/OCC. Numbers are read from the CAD geometry, not measured on the machine. Verify with calipers before printing anything.

- **Carriage (Hybrid, solid #1; 79.8 x 70.1 x 27.7mm):** two rod bores of ~15.4mm diameter on **8mm rods, 58.0mm apart**, horizontal, centred at the same height. Bore size suggests LM8UU-type (15mm OD) bearings.
- **Hotend positions:** two groove-mount bores (16.2-16.5mm, i.e. E3D V6 groove mount) at **38mm pitch**, centred exactly between the rods, seat plane ~15mm below the rod axis. The dual head file (`bigbox_dual`) has a longer 109.5mm carriage with the two positions at **35mm** pitch. The Hybrid uses its own carriage and leaves slot 2 empty; it is not the dual carriage.
- **Existing carriage mounting holes:** four 4.4mm holes in a ~26.7 x 38mm rectangle around the hotend seat (Hybrid). Candidate points to bolt a Hero Me adapter plate to; their purpose is unverified.
- **Transit brackets:** three 8mm rods ~497mm long; two line up with the carriage bores (58mm apart), plus end brackets. Confirms 8mm rods; otherwise not relevant to Hero Me.
- **Not in the CAD:** no nozzle or hotend body is modelled, so nozzle-tip height relative to the carriage is unknown. I did not establish which CAD axis maps to firmware X or Y.
- **Hero Me side (measured from the STL mesh):** the Universal Base V2 is 41.6 wide x 51.2 x 38.5mm. Its rear mounting pattern, shared by the gantry adapters, is 4 holes at **32.0 x ~12.4mm** (3.2-3.4mm in adapters, ~4.1-4.4mm in the base). The hotend holes in the base are 22mm apart and the fan holes 30mm apart.

### Implications

- Hero Me's standard interface is just a 32 x 12.4mm four-hole plate, so the custom piece can be a simple adapter. It needs to bolt to the BigBox carriage's underside (or replace the Hybrid carriage's hotend-clamp area) and put the Hero Me base centred between the rods.
- The Universal Base (41.6mm) fits inside the 58mm rod spacing, but only with ~42.5mm clear between bearing surfaces (58 - 15.4). Check clearance for the base, the duct wings and the heatsink fan against the bearing housings.
- The Hero Me stack is taller than the stock hotend. The probe, bed-level distances and the Z travel (250mm bed Z) need rechecking.
- The Hybrid's second hotend slot could carry a fan/duct, Eddy mount or ADXL345 if Hero Me replaces only slot 1.

### Still needed from you

Photos or measurements of the carriage underside and the actual bearing type, the nozzle-tip height below the carriage bottom, and whether the original carriage can be left in place.

## Addendum 2: V6, Eddy and accelerometer STEP files

Same caveat as above: read from CAD, not measured on the printer.

### E3D V6 (`e3d-v6-hotend` snapshot, 30x30x10 fan and stock duct included)
- Nozzle tip to top of heatsink: **61.2mm**. Heatsink 22.3mm diameter; the 16mm top flange (3.7mm) / 12mm groove (6mm) / 16mm lower flange match a standard groove-mount V6. Heater block 20 x 16 x 11.5mm.
- **Nozzle position in the Hybrid carriage (estimate):** if the V6 top sits at the bore step (CAD Z 697.6), the **nozzle tip is ~45.5mm below the carriage underside and ~60.4mm below the rod axis**. This is inferred from the carriage bore, not modelled; the stock duct bottoms in the dual-head file sit ~1.3mm below that point, which supports it. Confirm with a ruler.
- The V6 sits mostly inside the carriage between the rods (top of hotend roughly level with the rod axis).

### BTT Eddy (`Eddy_Bigtreetech.stp`)
- Envelope **18.9 x 17.0 x 33.8mm**, two solids (apparently two models of the same part, offset ~1.5mm). Two **3.3mm holes, 10.5mm apart**, 22.9mm from one end.
- The model is a chunky block, and I could not tell which face holds the coil. Confirm orientation and sensing face before designing the mount.
- Hero Me has no Eddy mount. Beacon3D mounts are the nearest, but this hole spacing (10.5mm) would need checking against them.

### BigTreeTech S2DW accelerometer
- Board **16.2 x 35.2mm**, 4.7mm tall including the USB-C connector at one end.
- Mounting: two **3.0mm holes 15.4mm apart** (at x=13.0, y=2.5 and y=17.9) plus a 6mm hole at (7.8, 20.3).
- Hero Me ADXL345 mounts (`ADXL345 Mounts`, 14 variants) are built for boards with **14.0mm** hole spacing (3.4mm holes). The S2DW's 15.4mm spacing does not match any of them. Options: slot the mount holes by ~1.4mm, or print a small adapter plate. The "35mm" mounts match the board length but not the hole spacing.
- Eddy Duo + S2DW both being USB devices on the Pi does not affect mounting, but cable routing and the Hybrid's free slot 2 are worth planning together.

## Addendum 3: Photos of the current head

- **Part fan:** label reads *Xinyujie XYJ24B4020H, DC24V 0.10A, ball bearing*, a standard **4020 radial blower**. Hero Me supports 4020 blowers (`Standard Ducts/4020 fans`, Single/Dual, Left/Right). The release has "4020L" and "4020W" duct variants; their meaning is not documented in the files, so measure the blower's outlet (and print one variant as a test) before committing.
- **Extruder:** the black printed extruder with spring-loaded idler sits directly on top of the carriage, so this is a **carriage-mounted direct drive** (the Bowden question is settled). The motor is above the frame of the photos. Hero Me's extruder mounts replace this piece; the Hobb-Goblin is still not on its supported list.
- **Hotend:** V6 hangs below the carriage with silicone sock, heatsink fins fully exposed, 30mm fan taped on the side. The stock duct outlet ends roughly level with the heater block bottom, consistent with the CAD-based nozzle estimate.
- **Duct condition:** the printed stock duct around the heater block looks partly melted/deformed. Worth replacing regardless.
- Both rods are 8mm bright steel; the carriage rides between them as in the CAD.

## Addendum 4: Community Eddy mount, ADXL comparison, height analysis

### Eddy mount (Printables/Thingiverse "Hero Me 7.4 BTT Eddy Mount, version TZ-V6-2.0", Juri, May 2024)
- Two parts: a **mount** (56 x 12.6 x 9.5mm, three M3 holes 6mm apart for attaching to the Hero Me body) and a **slide plate** (18.1 x 33.7 x 3.5mm) that holds the Eddy and adjusts in height. Plate holes for the Eddy are 10.5mm apart, which matches the Eddy STEP. STEP files are public so the mount can be adapted.
- Built for the **TZ-V6-2.0** hotend (a V6-form-factor clone); the E3D V6 is the same groove-mount form but the mount needs checking against the actual body and duct clearance.
- Author's assembly order: mount to the Hero Me body, set plate to ~2mm above the print plate, then fit the Eddy. M3x8 plate screw, M3x16 for the Eddy; hex screw heads must be <= 1.5mm tall (or thicken the plate).
- Coil end of the Eddy (confirmed by owner): the wider end, **farther from the mounting holes** (Z=0 end in the STEP, 22.9mm from the holes).
- License: CC BY-NC 4.0 (personal use fine, attribute the author).
- Expect the probe offset to drop well below the current -65mm, but the true value needs the assembled geometry.

### ADXL mounts vs S2DW
All 14 Hero Me ADXL345 mounts have **14.0mm** board-hole spacing (measured from the STLs). The S2DW STEP shows 15.4mm. No BTT ADXL345 2.0 model was available to compare, so the "same profile" claim is unverified. Measure the physical board's hole spacing; if it is 15.4mm, slot the mount holes or print an adapter.

### Height analysis (estimates; collar-mount orientation is inferred)
| | Stock BigBox Hybrid | Hero Me (Universal Base + V6 collar mount) |
|---|---|---|
| Nozzle tip vs reference | 60.4mm below rod axis; 45.5mm below carriage underside | ~63mm below base underside; ~76mm below the centre of the 32 x 12.5mm rear bolt pattern |
| Hotend position | centred between rods | **~42mm in front of the bolt plane** |

- The bolt-pattern centre sits ~13mm above the base underside. If it is placed level with the top of the Hybrid carriage (CAD Z 709.5), the nozzle ends up **~3mm lower** than stock: negligible. Placed at rod-axis height, it would be ~16mm lower.
- **The bigger issue is not height but lateral offset.** Stock puts the hotend between the rods; Hero Me's interface is a vertical plate with the hotend 42mm out in front. Bolted to a carriage face (carriage is ~79mm deep), the hotend would sit ~80mm off the carriage centre, far from the rods (leverage, shifted usable area). A custom bracket that keeps the base near the rod plane is needed, or a replacement carriage designed around the Hero Me interface.
- Confirm after any redesign: duct and Eddy plate clearance, bed clips, and Z home.

## Addendum 5: BIGTREETECH S2DW V1.0 manual

- Board is **33.25 x 15.5mm** per the manual (the STEP envelope of 35.2 x 16.2mm includes the USB-C overhang). Sensor is a **LIS2DW** on an **RP2040**, USB, 5V.
- Manual's mounting drawing confirms the STEP: holes **2.5mm and 18.0mm from the end** (**15.5mm apart**), plus the larger 6mm hole at 20.5mm. So the 15.5mm spacing is real and still does not match Hero Me's 14.0mm ADXL345 mounts.
- Two mounting methods shown (Voron StealthBurner example):
  1. On a side bracket with dual holes at the official spacing.
  2. Screws through the PCB and a rubber ring directly on the **heater block**. This needs no Hero Me ADXL mount, but the board is rated -40 to +85C and a V6 block runs 200C+, so only use it for short tuning runs, with the rubber spacer, and remove afterwards.
- Klipper: `[lis2dw]` section (added Aug 2023, update Klipper if "not a valid section"), RP2040 firmware (no bootloader offset, W25Q080 CLKDIV 2, USB), sample config `sample-bigtreetech-lis2dw-v1.0.cfg` at github.com/bigtreetech/LIS2DW. Set `axes_map` from the board's silkscreen axes vs printer motion.
