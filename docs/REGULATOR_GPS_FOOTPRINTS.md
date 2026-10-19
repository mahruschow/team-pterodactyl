# Regulator and GPS footprint work — October 19, 2026

**U2 now has a source-checked regulator footprint in the v4 schematic and PCB. The GPS has a separate, explicitly unverified comparison footprint; U5 remains unassigned.** Neither installed mechanical fit nor fabrication approval is implied.

## Regulator carrier

Library: `Pterodactyl_Modules:Pololu_S9V11F5_SSW_Carrier`, in the existing shared `Native_KiCad_v11/Pterodactyl_Modules.pretty` library registered by the v4 project. This library location does not mean the legacy v3.8 board was changed.

Sources are Pololu's [#2836 resources](https://www.pololu.com/product/2836/resources), [reg20a dimension drawing](https://www.pololu.com/file/0J1272/pololu-5v-step-up-step-down-voltage-regulator-s9v11f5-dimensions.pdf), [drill guide](https://www.pololu.com/file/0J1271/reg20a-drill.dxf), and the manufacturer's [labelled bottom-side pinout](https://a.pololu-files.com/picture/0J7676.1200.jpg?5bafbdcc9aff1d21b674e817d7ee5ab9). Local copies and hashes are in `reference/regulator-gps/`. The drawing and photographs are copyright Pololu Corporation; the carrier footprint is our implementation of their interface dimensions.

The footprint assumes the module lies parallel to the carrier, **inductor/silkscreen side up**, with its header at the bottom of the footprint. Left to right, the named pads are VIN, GND and VOUT. The square centre pad follows the module's GND marker; do not interpret it as VIN. These identifiers match the new `Pterodactyl_v4:Pololu_S9V11F5_Header` symbol directly.

| Feature | Implemented nominal geometry |
| --- | --- |
| Module outline | 7.62 × 11.43 mm, converted from drawing's 300 × 450 mil dimensions; rounded metric labels are 7.6 × 11.4 mm |
| Header centres | VIN (0,0), GND (2.54,0), VOUT (5.08,0) mm |
| Module boundary relative to VIN | X −1.27 to 6.35; Y −10.16 to 1.27 mm |
| Carrier holes/pads | 1.04 mm plated drills, 1.8 mm pads for proposed SSW sockets; these are carrier holes, not a copy of module drill sizing |
| Courtyard | Nominal module rectangle plus 1 mm allowance, encompassing the candidate socket body |
| Under-module area | Front-side component keepout; tracks, vias and copper remain allowed |

The manufacturer's drawing specifies drill-position tolerance ±0.1 mm and board-edge tolerance ±0.3 mm. The courtyard allowance does not prove connector fit. Proposed connector pair: Samtec SSW-103-01-L-S carrier socket with HTSW-103-07-L-S module header, following the already documented SSW/HTSW family dimensions. Stock/orderable configuration, tolerance stack, soldering and retention must be checked. The regulator has no mounting holes; the team still needs a suitable retention arrangement. Do not rely on a removable socket alone for flight retention.

The carrier exposes only the three header pins. EN stays on the module and is not brought to a fictitious fourth carrier pad. U2's former logical EN pin and corresponding no-connect marker were removed; the module's normal enabled behavior is unchanged. At least **3 V at module VIN is required for startup**; operation down to 2 V applies only after startup. Battery sag, protection and wiring drops still need margin in the final power specification. [Pololu electrical guidance](https://www.pololu.com/product/2836).

U2 replaces its old envelope at the bottom-right of the current board. VIN is assigned `/VBAT_SW`, GND to `GND`, and VOUT to `+5V`. The two non-ground connections remain unrouted. Existing 49 footprint positions, pad geometry/net identities, and all 192 track segments plus 10 vias are unchanged; zone fills were refreshed for the added pad. KiCad reserialization and changed zone fill geometry account for much of the PCB text diff.

## GPS comparison footprint

Library: `Pterodactyl_Modules:Adafruit_GPS_5440_UNVERIFIED_Legacy_Carrier`.

This is derived from the recorded Adafruit Ultimate GPS CAD at commit `70430c1240b49c1e054f1edee84ad0b5ec8ebe56`, which identifies the older PA6H board. It includes the rounded outline, nine header pads, two proposed carrier mounting holes, a courtyard, a component keepout and a visible **UNVERIFIED #5440** warning. The source coordinates match the recorded CAD; that does not establish a match to current #5440 hardware.

Designed by Limor Fried/Ladyada for Adafruit Industries. Source: [Adafruit Ultimate GPS PCB](https://github.com/adafruit/Adafruit-Ultimate-GPS/tree/70430c1240b49c1e054f1edee84ad0b5ec8ebe56). GPS geometry adaptation is CC BY-SA 3.0; see `Native_KiCad_v11/Pterodactyl_Modules_LICENSE.txt`. Changes: Eagle-to-KiCad coordinate conversion, named carrier pads, proposed socket drills, enlarged carrier mounting holes, courtyard/keepout and revision warnings. Support Adafruit's open-source hardware by purchasing the original product.

Origin is the legacy JP1 pad 1 (PPS). Pads progress in negative X at 2.54 mm pitch: PPS, VIN, GND, RX, TX, FIX, VBAT, EN, 3V3_OUT. These names match the existing logical GPS symbol. Carrier electrical drills are 1.04 mm; the two 2.7 mm NPTH holes are a carrier fastener-clearance proposal for the legacy 2.5 mm module holes. A candidate SSW-109 socket body is shown. Actual #5440 socket/header selection, spacer height, battery-holder clearance and retention remain open.

**M01 remains open.** The current [#5440 page](https://www.adafruit.com/product/5440) records the September 2024 PCB/coin-cell-holder update. Before assigning this footprint, obtain revision-matched manufacturer CAD/dimensions or measure an actual #5440: all header functions/centres, both hole centres/diameters, outline, underside holder and antenna envelopes. The GPS remains a keepout envelope on the main PCB; its symbol's footprint field is blank.

## Validation and reproduction

Run with KiCad 10's Python:

```powershell
& 'C:\Program Files\KiCad\10.0\bin\python.exe' -B tools/generate_power_gps_footprints.py
& 'C:\Program Files\KiCad\10.0\bin\python.exe' -B tools/verify_power_gps_footprints.py
```

The first command regenerates only these two library footprints. The second reads them natively, compares regulator header centres against the DXF crosses, checks GPS pads/holes against the recorded source, verifies named symbol/pad contracts, exports an isolated fixture, runs native checks, compares all 32 schematic nets and 35 intentional no-connects, and tests whether moving the IMU in memory changes the placement result. Neither command regenerates the routed board.

Results in [validation/2026-10-19/regulator-gps](validation/2026-10-19/regulator-gps/):

- Source-coordinate and symbol/pad checks: pass for 3 regulator pads, 9 GPS pads and 2 GPS mounting holes.
- Isolated fixture physical DRC: 0 violations.
- Main schematic ERC: 0 violations; main board enabled physical DRC: 0 violations.
- Main parity: only missing U5. Main board: **12 unconnected items**, versus 10 before U2 pads existed.
- Seven placement targets pass. The checker now reads live PCB geometry instead of `placement.json`; the deliberate in-memory move fails PC1 as intended.
- Existing placement and routing preservation check: pass. No firmware changes or hardware tests.

Preview: [footprint fixture](validation/2026-10-19/regulator-gps/footprint-fixture.svg), [current board top](validation/2026-10-19/regulator-gps/board-top.svg).

Next: verify GPS M01, agree connector/retention details, complete the open power connections, and perform physical module fit checks before fabrication approval. Do not rerun the full schematic/PCB generators over hand edits; their definitions were updated for consistency, but only targeted integration was performed on the existing routed design.
