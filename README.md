# Team PTERODACTYL

Working files for the UMD near-space PTERODACTYL sensor-board redesign. The current board is an imported **v3.8 v11 baseline**, not a completed next-launch design or a fabrication release.

## Open the design

Use KiCad 10 to open `Native_KiCad_v11/PTERODACTYL_v3.8_v11.kicad_pro`. The project contains a native KiCad schematic, PCB, imported symbol and footprint libraries, and project-local library tables. These files were converted from the supplied Autodesk Fusion/Eagle source; component choices and connectivity still need engineering review.

| Folder or file | Purpose |
|---|---|
| `Native_KiCad_v11/` | Editable KiCad project and the saved October 7, 2026 PCB DRC report |
| `KiCad_import/` | Eagle XML schematic and board pair prepared for KiCad's Eagle importer |
| `Original_Fusion_source/` | Supplied editable `.f3z`, `.sch`, and `.brd` files for comparison |
| `Firmware_reference/` | Original v19 and v19.1 firmware archives from the supplied package; not validated for this redesign |
| `Reference_Gerbers_v12_DO_NOT_ORDER/` | Historical Gerbers for revision comparison only |
| `PTERODACTYL_V3.8_Setup_reference.pdf` | Original setup guide from the supplied package |
| `CUSTOM_BOARD_BRIEF.md` | Sensor goals and decisions still to make |

## Current state

The imported PCB has approximately 97.79 × 97.79 mm outer dimensions, four copper layers, 39 footprints, 417 tracks, and two refilled copper zones. It uses a Teensy 4.1 baseline. The saved PCB DRC reported **11 errors, 428 warnings, and 0 unconnected items**. Schematic ERC and schematic/PCB parity have not been verified. The native schematic file is present, but its symbols, pin mapping, and connectivity require review against the original source.

The supplied Gerbers say v3.8 **v12** while the editable Fusion source says v3.8 **v11**; the Gerber job metadata also contains a v3.7 identifier. Reconcile those revisions before using any prior files for fabrication.

## Next-launch work

The intended board should log gyroscope, accelerometer, GPS, pressure, temperature, and derived altitude data. Keep Teensy 4.1 for now. Live telemetry, final sensors, battery, environmental requirements, and the local PCB manufacturer's design rules remain undecided. See `CUSTOM_BOARD_BRIEF.md`.

Before fabrication: agree on the requirements and reference revision; review the schematic and all footprints against component datasheets; check power, pin mapping, routing, and board dimensions; resolve DRC/ERC failures; generate fresh Gerbers and drill files from the approved KiCad board; inspect them in a Gerber viewer; and obtain a hardware review and prototype test.

## Collaborating

Clone this private repository, open the `.kicad_pro` file, and commit changes on a branch. Keep the KiCad project, schematic, PCB, and local libraries together. Do not commit editor lock files or local UI settings. Explain changes to connectors, sensors, pin mapping, and power in the commit or pull request so they can be checked against the schematic and firmware.

**Do not send the reference Gerbers or this imported baseline directly to a manufacturer.**
