# Step 3 — carrier footprint review

October 18, 2026. Two **draft carrier footprints** have been created and registered in the project-local library `Pterodactyl_Modules`. The main schematic and PCB have not been changed or assigned these footprints. No modules have been purchased, so physical fit remains untested.

## Available footprints

| Library item | Intended module | Electrical pads | Mounting proposal |
| --- | --- | ---: | --- |
| `Pterodactyl_Modules:Adafruit_BNO055_2472_Carrier` | Adafruit #2472, non-STEMMA-QT BNO055 | 10, both header rows | Four NPTH carrier holes at manufacturer module-hole centers |
| `Pterodactyl_Modules:Adafruit_MS8607_4716_Carrier` | Adafruit #4716 MS8607 | 5 | Four NPTH carrier holes at manufacturer module-hole centers |

The library lives in `Native_KiCad_v11/Pterodactyl_Modules.pretty`. `fp-lib-table` uses `${KIPRJMOD}`, so cloning the repository preserves the path. Open the project in KiCad and use the Footprint Editor library browser to inspect `Pterodactyl_Modules`. These footprints will require corresponding module symbols during Step 5; do not assign the new numeric pads to the old imported symbol by name alone.

## Pad numbering contract

The carrier uses unique numeric pads. Numbers do not restart at the second BNO055 header.

| Module | Carrier pads and functions | Manufacturer header mapping |
| --- | --- | --- |
| BNO055 | 1 VIN, 2 3Vo, 3 GND, 4 SDA, 5 SCL, 6 RST | JP1 pads 1–6 |
| BNO055 | 7 PS0, 8 PS1, 9 INT, 10 ADR | JP2 pads 1–4 |
| MS8607 | 1 VIN, 2 3Vo, 3 GND, 4 SCL, 5 SDA | JP2 pads 1–5 |

VIN and 3Vo are deliberately different pads: the planned supply goes to VIN; the regulator output remains unconnected on the carrier. Retain physically present header pads even when their electrical function is unused. Mark intentional unused pins in the new schematic after review. See [connection dispositions](SENSOR_CONNECTION_MAP.md) and the [machine-readable pad map](reference/step3-carrier-pad-map.csv).

Footprint origin is VIN pad 1. Manufacturer Eagle coordinates are converted as `Xcarrier = Xsource − XVIN`, `Ycarrier = YVIN − Ysource`. This produces the top/component-side mounting view in KiCad without exchanging SDA and SCL. Pin 1 is rectangular and has a silkscreen triangle. Labels on F.Fab show pad number and function.

## Geometry and assembly assumptions

- Header centers, row offsets, module outline arcs and mounting centers come from the pinned manufacturer CAD listed in the [source manifest](reference/step3-source-manifest.json).
- Header pads are provisionally 1.8 mm diameter with 1.0 mm finished drill; VIN is a 1.8 mm square pad. Select actual mating headers/sockets and check recommended drill/tolerance before release.
- Module CAD holes are 2.5 mm. The carrier currently proposes 2.7 mm **non-plated** clearance holes at the same centers. This is an assembly choice, not a copied manufacturer requirement. Confirm screw/standoff size, magnetic material suitability near BNO055, washer/head dimensions, and clearance to copper.
- Drawing-layer circles show a provisional 3 mm radius around fastener centers. They are reference envelopes, not enforced copper or component keepouts. Review them when routing and placing other parts.
- F.Fab contains the module outline. It is **not** on Edge.Cuts and will not cut that outline into the carrier. The MS8607 source's internal layer-20 segments are also preserved on F.Fab for review, not copied as carrier milling.
- F.CrtYd reserves the module outer rectangle plus a provisional 1 mm margin. This does not include a guaranteed plugged-in STEMMA cable envelope, an electrical interference distance or a thermal isolation distance. The current proposal uses headers and leaves STEMMA ports unplugged.
- `NO PARTS UNDER MODULE` on Dwgs.User is an assembly constraint for the initial design, not a KiCad rule area. Before placing other carrier components underneath, prove clearance using the chosen sockets/standoffs, underside components, solder joints and tolerance stack.
- Socket height, retention, final fasteners and enclosure remain unselected. No 3D models were added, so KiCad's 3D view cannot yet prove the assembled height or fit.

## Verification performed

1. Regenerated footprints from the saved source-geometry JSON with `tools/generate_module_footprints.py`.
2. Loaded both files with KiCad 10.0.7 `pcbnew.FootprintLoad`. The independent native-readback check compared all 15 numbered pads and eight mounting positions against the source coordinates, and checked pad counts/types and provisional drills. [Check report](validation/2026-10-18/step3-footprints/source-coordinate-check.json).
3. Exported SVGs through KiCad's footprint exporter, rendered and visually inspected both. Confirmed row order, pin-one locator, mounting positions and module outlines; adjusted the MS8607 annotation to avoid crossing the internal outline.
4. Placed both footprints on an isolated, unrouted test board and ran KiCad DRC with all severities: **0 violations and 0 unconnected items**. [Native report](validation/2026-10-18/step3-footprints/footprint-check-drc.json). The fixture has no circuit nets or schematic; this result checks local geometric issues, not actual connectivity, manufacture, physical fit or sensor performance. It does not replace the main project's existing failing ERC/DRC results.

The [fixture board](validation/2026-10-18/step3-footprints/footprint-check.kicad_pcb) is evidence only, not a PCB design or fabrication source. Previews: [BNO055 SVG](validation/2026-10-18/step3-footprints/Adafruit_BNO055_2472_Carrier.svg), [MS8607 SVG](validation/2026-10-18/step3-footprints/Adafruit_MS8607_4716_Carrier.svg). Screen images are not dimensionally reliable print templates; check any printed fit drawing at actual size with a ruler.

The fixture uses default DRC configuration. `--severity-all` includes all configured severities but does not enable ignored checks; the JSON records five ignored categories. No schematic-parity check was possible for this netless fixture. Courtyard outlines were inspected in the native previews.

To reproduce from the repository root, use ordinary Python 3 for `tools/generate_module_footprints.py` and KiCad's Python for `tools/verify_module_footprints.py`. On Saadat's machine, the latter is `C:\Program Files\KiCad\10.0\bin\python.exe`. Run `kicad-cli fp export svg` on `Native_KiCad_v11/Pterodactyl_Modules.pretty` to regenerate previews. Preserve the source geometry and manifest when moving the generator.

## Teensy and GPS status

**Teensy:** the imported footprint's two rows were previously found to contain 24 positions each, at 2.54 mm pitch and 15.24 mm separation. Signal functions have been checked, but its complete outline/USB/SD/underside geometry has not been approved. A browser attempt to inspect PJRC's dimension drawing was denied by browser security policy during this continuation. No alternative route was used to bypass that denial. The existing Teensy footprint was left unchanged; full drawing and physical mounting checks remain open.

**GPS:** a fresh check found only the `master` branch in Adafruit's Ultimate GPS PCB repository. The last commit affecting `Adafruit Ultimate GPS.brd` was `c8ae9a95d82f77d3bbd023754dee658959864e5c`, November 12, 2017. It still names PA6H, predating the selected PA1616D #5440 and its September 2024 holder revision. The top-level Adafruit CAD-parts listing checked in this continuation did not provide a #5440 entry. These checks did not establish exact #5440 mechanics. [Recorded history](reference/step3-gps-cad-history.json), [official repository history](https://github.com/adafruit/Adafruit-Ultimate-GPS/commits/master/Adafruit%20Ultimate%20GPS.brd).

Do not release a GPS carrier footprint from that older file. The remaining evidence can come from an exact #5440 mechanical drawing/CAD revision supplied by the manufacturer or measurements of the purchased board, including header order/pitch, holes, antenna orientation and underside holder clearance. The selected product remains #5440; this is a verification gap, not a proposal to substitute another GPS.

## Remaining Step 3 work

1. Resolve the exact GPS mechanical evidence and complete the Teensy drawing comparison.
2. Select header/socket and fastener arrangements, including module height and retention; revise the provisional carrier drills/envelopes if needed.
3. Review symbol-to-footprint pin mapping before assignment during schematic work.
4. Check actual module fit after purchase and retain the bench interface tests in Step 6.

Step 3 has progressed from documentation to native footprint assets, but mechanical release is still open. Interference planning can proceed with these draft envelopes. Battery-dependent circuit design remains Step 5 work.

## Attribution

The footprint geometry derives from Adafruit Industries' BNO055 Breakout PCB and MS8607 PCB files at the commits in the source manifest. These derived footprint files are distributed under Creative Commons Attribution-ShareAlike 3.0 Unported; a copy is in `Native_KiCad_v11/Pterodactyl_Modules_LICENSE.txt`. Changes include coordinate conversion, unique carrier pad numbering, proposed carrier hole/pad sizes, labels and assembly envelopes. This attribution does not imply Adafruit reviewed or approved the carrier design.
