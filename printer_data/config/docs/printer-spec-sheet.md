# Printer Reference

---

## Printer Specs

- **Model:** E3D BigBox Hybrid Pro
- **Current firmware:** Klipper
- **Original firmware:** Marlin 1.1.0-RC6, compiled Jun 10 2016
- **Bed size:** X=300mm, Y=200mm Z=250 mm
- **Nozzle:** E3D V6, 0.6mm

## Heated Bed

- **Type:** 24V Variable-Power-Density (VPD) heated bed PCB — trace density increases near the outer edges to counteract convective heat loss and keep surface temp uniform.
- **Substrate:** FR4 fiberglass PCB, copper heating traces, black solder mask, printed mm grid + "HOME (0,0)" markings.
- **Surface area:** 300mm × 200mm.
- **Voltage:** 24V DC, driven from the main 24V 17A (400W) PSU via the RUMBA's `HB-OUT` MOSFET terminals.
- **Sensor:** ATC Semitec 104GT-2, 100k NTC, on `THB` (PK3).
- **Max Temp:** 120°C - set to 115°C to give a buffer.
- **Mounting:** Suspended above the Z-carriage frame on four M3 15mm female-female standoffs at the corners.
- **Print surface:** 4mm Borosilicate glass glass plate + spring steel clips.

## Control Board

- **Board:** RUMBA (Reprap Universal Mega Board w/ Allegro driver), 135mm × 75mm. 
- **Display:** RepRapDiscount Full Graphic Smart Controller (st7920). Pins: `cs_pin: PD2`, `sclk_pin: PD3`, `sid_pin: PL7`, `encoder_pins: ^PB5, ^PB6`, `click_pin: ^!PL6`
- **Main MCU:** ATmega2560
- **USB-serial bridge chip:** ATmega16U2-AU (separate chip; with its own ISP2 header, unrelated to main MCU's ISP1)
- **Klipper serial path:** /dev/serial/by-id/usb-RRD__www.ru_RUMBA_-_ATmega_2560_co_9533335313735141A251-if00 (resolves to /dev/ttyACM0)
- **Baud rate:** 250000 (Klipper's documented default), firmware reflashed to match. Initially failed to connect at 250000 — root cause was an outdated pyserial (3.4) on the host failing to apply that non-standard baud rate to the 16U2's USB-CDC (ttyACM) port; upgrading to pyserial 3.5 (~/klippy-env/bin/pip install -U pyserial) resolved it.
- **Logic power jumper (`5V_SEL` / "Stand alone" vs "USB Power"):** set to **Standalone** — logic rail is powered from main PSU via onboard 5V DC-DC, not from USB, so cutting main power fully powers down the MCU.
- **Stock steppers drivers:** Allegro A4988
- **New drivers:** BigTreeTech TMC2209, run in UART mode. Reference doc: https://global.bttwiki.com/TMC2209.html

## Motors 
Confirmed via physical labels

| Axis | Model | Rated current | Step angle | Full steps/rev |
|---|---|---|---|---|
| X, Y, Extruder | Wantai `42BYGHMB09L20P4.5-17-X` | 1.7A | 0.9° | 400 |
| Z, Z1 | Wantai `42BYGHW609L20P1-X2` | 1.7A | 1.8° | 200 |

- Y axis has a 36:16 (2.25:1) belt reduction.
- Z originaly wired in parallel

## Pin Reference

# EXP3 Header Wiring Map

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

| Axis | UART pin | EXP3 pin # |
|---|---|---|---|
| X | PC6 | 14 | 
| Y | PC7 | 13 | 
| Z | PJ0 | 12 | 
| Z1 | PJ1 | 11 | 
| E0 | PD1 (SDA) | 10 |

- EXP3 pin 10/9 (SDA/SCL): The I2C pair. PD1/PD0 carries a pull-up (R3, 10kΩ to +5V).
- EXP3 pin 8 (A10/PK2) and pins 2/4/6 are used by the PT100 extruder-temp amplifier board.
- EXP3 pin 7 (A9) still free but blocked by empty dupont connector.
- **Official RUMBA doc confirms EXP3 provides:** "+5V and +12V, 2x ADC, 2x PWM I/O, 4x I/O, I2C" — validates PWM_1/PWM_2 as genuine general-purpose PWM-capable pins.

# TMC2209 Upgrade notes
- TMC2209 module has 3 microstep-select jumpers. Removed all 3 jumpers removed before wiring UART. May only  need the 3rd one removed, but not confirmed either way.
- **X axis direction inverted after the driver swap:** `dir_pin: PH1` (no `!`) on TMC2209 — was `!PH1` on the original A4988s.
- Extra driver current headroom (0.5A→1.36A RMS, ~2.7×) translates to roughly 2×–2.5× more usable acceleration. May not be practical to try though.


# Other Traced Pins

| Resource | Pin(s) | Status |
|---|---|---|
| X-MAX | PC1 | Free |
| Y-MAX | PC3 | Free |
| Z-MAX | PC5 | Free |
| Z-MIN | PC4 | **Occupied** — IR probe signal |
| Part-cooling fan | `[fan]` |
| Hotend fan | PH5 | `[heater_fan hotend_fan]`, thermally linked to extruder, 40°C on threshold |
| Bed heater | PH6 | `[heater_bed]` |
| Extruder heater | PE4 | `[extruder]` |
| Thermistor THB | PK3 | bed thermistor (ATC Semitec 104GT-2) |
| EXP1/EXP2 | — | SD/LCD/Beeper/Push Button Rotary Encoder/RESET |
| ISP1 | — | Shares SD SPI bus, As SD is disabled in klipper those pins could still be used |
| ISP2 | — | Not usable — dedicated to USB-bridge-chip (ATmega16U2) could be used to reflash |
| JTAG block | PF4(TCK)/PF5(TMS)/PF6(TDO)/PF7(TDI) | Free, general GPIO — but needs a firmware-level "release from JTAG" step (`set_digital_out`/menuconfig) before use as plain I/O; not automatic |
| I2C pair | PD1(SDA)=EXP3 pin10, PD0(SCL)=EXP3 pin9 | Free but reserved as a pair; PD1 currently also carries the E0 UART wire |
| Thermistor T0–T3 | PK7/PK6/PK5/PK4 | Free |

## X/Y Motion & Belt

- **Belt:** GT2 timing belt, 2mm pitch. Y-axis: two 690mm cut sections.
- **X pulley:** GT2 20T, 5mm ID.
- **Y drive:** GT2 16T (5mm ID) on the Y motor → GT2 36T (8mm ID) on the rear transmission bar — matches config's `gear_ratio: 36:16`.
- **Y transmission bar outlets:** dual GT2 20T (8mm ID), driving the left/right Y side belts.
- **Idler bearings:** F-604-ZZ flanged, 4mm ID × 12mm OD × 4mm W.

## Extruder & Hotend

- **Hotend:** E3D V6 all-metal, 1.75mm filament.
- **Nozzle:** 0.6mm brass.
- **Drive gear:** E3D Hobb-Goblin, 5mm ID.
- **Heater cartridge:** 24V DC, 30W, 1700mm leads.
- **Temp sensor:** PT100 RTD, 1700mm leads, via external PT100 amplifier board.
- **Hotend fan:** 30×30×10mm, 24V.
- **Part-cooling fan:** 40×40×20mm blower, 24V.

## Z Probe

- **Type:** Mini Differential IR height sensor (dc42/Duet3D design), signal wired to **Z-MIN (PC4)**, used in Klipper as `probe:z_virtual_endstop`.
- **Probe offsets:** `x_offset: -65.0`, `y_offset: 0`
- **Reference doc:** https://miscsolutions.wordpress.com/mini-height-sensor-board/
- **Known issue:** sensor self-configures into digital-output mode (2 LED flashes = correct) only if it detects a pull-up on its OUT line within ~4 seconds of power-up; if Klipper hasn't finished booting and enabling that pin's pull-up in time, sensor defaults to analog mode (4 flashes) and gives bad/inconsistent readings. If the pullup resistor is set in klipper then unplugging and replugging it in will boot it into the correct mode. Klipper can not set the pull up resistor at boot so unless an external 10k resistor is added it will always boot into the wrong mode on power up.
- **Bed surface affects IR reading quality:** readings only became reliably good after placing a piece of dark paper under the glass bed — the sensor's IR response is sensitive to what's on the far side of the glass.

## Z Leadscrew

- **This printer:** 8mm lead (T8×8 — 2mm pitch, 4-start). Confirmed by brass nut hole count (4) and E3D's commissioning manual. `rotation_distance: 8`.
- **Older BigBox variant:** 2mm lead (T8×2, single-start, 8-hole nut). `rotation_distance: 2`. Changing this also changes the old-Marlin-equivalent steps/mm (400 ↔ 1600).
- **ID method:** count the brass nut's thread grooves — 4 holes = 8mm, 8 holes = 2mm.

## Power Supply

- **Model:** Weho S-400-24.
- **Output:** 24V DC @ 17A (400W).
- **Input:** switchable 115V/230V AC.
- **Mounting:** M3 screws, 5mm nylon isolator spacers, lower base plate.

## Legacy Marlin M503 Dump

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
M851 Z-2.3                                 (Z probe offset)
```

## Useful Links

- **Original firmware source:** https://github.com/BigBox3D/Marlin/tree/Hybrid-Pro — the correct branch;
- **RUMBA Reference:** https://reprap.org/wiki/RUMBA
- **Display Reference:** https://reprap.org/wiki/RepRapDiscount_Full_Graphic_Smart_Controller
- **Archive of the Build Manual:** https://web.archive.org/web/20161018063904/http://wiki.e3d-online.com/wiki/BigBox_Build_Manual
