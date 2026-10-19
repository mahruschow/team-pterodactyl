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
| 7. PCB layout | 🟡 Parts placed and checked; **not routed** | [PCB_LAYOUT_V4.md](PCB_LAYOUT_V4.md), [render](validation/2026-10-19/step7-pcb/v4-top.png) |
| 8. Order prototype | ⬜ Not started | — |
| 9. Build and test | ⬜ Not started | — |
| 10. Flight version | ⬜ Not started | — |

**What we can show today:** the v4 schematic PDF, the placed v4 board render and the floor plan. **What we can't show yet:** a routed board or anything running on hardware.

## Routing status (Step 7)

A Freerouting autoroute was tried on October 19. Freerouting 2.5.0's Windows command-line build crashed on start-up (a packaging bug in that build; see `validation/2026-10-19/step7-pcb/freerouting.log`). The board was not changed. Ways forward:
- Run the portable Freerouting `.jar` with a Java 25 runtime (only Java 17 is installed on Saadat's machine), using `tools/autoroute_v4_pcb.py`.
- Or route by hand in KiCad.

Either way, the result must be reviewed against PC6, PC10 and PC11 (supply returns, nothing noisy under the GPS, I2C ≤ 150 mm) and checked with `tools/check_v4_pcb.py`.

## To-do list

### Needs the team lead (blocking)
Send [TEAM_LEAD_REQUESTS.md](TEAM_LEAD_REQUESTS.md). The most important items:

- [ ] **R1:** approval to buy one of each module (Teensy 4.1, BNO055 #2472, MS8607 #4716, GPS #5440). This unblocks the GPS footprint, the test fit and firmware testing.
- [ ] **R3/R6:** enclosure and how the board is mounted in flight.
- [ ] **R7 / D02:** battery type and where it sits.
- [ ] **R8:** venting, and whether temperature/humidity should be outside air.
- [ ] **R5 / D08:** PCB manufacturer, which sets the design rules.
- [ ] **D10:** how the logger is started and stopped (switch, button, pull-before-flight).

### Saadat (PCB design)
- [ ] Route the board: autoroute first pass, then hand clean-up, or route by hand. Then place silkscreen labels and add outer-layer GND pours.
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
- [ ] Routed board passes DRC with 0 unconnected, apart from anything explicitly accepted.
- [ ] Team design review of the schematic and layout.
- [ ] Fresh Gerbers and drill files generated and inspected. The old v12 Gerbers are reference only.

## How to stay in sync

1. Pull `saadat-dev` before starting. For bigger changes, work on your own branch and open a pull request.
2. Read the latest note in [sessions/](sessions/), then this file.
3. **Generated files:** the v4 schematic comes from `tools/generate_v4_schematic.py` and the pre-routing board from `tools/build_v4_pcb.py`. Once someone edits the schematic or routes the board by hand in KiCad, stop rerunning those generators, because they overwrite the files.
4. After changing anything, rerun the matching check (`tools/verify_v4_schematic.py`, `tools/check_v4_pcb.py`, or the firmware compile) and update this checklist and CURRENT_STATUS.md.
