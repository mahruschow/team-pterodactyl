# Team PTERODACTYL

Working files for the UMD near-space PTERODACTYL sensor-board redesign. The current board is an imported **v3.8 v11 baseline**, not a completed next-launch design or a fabrication release.

## Team handoff and planning

For a quick picture of progress and what's left, read [docs/REMAINING_WORK.md](docs/REMAINING_WORK.md). Start with [docs/README.md](docs/README.md) for the shared planning directory, then [current status and resume steps](docs/CURRENT_STATUS.md). The directory includes requirements, the development plan, session notes, the supplied parts workbook and native KiCad validation evidence so teammates can continue without the previous chat.

Step 3 now includes a project-local `Pterodactyl_Modules` library with draft BNO055 #2472/MS8607 #4716 carrier footprints with matching symbols, a Teensy SSW carrier, and an unassigned GPS #5440 logical symbol, plus documented connector/mounting proposals. They are not assigned to the main circuit. See [the footprint review](docs/FOOTPRINT_REVIEW.md) for pin mapping, validation and outstanding physical-fit requirements.

Step 5 adds a separate **draft v4 schematic** in `Native_KiCad_v4/`, built from the documented connection map and power architecture. It passes ERC with 0 violations and matches an independent net list, but it is not yet team-reviewed. Step 7 adds a placed (not yet routed) v4 PCB in the same project; see [the draft layout](docs/PCB_LAYOUT_V4.md). See [the power architecture and schematic plan](docs/POWER_ARCHITECTURE.md).

## Open the design

Use KiCad 10 to open `Native_KiCad_v11/PTERODACTYL_v3.8_v11.kicad_pro`. The project contains a native KiCad schematic, PCB, imported symbol and footprint libraries, and project-local library tables. These files were converted from the supplied Autodesk Fusion/Eagle source; component choices and connectivity still need engineering review.

| Folder or file | Purpose |
|---|---|
| `Native_KiCad_v11/` | Editable KiCad project and the saved October 7, 2026 PCB DRC report |
| `Native_KiCad_v4/` | Draft v4 project: schematic (Step 5) and placed, unrouted PCB (Step 7); see docs/PCB_LAYOUT_V4.md |
| `KiCad_import/` | Eagle XML schematic and board pair prepared for KiCad's Eagle importer |
| `Original_Fusion_source/` | Supplied editable `.f3z`, `.sch`, and `.brd` files for comparison |
| `Firmware_v4/` | Draft v4 logger firmware (Step 6); compiles for Teensy 4.1, not yet hardware-tested |
| `Firmware_reference/` | Original v19 and v19.1 firmware archives from the supplied package; not validated for this redesign |
| `Reference_Gerbers_v12_DO_NOT_ORDER/` | Historical Gerbers for revision comparison only |
| `PTERODACTYL_V3.8_Setup_reference.pdf` | Original setup guide from the supplied package |
| `CUSTOM_BOARD_BRIEF.md` | Sensor goals and decisions still to make |

## Current state

The imported PCB has approximately 97.79 × 97.79 mm outer dimensions, four copper layers, 39 footprints, 417 tracks, and two refilled copper zones. It uses a Teensy 4.1 baseline. A fresh KiCad 10.0.7 audit on October 18, 2026 reproduced **11 PCB DRC errors, 428 warnings, and 0 unconnected items**. Schematic ERC reported **33 errors and 10 warnings**, with **52 additional schematic/PCB parity warnings**. These findings remain unresolved. See the [validation report](docs/validation/2026-10-18/VALIDATION_SUMMARY.md) for triage and check limitations, and the [development plan](docs/DEVELOPMENT_PLAN.md) for next steps. The symbols, pin mapping, power architecture and exact module footprints still require engineering review.

The supplied Gerbers say v3.8 **v12** while the editable Fusion source says v3.8 **v11**; the Gerber job metadata also contains a v3.7 identifier. Reconcile those revisions before using any prior files for fabrication.

## Next-launch work

The intended board should log gyroscope, accelerometer, orientation, GPS, pressure, humidity, temperature, and derived altitude data. The working selection is Teensy 4.1 with Adafruit BNO055 2472, MS8607 4716 and PA1616D GPS 5440. The lead has specified no telemetry: record onboard to microSD for analysis after recovery. Saadat selected the core logger with power control, status LEDs and supply monitoring; OLED, remote probes, alternative IMU, heater and servos are outside this scope. Component placement must address interference. Battery/runtime, quantitative performance, enclosure/environment, exact control workflow and manufacturer constraints remain open. See `CUSTOM_BOARD_BRIEF.md` and the [version-one requirements draft](docs/V1_REQUIREMENTS.md), which distinguishes the selected baseline from proposed behavior and open decisions.

Before fabrication: agree on the requirements and reference revision; review the schematic and all footprints against component datasheets; check power, pin mapping, routing, and board dimensions; resolve DRC/ERC failures; generate fresh Gerbers and drill files from the approved KiCad board; inspect them in a Gerber viewer; and obtain a hardware review and prototype test.

## Collaborating

Clone this private repository, open the `.kicad_pro` file, and commit changes on a branch. Keep the KiCad project, schematic, PCB, and local libraries together. Do not commit editor lock files or local UI settings. Explain changes to connectors, sensors, pin mapping, and power in the commit or pull request so they can be checked against the schematic and firmware.

**Do not send the reference Gerbers or this imported baseline directly to a manufacturer.**
