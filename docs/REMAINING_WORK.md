# What's done and what's left

Updated October 19, 2026 by Saadat (with Claude). Branch: `saadat-dev`. This is the one-page checklist for keeping the team in sync. Details are in the linked documents. [CURRENT_STATUS.md](CURRENT_STATUS.md) stays the full resume record.

## Where the project is

**Latest layout cleanup:** [LAYOUT_REVIEW_CLEANUP.md](LAYOUT_REVIEW_CLEANUP.md). C2 is now 4.493 mm from the carrier ADC pin; I2C follows Teensy → MS8607 → BNO055 (135.163/128.209 mm). Added three return-path stitching vias and readable silkscreen. Fresh enabled physical DRC and present-footprint unconnected counts are both 0; U5 remains missing. See the review for unchanged geometry, test evidence and remaining power-integrity/mechanical/manufacturer gates.

**Latest routing checkpoint:** [POWER_ROUTING.md](POWER_ROUTING.md). All connections among the 50 placed footprints are now routed: 0 enabled physical DRC violations, 0 unconnected items, and only U5/GPS missing in schematic parity. U5 is still absent, so this does not mean all schematic connections are implemented. TP1/TP2/TP4 were moved near their rails; a 68.667 mm unloaded TP1 spur was removed. No new vias; original signal routes and design rules are preserved. GPS geometry, layout/assembly review and fabrication gates remain open.

**Footprint update:** [REGULATOR_GPS_FOOTPRINTS.md](REGULATOR_GPS_FOOTPRINTS.md). U2 is assigned and placed; U5 remains unassigned. Fresh checks find 12 unconnected items, only U5 missing, and zero ERC/enabled physical DRC violations. GPS legacy comparison geometry is drafted but M01 is still open. Earlier autoroute counts below are historical.

| Step | State | Proof / where to look |
| --- | --- | --- |
| 1. Check the old v3.8 design | ✅ Done | [VALIDATION_SUMMARY.md](validation/2026-10-18/VALIDATION_SUMMARY.md) |
| 2. Requirements | 🟡 Scope agreed; numbers open | [V1_REQUIREMENTS.md](V1_REQUIREMENTS.md) |
| 3. Module wiring and mounting | 🟡 Drafted; needs GPS geometry and a test fit | [SENSOR_CONNECTION_MAP.md](SENSOR_CONNECTION_MAP.md), [MODULE_ASSEMBLY_PLAN.md](MODULE_ASSEMBLY_PLAN.md) |
| 4. Placement and interference | 🟡 Drafted; needs team review | [PLACEMENT_AND_INTERFERENCE.md](PLACEMENT_AND_INTERFERENCE.md) |
| 5. Power design and schematic | 🟡 Drafted and checked (ERC clean) | [POWER_ARCHITECTURE.md](POWER_ARCHITECTURE.md), [schematic PDF](validation/2026-10-19/step5-schematic/PTERODACTYL_v4.pdf) |
| 6. Firmware | 🟡 Written; compiles; not run on hardware | [FIRMWARE_V4.md](FIRMWARE_V4.md) |
| 7. PCB layout | 🟡 All placed footprints routed; GPS footprint/wiring and final review remain | [PCB_LAYOUT_V4.md](PCB_LAYOUT_V4.md), [render](validation/2026-10-19/step7-pcb/v4-top.png), [copper](validation/2026-10-19/step7-pcb/v4-copper.pdf) |
| 8. Order prototype | ⬜ Not started | — |
| 9. Build and test | ⬜ Not started | — |
| 10. Flight version | ⬜ Not started | — |

**What we can show today:** the v4 schematic PDF, the autorouted v4 board (render and copper PDF) and the floor plan. **What we can't show yet:** a finished, reviewed layout or anything running on hardware.

## Routing status (Step 7)

The targeted power-routing pass closes all 12 previously reported unconnected items. It adds 37 power segments and removes five segments of the unloaded TP1 spur. The board now has 224 segments / 10 vias, with no inner-plane tracks; I2C remains 110.5 mm. See [POWER_ROUTING.md](POWER_ROUTING.md) for current checks and images. The historical first-pass counts below describe earlier milestones.

## To-do list

### Review findings to close

See [V4_DESIGN_REVIEW.md](V4_DESIGN_REVIEW.md) for exact locations, failure cases and validation expectations.

- [ ] Finish U2/U5 footprints and all open supply connections; require clean parity and zero unconnected items.
- [ ] Propagate actual sensor transfer/CRC failures rather than logging invalid or stale values as `OK`.
- [ ] Add a timeout inside the BNO055 post-reset polling path so other streams continue on failure.
- [ ] Make required SD file opening transactional and implement storage failure recovery.
- [ ] Correct the power contract: at least 3 V at regulator VIN for startup, with battery and wiring margin.
- [ ] Track GPS RMC validity/age when combining its fields with GGA.
- [x] Derive placement separation checks from the current PCB rather than the saved placement JSON; deliberate in-memory IMU move is detected.

### Needs the team lead (blocking)
Send [TEAM_LEAD_REQUESTS.md](TEAM_LEAD_REQUESTS.md). The most important items:

- [ ] **R1:** approval to buy one of each module (Teensy 4.1, BNO055 #2472, MS8607 #4716, GPS #5440). This unblocks the GPS footprint, the test fit and firmware testing.
- [ ] **R3/R6:** enclosure and how the board is mounted in flight.
- [ ] **R7 / D02:** battery type and where it sits.
- [ ] **R8:** venting, and whether temperature/humidity should be outside air.
- [ ] **R5 / D08:** PCB manufacturer, which sets the design rules.
- [ ] **D10:** how the logger is started and stopped (switch, button, pull-before-flight).

### Saadat (PCB design)
- [x] First-pass autoroute (DRC clean; 6 supply connections open).
- [x] Finish open power connections on present footprints; move TP1/TP2 near power and TP4 near the sensor rail. Current DRC: 0 violations / 0 unconnected, with U5 still absent.
- [x] Review and correct I2C order, ADC filter proximity and labels; add local ground stitching. See LAYOUT_REVIEW_CLEANUP.md.
- [ ] Final independent layout review, power-transient/decoupling verification and GPS integration after M01; reassess optional outer pours after GPS routing.
- [x] Create, verify, assign and place the Pololu S9V11F5 three-pin carrier footprint. Installed socket/retention fit remains open.
- [ ] Confirm current GPS #5440 geometry (M01), then revise/approve and assign the newly created UNVERIFIED legacy comparison footprint.
- [ ] Set the manufacturer's rules once R5 is answered, and rerun the checks.

### A teammate can do now (no hardware needed)
- [ ] **Review** the schematic PDF and [POWER_ARCHITECTURE.md](POWER_ARCHITECTURE.md); note questions in an issue or the session notes.
- [ ] **Confirm part ratings** from datasheets: PTC fuse voltage, IRLML6402 Vds/Vgs, ferrite bead current, JST connectors. These are marked "(candidate)" in the [BOM](validation/2026-10-19/step5-schematic/bom.csv).
- [x] Find and inspect the Pololu S9V11F5 pinout, dimension drawing and DXF; local source copies and hashes are in `reference/regulator-gps/`.
- [ ] **Write a log-checking script** for the firmware's CSV files: headers, sequence numbers, timing, units (LOG-04). See the formats in [FIRMWARE_V4.md](FIRMWARE_V4.md).
- [ ] **Review the floor plan and interference rules** in [PLACEMENT_AND_INTERFERENCE.md](PLACEMENT_AND_INTERFERENCE.md).

### Once modules arrive
- [ ] Measure the GPS board and close M01; dry-fit all modules (M04).
- [ ] Run the firmware on a Teensy with the modules (the "not verified" list in FIRMWARE_V4.md).

### Before ordering a prototype (Step 8)
- [ ] Routed board passes DRC with 0 unconnected (U2/U5 connections once their footprints exist).
- [ ] Team design review of the schematic and layout.
- [ ] Fresh Gerbers and drill files generated and inspected. The old v12 Gerbers are reference only.

## How to stay in sync

1. Pull `saadat-dev` before starting. For bigger changes, work on your own branch and open a pull request.
2. Read the latest note in [sessions/](sessions/), then this file.
3. **Generated files:** the v4 schematic comes from `tools/generate_v4_schematic.py` and the pre-routing board from `tools/build_v4_pcb.py`. Once someone edits the schematic or routes the board by hand in KiCad, stop rerunning those generators, because they overwrite the files.
4. After changing anything, rerun the matching check (`tools/verify_v4_schematic.py`, `tools/check_v4_pcb.py`, or the firmware compile) and update this checklist and CURRENT_STATUS.md.
