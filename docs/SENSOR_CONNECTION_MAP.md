# Step 3 — module connections, power and mechanical review

Reviewed October 18, 2026. Connection research plus two draft carrier footprints; no main schematic/PCB changes and no hardware tested. See [FOOTPRINT_REVIEW.md](FOOTPRINT_REVIEW.md) for created assets, pad numbering, native checks and remaining mechanical gates.

Saadat confirmed the boards have **not been purchased** and instructed us to use the spreadsheet's exact product numbers: Teensy 4.1, Adafruit BNO055 **2472**, MS8607 **4716**, and PA1616D GPS **5440**. In particular, do not substitute the BNO055 STEMMA QT variant. This resolves the intended BNO055 footprint family. Delivered revisions still need inspection before assembly.

## Result and remaining gates

- Teensy `Wire` uses SDA **18**, SCL **19**; `Serial2` uses RX **7**, TX **8**. These functions agree with the legacy netlist and can be retained in the working map. [PJRC I2C](https://www.pjrc.com/teensy/td_libs_Wire.html), [PJRC UART](https://www.pjrc.com/teensy/td_uart.html).
- BNO055 uses **0x28** with its default address pull-down; MS8607 uses **0x76** for pressure/temperature and **0x40** for humidity. There is no address collision among these selected devices. [BNO055 driver definitions](https://raw.githubusercontent.com/adafruit/Adafruit_BNO055/master/Adafruit_BNO055.h), [MS8607 definitions](https://adafruit.github.io/Adafruit_MS8607/html/_adafruit___m_s8607_8h.html).
- **Replace the imported BNO055 footprint.** Its four signal/power positions match the QT variant, not product 2472, and its `3V3` pad occupies the QT board's regulator-output position. The proposed map powers the breakout through VIN instead.
- GPS logical wiring is established, but exact #5440 mechanical approval remains open: the published Ultimate GPS CAD inspected here names `FGPMMOPA6H`, not PA1616D. Do not turn that legacy CAD into an approved #5440 footprint without matching the revision.
- Battery/input regulation, USB power isolation, peak-current sizing, supply divider, control/LED GPIOs, module mounting height and final enclosure fit remain open. These do not invalidate the logical sensor map.

## Proposed carrier connections

`SENSOR_3V3` below means a regulated 3.3 V supply whose source will be chosen in Step 5. It is not permission to connect multiple regulator outputs together. `GND` is the intended common logic return; reconcile imported ground labels during the schematic edit.

| Carrier function | Teensy endpoint | Module endpoints | Direction / electrical intent |
| --- | --- | --- | --- |
| Sensor data | 18 / SDA / Wire | BNO055 SDA; MS8607 SDA | Bidirectional open-drain; pull-ups at 3.3 V |
| Sensor clock | 19 / SCL / Wire | BNO055 SCL; MS8607 SCL | Teensy controller clock; allow device clock stretching |
| GPS data into logger | 7 / RX2 | GPS TX | GPS output to Teensy input; 3 V logic |
| GPS configuration | 8 / TX2 | GPS RX | Teensy output to GPS input; 3.3 V logic |
| Sensor supply | Source TBD | VIN of BNO055, MS8607 and GPS | Proposed 3.3 V input to each breakout; leave their regulator outputs separate |
| Controller supply | VIN | Reviewed regulated controller rail | Target 5 V architecture; input regulator not selected |
| Return | Teensy GND pins | All module GND pins | Common electrical reference; review return paths in Step 4 |
| Storage | Built-in microSD | No additional carrier SPI wiring | Reserve Teensy's onboard SD connections; do not repurpose them |
| Supply monitoring | 26 / A12 candidate | Divider/filter/protection TBD | ADC input; maximum source voltage must be known first |
| LEDs / optional clean-stop control | Unallocated | Components TBD | Reserve during schematic work; core feature selection does not fix pin numbers |

The supply and ADC proposals are design choices; the UART/I2C pin functions are documented capabilities. No GPIO may receive more than 3.3 V. Teensy VIN and USB VUSB are connected by default: simultaneous USB and external VIN require a reviewed isolation arrangement. PJRC recommends no more than 250 mA of external load from Teensy's 3.3 V output and does not describe its 3.3 V pin as the normal board-power input. [Teensy power and pin specifications](https://www.pjrc.com/store/teensy41.html).

## BNO055 #2472: each exposed pin

Use the non-QT CAD, identified as Rev C in the [manufacturer downloads](https://learn.adafruit.com/adafruit-bno055-absolute-orientation-sensor/downloads). Header numbering here is the manufacturer's Eagle connector numbering, not a newly assigned KiCad pad number. CAD coordinates are in millimetres, component-side view, X right and Y up from the outline's lower-left extent. Do not mirror them when designing a top-mounted carrier socket; convert the coordinate convention deliberately.

| Header / pin | Label | CAD X, Y | Proposed connection / treatment |
| --- | --- | --- | --- |
| JP1 / 1 | VIN | 6.985, 1.270 | SENSOR_3V3; power input |
| JP1 / 2 | 3Vo | 9.525, 1.270 | Regulator output; no carrier connection |
| JP1 / 3 | GND | 12.065, 1.270 | GND |
| JP1 / 4 | SDA | 14.605, 1.270 | Teensy 18; bidirectional |
| JP1 / 5 | SCL | 17.145, 1.270 | Teensy 19; clock |
| JP1 / 6 | RST | 19.685, 1.270 | Leave external connection unused initially; module reset pull-up present. Consider a recovery GPIO before schematic freeze |
| JP2 / 1 | PS0 | 9.525, 19.050 | Unused externally; onboard pull-down selects normal I2C mode with PS1 |
| JP2 / 2 | PS1 | 12.065, 19.050 | Unused externally; onboard pull-down |
| JP2 / 3 | INT | 14.605, 19.050 | Sensor output; unused for proposed polling |
| JP2 / 4 | ADR | 17.145, 19.050 | Unused externally; onboard pull-down retains 0x28 |

VIN supports 3.3–5 V, but use 3.3 V here to keep the host-side pull-ups compatible with Teensy. The older CAD calls this input net `5.0V` and the external signals `SDA_5V`/`SCL_5V`; those are CAD names, not a requirement to apply 5 V. R8/R9 pull the external bus to VIN, while R6/R7 pull the sensor side to the local regulator output. These are separate sides of the level shifters. [Pin descriptions](https://learn.adafruit.com/adafruit-bno055-absolute-orientation-sensor/pinouts), [pinned non-QT CAD](https://github.com/adafruit/Adafruit-BNO055-Breakout-PCB/tree/64c5a387aa807edb01eff440d1cd07ce4b608642).

Adafruit documents I2C protocol quirks for BNO055 on some controller families. This is a requirement to bench-test the actual Teensy 4.1 combination, including timeouts and recovery; it is not evidence that Teensy 4.1 is incompatible. Begin with a proposed 100 kHz bus and test before increasing speed.

## MS8607 #4716: each exposed pin

The pinned CAD uses `JP2`. Its offsets are preserved exactly rather than rounded to an assumed centered header. The `VCC` net is the breakout VIN input; `3.3V` is the regulator output.

| Header / pin | Label | CAD X, Y mm | Proposed connection / treatment |
| --- | --- | --- | --- |
| JP2 / 1 | VIN | 7.5565, 2.6035 | SENSOR_3V3; power input |
| JP2 / 2 | 3Vo | 10.0965, 2.6035 | Regulator output; no carrier connection |
| JP2 / 3 | GND | 12.6365, 2.6035 | GND |
| JP2 / 4 | SCL | 15.1765, 2.6035 | Teensy 19 |
| JP2 / 5 | SDA | 17.7165, 2.6035 | Teensy 18 |

The two STEMMA QT connectors duplicate GND/VIN/SDA/SCL (CAD pins 1/2/3/4 respectively). Leave them unused in the header-carrier proposal; reserve their physical envelope. Do not accidentally introduce a second supply through a cable.

Adafruit specifies VIN at 3–5 V and level-shifted I2C. R3 is a four-resistor 10 kΩ pack, including host and sensor-side pull-ups. Powering VIN at 3.3 V keeps the external pull-ups at that level. [Pin guide](https://learn.adafruit.com/adafruit-te-ms8607-pht-sensor/pinouts), [pinned CAD](https://github.com/adafruit/Adafruit-MS8607-PCB/tree/56dfd5af979fb63cff98ebcfe2170644b4439430).

## PA1616D GPS #5440: each exposed function

The #5440 product specifies NMEA at 9600 baud by default, 3 V logic output and a 5 V-safe input. Use `Serial2`, initially 9600 8N1 with a proposed 1 Hz solution rate. Parse GN as well as GP talker prefixes; do not carry over the old u-blox binary-message configuration. [Exact selected product](https://www.adafruit.com/product/5440).

| Label | Proposed treatment | Physical pad status |
| --- | --- | --- |
| VIN | SENSOR_3V3 power input | Legacy CAD JP1/2; confirm #5440 revision |
| GND | GND | Legacy JP1/3; confirm |
| TX | Teensy 7 / RX2 | Legacy JP1/5; confirm |
| RX | Teensy 8 / TX2 | Legacy JP1/4; confirm |
| 3.3V | Regulator output; leave unconnected | Legacy JP1/9; confirm |
| EN | Leave at onboard enabled default; no GPIO assigned | Legacy JP1/8; confirm |
| VBAT | No carrier supply connection in current proposal; backup coin cell not selected | Legacy JP1/7; confirm holder and revision |
| FIX | Output; unused, read fix status from received data | Legacy JP1/6; confirm |
| PPS | Output; unused for initial serial timestamp plan. Revisit if precise synchronization is required | Legacy JP1/1; confirm |

The [general Ultimate GPS guide](https://learn.adafruit.com/adafruit-ultimate-gps/pinouts) describes these functions, including EN's default pull-up and optional backup power. The [published CAD inspected](https://github.com/adafruit/Adafruit-Ultimate-GPS/tree/70430c1240b49c1e054f1edee84ad0b5ec8ebe56) names PA6H. Connector numbers above are comparison aids, **not an approved PA1616D physical map**. The #5440 page records a September 2024 update with a preinstalled coin-cell holder; reserve underside clearance and confirm the exact board before footprint release.

## Pull-up and bus review

With only the two selected sensor boards, each host-side bus line has two documented 10 kΩ pull-ups. Their parallel equivalent is 5 kΩ. At a hypothetical 0 V low level, these host-side resistors alone draw 3.3/5000 = 0.66 mA. This is not the total sink current through both level-shifter networks: sensor-side pull-ups and any additional board/cable resistors also contribute.

Do not populate extra carrier pull-ups blindly. Reserve optional footprints if useful, then choose population from the full network and measured rise times. Check logic-high voltage, low-level voltage, edges and clock stretching with both modules installed. Keep 100 kHz as an initial bring-up choice; the old firmware's 400 kHz setting is not a validated configuration for this new combination. An address scan should find 0x28, 0x40 and 0x76, but a successful scan alone does not prove reliable acquisition.

## Power-load worksheet

These are planning inputs, not guaranteed peak limits. All breakout VIN pins are proposed on SENSOR_3V3; Teensy VIN is proposed on a regulated 5 V controller rail. A separate sensor regulator versus Teensy's 3.3 V output is undecided.

| Load | Available planning input | Missing before regulator/battery sizing |
| --- | --- | --- |
| Teensy 4.1 | Workbook 100 mA at 5 V | Actual firmware/clock draw and SD transients |
| BNO055 breakout | Workbook 15 mA at 3.3 V | Mode-specific maxima, breakout overhead and startup |
| MS8607 breakout | Workbook 5 mA at 3.3 V | Conversion duty cycle, onboard LED/regulator overhead and peak |
| PA1616D breakout | Product page lists 34 mA acquisition / 29 mA tracking | Full-board peak, backup arrangement and any active antenna load |
| Added status LEDs, divider, regulator losses | Not yet budgeted | Parts, currents and operating duty cycle |
| microSD | Explicitly excluded by workbook | Chosen card and measured writes/startup; include once in the correct rail budget |

The workbook sensor estimates total 54 mA. That arithmetic is useful for preliminary comparison only; it does not prove the Teensy 250 mA external-rail recommendation is satisfied under every condition. Do not size the battery from the inherited 0.6782 W alone. Preserve the original workbook and create the final power budget after the circuit and load peaks are established.

## Mechanical source comparison

| Module | Source geometry reviewed | Decision |
| --- | --- | --- |
| BNO055 #2472 / non-QT | Outline 26.67 × 20.32 mm; 2.54 mm header pitch; rows at Y=1.27 and 19.05 mm; four 2.5 mm mounting holes at X=2.54/24.13, Y=2.54/17.78 mm | Source geometry established for target family; create a new complete carrier footprint and check printed fit/height before release |
| MS8607 #4716 | Outer extent 25.4 × 17.78 mm; 2.54 mm header pitch; holes at X=2.54/22.86, Y=2.54/15.24 mm, diameter 2.5 mm | Source geometry extracted. CAD also contains internal layer-20 segments around the sensor region; preserve/review this detail instead of reducing the module to a rectangle |
| PA1616D #5440 | Product envelope 34.2 × 25.3 × 11.4 mm. Older PA6H CAD extent 25.4 × 34.29 mm in its X/Y orientation, two mounting holes | Envelope is useful for initial placement; exact header/hole/underside geometry not approved |
| Teensy 4.1 | Existing carrier has two 24-position side rows at 2.54 mm pitch, 15.24 mm row separation | Pin-function map checked; full outline, connector/SD overhang, underside parts and socket height still need comparison with the official drawing and chosen mounting hardware |

Module-hole drill sizes describe the manufacturer's board, not automatically the correct carrier fastener clearance. Header drills must match the chosen mating headers/sockets and fabrication process. The proposed mechanical approach is a top-mounted header carrier, subject to retention and enclosure requirements. [PJRC mechanical drawings](https://www.pjrc.com/store/teensy41.html#tech).

### Why the existing BNO055 footprint cannot be retained

Local `BNO055.kicad_mod` contains only four electrical pads: `3V3` (8.89, −2.54), `GND` (11.43, −2.54), `SCL` (13.97, −2.54), `SDA` (16.51, −2.54), plus one mechanical hole. Negating Y to compare with Eagle places them at QT JP3 pads 2–5. The non-QT #2472 has SDA then SCL, different row positions, and different hole spacing. Neither a matching sensor name nor the baseline's zero unconnected items establishes compatibility. The new footprint must expose VIN separately from 3Vo and include the selected board's complete mounting envelope.

### Imported power labels to reconcile

The native netlist places Teensy `3.3V_1` on `A3V3`, `3.3V_2` on `3V3`, `GND1` on `AGND`, `GND2` on `GND`, and `GND3` on `GND_1`. Those labels do not establish independent isolated power domains on the Teensy module. Review the PJRC schematic and carrier return paths before renaming or joining nets; do not connect another regulator output merely because a legacy net is labeled 3V3. The old GPS alternatives share RX2/TX2, and the old OLED/LSM/MS5611 share the I2C nets. Remove obsolete branches deliberately during Step 5.

## Completion and next work

- [x] Exact product family selected by Saadat; modules not yet purchased.
- [x] Official I2C/UART functions, address compatibility and breakout VIN/logic strategy documented.
- [x] Every sensor header function assigned a connection or explicit unused disposition; GPS pad numbering remains provisional.
- [x] Manufacturer CAD commits and hashes recorded; BNO055 mismatch identified; MS8607 coordinates extracted.
- [ ] Exact #5440 mechanical/revision match and full Teensy mechanical comparison.
- [x] Create and source-check BNO055 #2472 and MS8607 #4716 draft carrier footprints; registered as `Pterodactyl_Modules`.
- [ ] Complete remaining module footprints, select mounting hardware/height and check physical fit.
- [ ] Set final current limits, rail source, battery-dependent circuitry and optional reset/control/LED GPIOs.
- [ ] Bench-check voltage levels, simultaneous I2C/UART operation and failure recovery (Step 6).

Step 3's connection research and two native draft footprints are documented, but mechanical approval is incomplete. Step 4 placement/interference planning can use the known envelopes while retaining these gates. An isolated footprint fixture passed DRC; the unchanged main board was not rechecked. No physical verification or firmware compilation was performed.

Evidence: [source manifest](reference/step3-source-manifest.json), [CAD geometry extraction](reference/step3-cad-geometry.json), and the existing [baseline netlist](validation/2026-10-18/schematic-netlist.xml). Raw manufacturer files were inspected in a scratch directory; the manifest links immutable upstream versions so the team can reproduce the comparison. The geometry file records CAD facts, not an approved KiCad footprint.
