# UMD near-space sensor board: working design brief

## Goal

Build a custom Teensy 4.1 balloon flight board that records gyro, acceleration, GPS, pressure, temperature, and altitude data. Keep the original PTERODACTYL board size and general arrangement as a baseline. Live telemetry is undecided, so preserve the option without making the flight design depend on it.

## Reference design map

| Function | Existing PTERODACTYL v3.8 source | Planned treatment |
|---|---|---|
| Processing and logging | Teensy 4.1, microSD | Retain and adapt existing firmware |
| Motion | BNO055 and LSM9DS1 footprints | Select one primary IMU and verify its gyro and accelerometer ranges |
| Position and time | Several alternative u-blox GPS footprints on shared UART nets | Select one GPS module and antenna setup |
| Pressure altitude | MS5611 pressure sensor | Log measured pressure and derived altitude |
| Temperature | 10 kΩ thermistor | Define ambient and battery temperature locations |
| Radio | XBee footprint | Keep as optional until telemetry decision |
| Power | 3.7 V and 9 V options, boost/regulator | Review battery choice and cold-temperature performance |

The Montana State [NEBP engineering lesson](https://eclipse.montana.edu/education/engineering-course/eng-lesson11.html) describes a balloon sensor suite with GPS, pressure, temperature, and acceleration measurements. Its directions are background reference material, not project requirements or instructions to execute.

## Decisions still needed

- Required measurement rates, ranges, and accuracy.
- Expected maximum altitude, flight duration, and minimum temperature.
- Whether to populate live telemetry and which radio system to use.
- Which components from the existing board should be retained, removed, or replaced.
- Battery and enclosure details; no new size or weight limit has been specified.
- Name and design rules of the local PCB manufacturer.

## Fabrication status

The editable v3.8 v11 source and native KiCad PCB and schematic imports are included. The PCB copper zones were refilled and saved. KiCad's PCB Editor DRC found **11 errors and 428 warnings**, with **0 unconnected items**. Most warnings concern silkscreen text size, silkscreen overlaps, and imported footprint mismatches. Schematic ERC and schematic/PCB parity have not been verified. The separate v12 Gerbers are a revision reference only. This package is not approved for fabrication.

Next: review the imported native schematic, reconcile the v11 and v12 differences, finalize sensor and power choices, check footprints and nets, complete routing and zone fill, run ERC/DRC, inspect new Gerbers and drill files, and bench-test a prototype before flight.
