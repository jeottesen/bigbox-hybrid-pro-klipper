# BigBox Hybrid Pro — Klipper

This repo is the living backup for an E3D BigBox Hybrid Pro. It originally ran Marlin 1.1.0-RC6, and now runs Klipper on a RUMBA board.

See [docs/](docs) for the hardware spec sheet and the ongoing upgrade plan.

## Machine at a glance

| | |
|---|---|
| Model | E3D BigBox Hybrid Pro |
| Board | RUMBA (ATmega2560) |
| Firmware | Klipper (was Marlin 1.1.0-RC6) |
| Nozzle | E3D V6, 0.6mm |

## Firmware

`e3d-big-box.config` is the `make menuconfig` config used to build the AVR
firmware. "Enable extra low-level configuration options" has to be turned on
to set the baud rate manually (230400, matching `printer.cfg`'s `[mcu]`).
`INITIAL_PINS` is set to the hotend fan pin (`PH5`) as a safety measure, so
the fan is forced on at MCU startup even before Klipper connects.

## Status

Actively maintained alongside the physical printer. Treat anything here as a personal reference rather than a guide, and always cross-check against your own hardware before copying config values directly.

## License

[MIT](LICENSE)

## Credits

- [Klipper](https://www.klipper3d.org/) / [Moonraker](https://moonraker.readthedocs.io/) / [Mainsail](https://docs.mainsail.xyz/) / [Fluidd](https://docs.fluidd.xyz/)
- [Klipper-Backup](https://klipperbackup.xyz/) for automated backups
