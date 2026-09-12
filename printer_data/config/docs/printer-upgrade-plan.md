# Printer Upgrade Plan — E3D BigBox Hybrid Pro (RUMBA/Klipper)

Living reference doc for this build. Update as things get done or priorities shift.

## In Progress

- **TMC2209 UART bring-up**: X, Y, Z, and Extruder are live and uncommented in the actual config (all confirmed working). Only **Z1** remains commented out, intentionally — held back pending the physical Z-motor split (see below). When ready: run `STEPPER_BUZZ STEPPER=stepper_z1` before fully enabling, per the reminder already in the config.
- **IR Z-probe reliability fix**: root cause confirmed — sensor needs to see a pull-up on its OUT line within ~4s of power-up to start in digital mode (2 LED flashes); board power-on is too slow for Klipper to have configured that pull-up in time, so it defaults to analog mode (4 flashes) and gives bad readings until unplugged/replugged. Fix identified: passive 4.7–10kΩ resistor from OUT to +5V, added externally at the connector (no soldering to the sensor board itself). **Resistor not yet in hand** — checking an old RC car board or asking a friend with electronics parts.

## Recently Decided / Settled

- **Z motors staying wired together (parallel) for now.** Splitting onto independent TMC2209 drivers (for `z_tilt` auto-leveling) is deferred until the IR probe is proven reliable via `PROBE_ACCURACY` — no point adding z_tilt's dependency on the probe while the probe itself is still shaky. Current shared-driver current: `run_current: 1.6` (≈0.8A per motor). Once split: `1.36` per driver, matching X/Y/E0.
- **All motors confirmed via physical label**: Wantai 1.7A rated, X/Y/Extruder = 42BYGHMB09, Z/Z1 = 42BYGHW609. `run_current: 1.36` (80% of rated) across all five drivers once on UART.
- **stealthchop_threshold: omitted (SpreadCycle everywhere)** — chose accuracy over quiet noise for now; revisit only if the fan-noise work doesn't get things quiet enough on its own.
- **interpolate: left at default (true)** — not worth disabling given real-world accuracy is dominated by thermal/backlash effects, not the ~0.006mm interpolation error.
- **Leadscrew lead staying at 8mm** (not switching to 4mm) — not worth it.
- **MCU (ATmega2560) upgrade deliberately deferred** — waiting to actually hit real limits (skipped steps unexplained by torque, or "Rescheduled timer in the past" shutdowns) before switching to 32-bit, same philosophy as not rushing off stock Marlin before feeling its limits.
- **Motion settings baseline set from real stock M503 dump** (not guesswork): stock ran `M204 P1500/T1500` accel, `M205 X10` jerk. New conservative-but-improved Klipper targets: `max_velocity: 150`, `max_accel: 2000`, `square_corner_velocity: 8`, `max_z_velocity: 10`, `max_z_accel: 100`. Not chasing max speed — can push further later via Ellis' TEST_SPEED method once comfortable.
- **Two-stage X/Y homing added** (`second_homing_speed: 10`, `homing_retract_dist: 5`) for more repeatable home position.
- **Benchy hull text is NOT a realistic goal on the 0.6mm nozzle** — official Benchy settings target a 0.4mm nozzle; not worth tuning toward. Layer height itself (0.25/0.2, sometimes 0.3, variable height) is fine on 0.6mm per real-world reports — it's XY fine detail specifically that the nozzle caps, not Z resolution.
- **0.6mm nozzle being kept** (previous owner's choice) — good trade of detail for speed for the kind of printing actually being done.

## Open / Needs Attention

- **Bed surface: investigating a PEI-coated spring steel sheet** to replace the glass bed. Two separate problems point at the same fix: (1) the glass bed's transparency was giving bad IR probe readings until a piece of dark paper was added underneath it — which works, but insulates the bed enough to throw bed heating off by roughly 10-15°C; (2) the BTT Eddy probe option below already requires a spring steel bed. A PEI spring steel sheet would fix both at once and let the paper come back out.
- **Gantry squareness**: ~2mm front-to-back discrepancy after a manual adjustment attempt (frame/belt access made further physical correction difficult). Two paths considered: better measurement via matched diagonals, or just use Klipper's `[skew_correction]` module with a calibration print instead of continuing to fight physical access. Not urgent — low-to-moderate severity (parallelogram-shaped prints), not a structural/binding issue.
- **Pressure advance**: not yet tuned. Suspected fix for the pitting seen on Benchy hull at 0.2mm layers (flow-consistency issue that's more visible at thin layers, not true warping). Do this before revisiting the print-in-place fidget toy.
- **Print-in-place fidget toy**: paused until pressure advance is tuned and Z leveling/probe are trustworthy — both first-layer consistency and PA-controlled ooze at direction changes are likely why it struggled under Marlin.

## Future Upgrades (not yet started)

- **Hotend fan RPM monitoring**: basic PWM/thermal-linked control is already implemented (`[heater_fan hotend_fan]` on PH5, tied to extruder temp) — what's still pending is upgrading to a 3-wire tach fan (same 4010 size as stock E3D V6 fan) specifically for failure detection via Ellis' `fan_tach_monitor.cfg`. Wiring plan: existing power wiring stays on PH5 as-is; tach wire goes to a spare digital input (X-MAX/Y-MAX/Z-MAX headers are candidates). Noctua NF-A4x10 (12V, 4-wire) is compatible with this plan — 4th PWM wire just left unconnected since board-side switching is used instead of fan-side PWM input.
  - **Needs more research: good quiet hotend fan options** beyond the Noctua NF-A4x10 default pick — revisit before ordering.
  - Also flagged for later: general case/part-cooling fan noise reduction (may end up mattering more than driver StealthChop for perceived noise).
- **BLTouch**: would need Z-MAX (PC5, free) for signal + PWM_1 or PWM_2 on EXP3 (confirmed genuine general-purpose PWM I/O per RUMBA's own docs) for control line. Z-MIN is unavailable (already used by IR probe).
- **BTT Eddy probe**: contingent on switching the bed to spring steel (see the PEI sheet note above). Wiring/requirements not yet researched — don't assume a pin reservation until actually scoped, since some Eddy variants use USB/CAN rather than simple GPIO.
- **Filament runout sensor**: simple switch, straightforward — any free 3-pin endstop-style header (X-MAX or Y-MAX) works with zero extra setup.

## Reserved / Spare Capacity Reference

- **JTAG block (PF4/PF5/PF6/PF7)**: 4 general-purpose GPIO/analog pins, currently idle (no debugging use planned). Requires a firmware-level "release from JTAG" step before use as plain I/O — confirmed via `set_digital_out`/menuconfig research that this isn't automatic. Best reserve for simple switches/sensors given no I2C devices currently planned.
- **I2C pins (EXP3 pin 10/SDA=PD1, pin 9/SCL=PD0)**: reserved for a possible future I2C device — most likely candidate is an ADXL345 accelerometer for Klipper input-shaper tuning, if that becomes a priority. Note: these two pins already carry board pull-up resistors (R2/R3) to +5V — fine for I2C or for the UART wire currently landed on pin 10 (E0), just worth remembering if debugging that line specifically.
- **Spare thermistor channels (T0–T3, i.e. PK7/PK6/PK5/PK4)**: THB (bed) is in use; T0–T3 are free — candidate for a chamber thermistor if the printer ever gets enclosed.
- **ISP1 / ISP2**: not usable for anything — dedicated to emergency firmware reflashing only (ISP1 = main 2560, ISP2 = USB bridge chip), pins already claimed by SD/LCD SPI bus and RESET.
- **EXP3 pins 2/4/6/8** (physically occupied by the PT100 extruder temp board) and **Z-MIN** (IR probe signal) — not available for anything else.
