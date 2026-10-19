# What's done and what's left

Updated October 19, 2026 by Saadat (with Claude). Branch: `saadat-dev`. This is the one-page checklist for keeping the team in sync. Details are in the linked documents. [CURRENT_STATUS.md](CURRENT_STATUS.md) stays the full resume record.

## Where the project is

| Step | State | Proof / where to look |
| --- | --- | --- |
| 1. Check the old v3.8 design | ✅ Done | [VALIDATION_SUMMARY.md](validation/2026-10-18/VALIDATION_SUMMARY.md) |
| 2. Requirements | 🟡 Scope agreed; numbers open | [V1_REQUIREMENTS.md](V1_REQUIREMENTS.md) |
| 3. Module wiring and mounting | 🟡 Drafted; needs GPS geometry and a test fit | [SENSOR_CONNECTION_MAP.md](SENSOR_CONNECTION_MAP.md), [MODULE_ASSEMBLY_PLAN.md](MODULE_ASSEMBLY_PLAN.md) |
| 4. Placement and interference | 🟡 Drafted; needs team review | [PLACEMENT_AND_INTERFERENCE.md](PLACEMENT_AND_INTERFERENCE.md) |
| 5. Power design and schematic | 🟡 Drafted and checked (ERC clean) | [POWER_ARCHITECTURE.md](POWER_ARCHITECTURE.md), [schematic PDF](validation/2026-10-19/step5-schematic/PTERODACTYL_v4.pdf) |
| 6. Firmware | 🟡 Written; compiles; not run on hardware | [FIRMWARE_V4.md](FIRMWARE_V4.md) |
| 7. PCB layout | 🟡 Placed and **first-pass autorouted** (DRC clean; 6 supply connections left) | [PCB_LAYOUT_V4.md](PCB_LAYOUT_V4.md), [render](validation/2026-10-19/step7-pcb/v4-top.png), [copper](validation/2026-10-19/step7-pcb/v4-copper.pdf) |
| 8. Order prototype | ⬜ Not started | — |
| 9. Build and test | ⬜ Not started | — |
| 10. Flight version | ⬜ Not started | — |

**What we can show today:** the v4 schematic PDF, the autorouted v4 board (render and copper PDF) and the floor plan. **What we can't show yet:** a finished, reviewed layout or anything running on hardware.

## Routing status (Step 7)

A first-pass autoroute with Freerouting 2.5.0 (portable `.jar` on a Java 25 runtime) is in the board:
- DRC has 0 violations, nothing is routed on the inner GND planes, and I2C is 110.5 mm long.
- 6 supply connections are still open (SENSOR_3V3 decoupling and two +5V points), because the test-point row above the Teensy is a bottleneck.

The clean-up list is in [PCB_LAYOUT_V4.md](PCB_LAYOUT_V4.md#clean-up-list-for-hand-routing). From here, routing is done by hand in KiCad.

## To-do list

### Review findings to close

See [V4_DESIGN_REVIEW.md](V4_DESIGN_REVIEW.md) for exact locations, failure cases and validation expectations.

- [ ] Finish U2/U5 footprints and all open supply connections; require clean parity and zero unconnected items.
- [ ] Propagate actual sensor transfer/CRC failures rather than logging invalid or stale values as `OK`.
- [ ] Add a timeout inside the BNO055 post-reset polling path so other streams continue on failure.
- [ ] Make required SD file opening transactional and implement storage failure recovery.
- [ ] Correct the power contract: at least 3 V at regulator VIN for startup, with battery and wiring margin.
- [ ] Track GPS RMC validity/age when combining its fields with GGA.
- [ ] Derive placement separation checks from the current PCB rather than the saved placement JSON.

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
- [ ] Hand clean-up per [the clean-up list](PCB_LAYOUT_V4.md#clean-up-list-for-hand-routing): finish the 6 connections, move TP1/TP2 near the power section, review against PC6/PC7/PC11, then silkscreen labels, outer GND pours and stitching vias.
- [ ] Make the Pololu S9V11F5 regulator footprint once its pinout is confirmed.
- [ ] Make the GPS #5440 footprint once its geometry is known (M01).
- [ ] Set the manufacturer's rules once R5 is answered, and rerun the checks.

### A teammate can do now (no hardware needed)
- [ ] **Review** the schematic PDF and [POWER_ARCHITECTURE.md](POWER_ARCHITECTURE.md); note questions in an issue or the session notes.
- [ ] **Confirm part ratings** from datasheets: PTC fuse voltage, IRLML6402 Vds/Vgs, ferrite bead current, JST connectors. These are marked "(candidate)" in the [BOM](validation/2026-10-19/step5-schematic/bom.csv).
- [ ] **Find the Pololu S9V11F5 pinout and dimension drawing** (Pololu product #2836 page or its PCB drawing) so the footprint can be made.
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
