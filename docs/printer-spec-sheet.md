# Printer Spec Sheet — Reference Facts

---

## Machine Identity

- **Model:** E3D BigBox Hybrid Pro
- **Original firmware:** Marlin 1.1.0-RC6, compiled Jun 10 2016
- **Original firmware source:** https://github.com/BigBox3D/Marlin/tree/Hybrid-Pro — the correct branch; supersedes the URL reported by `M115` below (`SOURCE_CODE_URL:https://github.com/BigBox3D/Marlin-Hybrid`, which doesn't resolve to the same place)
- **M115 reported:** `MACHINE_TYPE:BigBox Hybrid P EXTRUDER_COUNT:1`
- **Bed size (from current Klipper config):** X 0–300mm, Y 0–245mm
- **Nozzle:** E3D V6, 0.6mm
- **Now running:** Klipper

## Control Board

- **Board:** RUMBA (Reprap Universal Mega Board w/ Allegro driver), 135mm × 75mm. Reference doc: https://reprap.org/wiki/RUMBA
- **Display:** RepRapDiscount Full Graphic Smart Controller (st7920). Reference doc: https://reprap.org/wiki/RepRapDiscount_Full_Graphic_Smart_Controller. Pins: `cs_pin: PD2`, `sclk_pin: PD3`, `sid_pin: PL7`, `encoder_pins: ^PB5, ^PB6`, `click_pin: ^!PL6`
- **Main MCU:** ATmega2560
- **USB-serial bridge chip:** ATmega16U2-AU (separate chip; its own ISP2 header, unrelated to main MCU's ISP1)
- **Klipper serial path (persistent, by-id — already correctly configured):**
  `/dev/serial/by-id/usb-RRD__www.ru_RUMBA_-_ATmega_2560_co_9533335313735141A251-if00`
- **Logic power jumper (`5V_SEL` / "Stand alone" vs "USB Power"):** set to **Standalone** — logic rail is powered from main PSU via onboard 5V DC-DC, not from USB, so cutting main power fully powers down the MCU.
- **Stock steppers drivers:** genuine **Allegro A4988** (confirmed by chip package label — matches schematic's `A4988BREAKOUT` footprint)
- **New drivers:** BigTreeTech TMC2209, run in UART mode. `sense_resistor: 0.110` (BTT spec). Reference doc: https://global.bttwiki.com/TMC2209.html

## Motors (confirmed via physical nameplate labels)

| Axis | Model | Rated current | Step angle | Full steps/rev |
|---|---|---|---|---|
| X, Y, Extruder | Wantai `42BYGHMB09L20P4.5-17-X` | 1.7A | 0.9° | 400 |
| Z, Z1 | Wantai `42BYGHW609L20P1-X2` | 1.7A | 1.8° | 200 |

- Y axis has a 36:16 (2.25:1) belt reduction.
- All five drivers target `run_current: 1.36` (80% of 1.7A rating) once fully split onto independent UART drivers.
- **Z temporarily wired in parallel** (two motors, one driver) pending IR probe reliability fix + Z split for `z_tilt`. Shared-driver current: `run_current: 1.6` (driver's own 2A rating × 80%, ≈0.8A delivered per motor while paralleled).

## TMC2209 UART Wiring Map (EXP3 header)

EXP3 is a 14-pin (7×2) header.

```
        [ EXP3 ]
 PC6  • 14   13 •  PC7
 PJ0  • 12   11 •  PJ1
 SDA  • 10    9 •  SCL
 A10  •  8    7 •  A9
PWM_2 •  6    5 •  PWM_1
 GND  •  4    3 •  GND
 +5V  •  2    1 •  +12V
```

| Axis | UART pin | EXP3 pin # | Note |
|---|---|---|---|
| X | PC6 | 14 | clean, dedicated I/O |
| Y | PC7 | 13 | clean, dedicated I/O |
| Z | PJ0 | 12 | clean, dedicated I/O |
| Z1 | PJ1 | 11 | clean, dedicated I/O |
| E0 | PD1 (SDA) | 10 | **carries R2 10kΩ pull-up to +5V** (board's I2C pull-up pair) — works fine for UART, just not a "clean" pin |

- EXP3 pin 9 (SCL/PD0) also carries a pull-up (R3, 10kΩ to +5V) — the I2C pair.
- EXP3 pin 8 (A10/PK2) and pins 2/4/6 are **physically occupied** by the PT100 extruder-temp amplifier board — do not use.
- EXP3 pin 7 (A9) still free.
- **Official RUMBA doc confirms EXP3 provides:** "+5V and +12V, 2x ADC, 2x PWM I/O, 4x I/O, I2C" — validates PWM_1/PWM_2 as genuine general-purpose PWM-capable pins (relevant for future BLTouch control line).
- **Gotcha:** each TMC2209 module has 3 microstep-select jumpers. The 3rd one (mimicking A4988's MS3, always-on for 1/16 microstep) is wired on this board to +5V when "on" — but on the TMC2209 that same physical pin is **PDN_UART**, not MS3. Leaving it on grounds/shorts the UART line and causes silent `DUMP_TMC` failures. Fix: all 3 jumpers removed before wiring UART (may only strictly need the 3rd one removed, not confirmed either way — removing all three is known to work).
- **X axis direction inverted after the driver swap:** `dir_pin: PH1` (no `!`) on TMC2209 — was `!PH1` on the original A4988s.

## Z Probe

- **Type:** Mini Differential IR height sensor (dc42/Duet3D design), signal wired to **Z-MIN (PC4)**, used in Klipper as `probe:z_virtual_endstop`.
- **Probe offsets (confirmed live config):** `x_offset: -65.0`, `y_offset: 0`
- **Reference doc:** https://miscsolutions.wordpress.com/mini-height-sensor-board/
- **Old Marlin Z-probe offset:** `M851 Z-2.3` (tuned after the M503 dump was taken — supersedes the `-3.00` shown in that dump)
- **Known issue (root cause confirmed):** sensor self-configures into digital-output mode (2 LED flashes = correct) only if it detects a pull-up on its OUT line within ~4 seconds of power-up; if Klipper hasn't finished booting and enabling that pin's pull-up in time, sensor defaults to analog mode (4 flashes) and gives bad/inconsistent readings until manually unplugged and replugged (which re-triggers its detection window after the board is already fully up).
- **Confirmed via direct test:** cold power-on LED observed flashing 4 times (bad/analog mode).
- **Fix identified, not yet installed:** passive 4.7–10kΩ resistor, OUT to +5V, added externally at the connector (no soldering to sensor PCB required). Sourcing resistor as of last update (RC car board or a friend's parts bin).
- Firmware-level `menuconfig` → "GPIO pins to set at micro-controller startup" was tried as an alternative fix — did not work.
- **Bed surface affects IR reading quality:** readings only became reliably good after placing a piece of dark paper under the glass bed — the sensor's IR response is sensitive to what's on the far side of the semi-transparent glass. Downside: the paper insulates the bed enough to throw bed heating off by roughly 10-15°C, so PID/target temps have to account for it. Currently looking into a PEI-coated spring steel sheet as a bed replacement — opaque (no paper needed) and also a prerequisite for the BTT Eddy probe option below, so it would fix both problems at once.

## Free / Reserved Pin Reference

| Resource | Pin(s) | Status |
|---|---|---|
| X-MAX | PC1 | Free |
| Y-MAX | PC3 | Free |
| Z-MAX | PC5 | Free |
| Z-MIN | PC4 | **Occupied** — IR probe signal |
| JTAG block | PF4(TCK)/PF5(TMS)/PF6(TDO)/PF7(TDI) | Free, general GPIO — but needs a firmware-level "release from JTAG" step (`set_digital_out`/menuconfig) before use as plain I/O; not automatic |
| I2C pair | PD1(SDA)=EXP3 pin10, PD0(SCL)=EXP3 pin9 | Free but reserved as a pair; PD1 currently also carries the E0 UART wire |
| Thermistor T0–T3 | PK7/PK6/PK5/PK4 | Free |
| Thermistor THB | PK3 | **Occupied** — bed thermistor (ATC Semitec 104GT-2) |
| ISP1 | — | Not usable — shares SD/LCD SPI bus + RESET, dedicated to main-MCU emergency reflash only |
| ISP2 | — | Not usable — dedicated to USB-bridge-chip (ATmega16U2) reflash only |
| EXP3 pins 2/4/6/8 | +5V/GND/PWM_2/A10 | **Occupied** — physical footprint of PT100 extruder-temp board |
| EXP3 pin 7 (A9) | PK1 | Free |
| Part-cooling fan | PH4 | **Occupied** — `[fan]` |
| Hotend fan | PH5 | **Occupied** — `[heater_fan hotend_fan]`, thermally linked to extruder, 40°C on threshold |
| Bed heater | PH6 | **Occupied** — `[heater_bed]` |
| Extruder heater | PE4 | **Occupied** — `[extruder]` |

## Legacy Marlin M503 Dump (for cross-checking any future recalibration)

```
Marlin 1.1.0-RC6
Last Updated: 2016-06-01 16:00 | Author: (Greg Holloway, Pro Hybrid)
Compiled: Jun 10 2016

M92 X160.00 Y180.00 Z400.00 E281.00        (steps/mm)
M203 X500.00 Y500.00 Z12.00 E120.00        (max feedrates, mm/s)
M201 X9000 Y9000 Z500 E10000               (max acceleration, mm/s^2 — ceiling, not operating value)
M204 P1500.00 R5000.00 T1500.00            (printing/retract/travel acceleration)
M205 S0.00 T0.00 B20000 X10.00 Z0.20 E2.50 (jerk: XY=10, Z=0.2, E=2.5)
M206 X0.00 Y0.00 Z0.00                     (home offset)
M145 S0 H220 B60 F0 / S1 H240 B120 F0      (material heatup presets)
M301 P46.19 I5.28 D101.02 C100.00 L20      (hotend PID)
M304 P336.00 I61.00 D462.40                (bed PID)
M200 D3.00 / D0                            (filament diameter settings)
M851 Z-3.00                                (Z probe offset)
```

**Cross-check confirmed:** current Klipper `rotation_distance`/`microsteps` values reproduce the stock `M92` steps/mm exactly (X: 160, Z: 400, E: ≈281) — independent validation that current motor calibration is correct.

## Motion Tuning Research Summary

Full report saved as artifact earlier in this project (title: "Large-Format FDM on RUMBA and Klipper: Motion Baseline and TMC2209 Torque-Headroom Upgrade"). Key takeaways:
- RUMBA/ATmega2560 has a hard Klipper step-rate ceiling (~99K steps/s across 3 simultaneous steppers @16MHz) — likely the real limiting factor before driver torque ever becomes one.
- Extra driver current headroom (0.5A→1.36A RMS, ~2.7×) translates to roughly 2×–2.5× more usable acceleration, but much less velocity gain (velocity is inductance/back-EMF limited, not current limited).

## Accuracy Reference Order (established via discussion, largest effect → smallest)

1. Thermal shrinkage/warping during cooling (~0.2–0.3mm) — not fixable via motion/driver tuning.
2. Nozzle line width (0.6mm) — hard floor on smallest resolvable XY feature; does **not** meaningfully limit Z/layer-height resolution.
3. Mechanical backlash (leadscrew nut, belts) — several hundredths to a couple tenths of a mm; not yet directly measured, method documented (push-pull test w/ dial indicator or calipers, motor disabled).
4. Step/microstep resolution — thousandths of a mm at 16 microsteps; already far finer than anything above it, not a meaningful lever.
