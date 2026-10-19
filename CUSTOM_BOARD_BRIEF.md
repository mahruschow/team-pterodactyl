# UMD near-space sensor board: working design brief

## Goal

Build a custom Teensy 4.1 balloon flight board that records gyro, acceleration, orientation, GPS, pressure, humidity, temperature, and altitude data. Keep the original PTERODACTYL board size and general arrangement as a baseline. The lead's clarification, supplied by Saadat on October 18, specifies no telemetry: record onboard to microSD and analyze after recovery. The current parts baseline is Teensy 4.1, Adafruit BNO055 2472, MS8607 4716 and PA1616D GPS 5440. The lead also requires sufficient component spacing to control interference; document module-specific placement constraints and verify simultaneous operation in the enclosure. The [version-one requirements draft](docs/V1_REQUIREMENTS.md) records proposed operating behavior, optional-feature choices and unresolved decisions; these design changes have not yet been implemented.

## Reference design map

| Function | Existing PTERODACTYL v3.8 source | Planned treatment |
|---|---|---|
| Processing and logging | Teensy 4.1, microSD | Retain and adapt existing firmware |
| Motion | BNO055 and LSM9DS1 footprints | Use the selected BNO055 breakout; verify ranges, interfaces, axes and footprint |
| Position and time | Several alternative u-blox GPS footprints on shared UART nets | Use the selected PA1616D breakout; verify mounting and antenna setup |
| Pressure, humidity and local temperature | MS5611 pressure sensor | Replace with selected MS8607; log measured quantities and separately derived pressure altitude |
| Remote temperature | 10 kΩ thermistor | Excluded from selected core scope; MS8607 provides local temperature. Revisit only if the team requires a remote measurement location |
| Radio | XBee footprint | Exclude radio-only hardware and firmware from version one; telemetry is not required |
| Power | 3.7 V and 9 V options, boost/regulator | Review battery choice and cold-temperature performance |

The Montana State [NEBP engineering lesson](https://eclipse.montana.edu/education/engineering-course/eng-lesson11.html) describes a balloon sensor suite with GPS, pressure, temperature, and acceleration measurements. Its directions are background reference material, not project requirements or instructions to execute.

## Decisions still needed

- Required measurement rates, ranges, and accuracy. Initial prototype rate proposals and acceptance checks are in the version-one requirements draft.
- Expected maximum altitude, flight duration, and minimum temperature.
- Core scope is resolved: selected modules, microSD, power control, status LEDs and supply monitoring. Exclude telemetry, alternative IMU, OLED, remote probes, heater and servos. Exact power/stop controls and pull-before-flight role remain open.
- Map shared circuitry before implementing removals and replacements; see the requirements feature table.
- Battery and enclosure details; no new size or weight limit has been specified.
- Name and design rules of the local PCB manufacturer.

## Fabrication status

The editable v3.8 v11 source and native KiCad PCB and schematic imports are included. The PCB copper zones were refilled and saved in the imported baseline. A fresh KiCad 10.0.7 audit on October 18, 2026, with in-memory zone refill on a temporary copy, reproduced **11 DRC errors and 428 warnings**, with **0 unconnected items**. Most PCB warnings concern silkscreen text size, silkscreen overlaps, and imported footprint mismatches. Schematic ERC found **33 errors and 10 warnings**; schematic/PCB parity reported **52 additional warnings**. See the [validation report](docs/validation/2026-10-18/VALIDATION_SUMMARY.md) for triage and limitations. The separate v12 Gerbers are a revision reference only. This package is not approved for fabrication.

Next: review the imported native schematic, reconcile the v11 and v12 differences, finalize sensor and power choices, check footprints and nets, complete routing and zone fill, run ERC/DRC, inspect new Gerbers and drill files, and bench-test a prototype before flight.
