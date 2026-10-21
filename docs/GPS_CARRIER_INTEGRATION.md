# GPS carrier integration — October 20, 2026

**U5 is assigned, placed and routed in the current v4 board.** Saadat inspected the linked 2017 Adafruit CAD and reported that it is the same, authorizing use of the existing source-derived carrier geometry. This is user visual acceptance for integration, not manufacturer confirmation or a measured physical-fit result.

## Changes

- Added `Pterodactyl_Modules:Adafruit_GPS_5440_Carrier` and assigned it to U5. The old `UNVERIFIED_Legacy_Carrier` remains a historical comparison asset; the new footprint preserves its pads, outline, holes, courtyard and component keepout.
- Replaced the upper-right GPS envelope with the actual footprint. PPS origin is (163.036, 87.867) mm, rotation 270 degrees. The nine pads run upward at 2.54 mm pitch: PPS, VIN, GND, RX, TX, FIX, VBAT, EN, 3V3_OUT. Electrical drills remain 1.04 mm; carrier mounting holes remain the proposed 2.7 mm NPTH, at (192.754, 67.547) and (192.754, 87.867) mm.
- Connected VIN to SENSOR_3V3, GND to both inner ground planes, TX to GPS_TXD / Teensy pin 7, and RX to GPS_RXD / Teensy pin 8. Five unused pins retain their intentional no-connect nets.
- Added 13 track segments, five serial-signal vias and three nearby GND return vias. Board total: 51 footprints, 246 track segments, 25 vias. Inner layers remain ground planes without signal tracks.
- Preserved every original footprint, all 233 original tracks and 17 original vias, project settings, outline and stackup. Updated the schematic generator's assignment and the library-only footprint generator; neither full design generator nor whole-board autorouter was run.

## Checks

KiCad 10.0.7 reports **0 ERC violations, 0 enabled physical DRC violations, 0 unconnected items, and 0 schematic parity issues**. All 32 functional nets and 35 intentional no-connects match the independent expected netlist. All seven spacing targets pass; the narrowest GPS-to-power courtyard gap is 20.555 mm against the 20 mm target. I2C remains 135.163/128.209 mm and C2 remains 4.493 mm from the carrier ADC pin. Six GND stitching vias connect to both inner planes.

Evidence: [validation/2026-10-20/gps-integration](validation/2026-10-20/gps-integration/). Run `tools/verify_v4_layout.py` with KiCad Python for the current board; it now requires U5, checks its pad/hole/net mapping and requires complete parity/connectivity. Earlier regulator/GPS fixture reports and their script describe an older checkpoint.

The DRC report records five unchanged ignored check categories: missing courtyard, track endpoint not centered on via, tuning profile geometry, footprint filters mismatch and footprint type mismatch. Clean enabled checks are not fabrication approval.

## Still needed before ordering

Verify the actual #5440 module fits the selected header/socket and mounting hardware, including underside coin-cell-holder clearance, installed height, antenna exposure, retention and enclosure. M01's footprint-assignment dependency is resolved by user acceptance; its physical evidence and M02–M04 remain open. No measured dimensions, purchased-module dry fit, manufacturer approval or 3D model were added by this change.

Other gates remain: battery/startup contract, exact BOM and ratings, C1/C4 power-integrity review, manufacturer stackup/rules, independent full-design review and fresh fabrication exports. Firmware is unchanged; GPS data freshness and hardware testing remain open.

The geometry derives from Adafruit Ultimate GPS CAD (board-file commit `c8ae9a95d82f77d3bbd023754dee658959864e5c`, 2017-11-12; recorded repository revision `70430c1`). Designed by Limor Fried/Ladyada for Adafruit Industries, adapted under CC BY-SA 3.0. See the shared footprint-library license.

KiCad may still display the previously opened board: close it without saving the stale view, then reopen the saved v4 PCB.
