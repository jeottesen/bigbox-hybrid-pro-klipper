# E3D BigBox Hybrid Pro Upgrade Plan 

Reference doc for this build. Update as things get done or priorities shift.

## In Progress

- **PEI plate:** covered the glass bed with a magnet and sat the pei plate on top. IR issues returned due to steels scattering providing bad readings.
- **BTT Eddy Duo:** Plugged into the raspberry pi and attached to the old ir probes mount on the print head. the ir probe has been moved to act the z endstop on the right side of the bed with a new adapter. Currently calibrating and testing.
- **Filament runout sensor**: simple switch, straightforward — any free 3-pin endstop-style header (X-MAX or Y-MAX) works with zero extra setup. Just need to reterminate the ends and wire it in.
- **Cleanup Wiring:** Wiring things to be hidden with the new sensors added and the ir probe moved. 

## Complete

- **Z motors wired together (parallel) for now.** Split to be controlled independently with new TMC2209 drivers. z_tilt setup and working. Decided to run the z motors at .8 and with stealth chop to prevent hum. Stealthchops accuracy issues aren't an issue for the z drivers with the leadscrew.
- **TMC2209 UART bring-up**: X, Y, Z, and Extruder are live and confirmed working.
- **IR Z-probe boot mode fix**: root cause confirmed — sensor needs to see a pull-up on its OUT line within ~4s of power-up to start in digital mode (2 LED flashes); board power-on is too slow for Klipper to have configured that pull-up in time, so it defaults to analog mode (4 flashes) and gives bad readings until unplugged/replugged. Installed a 10kΩ resistor from OUT to +5V, at the connector and removed the pull up resistor in klipper.

## Potential Upgrades

- **Hotend fan RPM monitoring**: basic PWM/thermal-linked control is already implemented (`[heater_fan hotend_fan]` on PH5, tied to extruder temp) — what's still pending is upgrading to a 3-wire tach fan (same 4010 size as stock E3D V6 fan) specifically for failure detection via Ellis' `fan_tach_monitor.cfg`. Wiring plan: existing power wiring stays on PH5 as-is; tach wire goes to a spare digital input (X-MAX/Y-MAX/Z-MAX headers are candidates).
- **Quieter fans**: general case/part-cooling fan noise reduction.
- **BLTouch**: would need Z-MAX (PC5, free) for signal + PWM_1 or PWM_2 on EXP3 (confirmed genuine general-purpose PWM I/O per RUMBA's own docs) for control line. Z-MIN is unavailable (already used by IR probe).
- **BTT Eddy probe**: contingent on switching the bed to spring steel (see the PEI sheet note above). Wiring/requirements not yet researched — don't assume a pin reservation until actually scoped, since some Eddy variants use USB/CAN rather than simple GPIO.
- **Input Shaping Accelerometer**: Add an ADXL345 accelerometer for input-shaper tuning, have not seen a need yet but might be interesting for debugging.

## Spare Pin Reference
- **JTAG block (PF4/PF5/PF6/PF7)**: 4 general-purpose GPIO/analog pins, currently idle (no debugging use planned). Requires a firmware-level "release from JTAG" step before use as plain I/O — confirmed via `set_digital_out`/menuconfig research that this isn't automatic. Best reserve for simple switches/sensors given no I2C devices currently planned.
- **I2C pins (EXP3 pin 10/SDA=PD1, pin 9/SCL=PD0)**: These two pins already carry board pull-up resistors (R2/R3) to +5V — fine for I2C or for the UART wire currently landed on pin 10 (E0).
- **Spare thermistor channels (T0–T3, i.e. PK7/PK6/PK5/PK4)**: THB (bed) is in use; T0–T3 are free.
- **ISP1 / ISP2**: ISP1 = main 2560, ISP2 = USB bridge chip), Could use ISP2 for accelerometer.
- **EXP3 pins 2/4/6/8**: physically occupied by the PT100 extruder temp board.
