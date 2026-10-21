# Current status and resume checklist

## Team-name silkscreen update — October 21, 2026

Saadat Muyeen, Mahrus Chowdhury and Ryeed Zaman are now on the back silkscreen, with 2 mm text and 0.30 mm strokes. Fresh DRC, connectivity and schematic-parity checks report zero issues. All original PCB bytes are retained; only three text objects were added. The other eight Gerber layers match the prior geometry exactly, apart from export timestamps. Existing ERC evidence remains applicable to the unchanged schematic.

**Order the updated native PCB or fabrication ZIP. AISLER TCVOYNZG revision 1 is superseded and does not contain the names.** Two revision-upload attempts failed; the alternate upload form says an anonymous project is already in progress and requires login to save it. Sign in and upload the updated board, then inspect the bottom preview before ordering. No new AISLER revision or order has been created. Earlier statements below about revision 1 being the exact current PCB or ready for checkout refer to the previous checkpoint.

## First prototype scope and order checkpoint - October 21, 2026

**Current authority: [FIRST_PROTOTYPE_RELEASE.md](FIRST_PROTOTYPE_RELEASE.md).** PCB checks and AISLER upload/preview passed; project TCVOYNZG revision 1 is ready for checkout. FB1/SW1/SW2/J3 are selected for P1. The user explicitly excludes physical testing, flight qualification, subsequent redesign and casing from this phase; older statements requiring those before PCB fabrication are superseded. Assembly receipt/polarity checks remain part of building the prototype. No order placed. Updated known cost is USD 129.37 (15 price lines missing); entered mass 170.25 g (three missing). The provisional EUR board quote is separate.

**Current implementation — October 21:** Targeted component/connector/capacitor edits and the budget update are now applied. Fresh ERC/DRC/connectivity/parity and preservation checks pass. Read [RESUME_HERE.md](RESUME_HERE.md), then [COMPONENT_IMPLEMENTATION.md](COMPONENT_IMPLEMENTATION.md) for the authoritative boundary. Four BOM references remain explicit candidates; holder/harness fit, cold runtime and flight qualification remain open. Earlier dated figures and research-only statements below are historical where superseded.

## Latest component checkpoint

Native v4 targeted edits are complete for the reviewed parts. 51 footprints / 246 segments / 25 vias retained; eight segments have bounded endpoint edits, four small nonmodule footprint moves, no changed pad nets. Fresh checks: 0 ERC, 0 enabled DRC, 0 unconnected, 0 parity; 32 nets and 35 no-connects verified. BOM: 47 individual reference rows, zero blank MPNs, four candidates (SW1, SW2, J3, FB1). Evidence is in `validation/2026-10-21/component-finalization/`.

L91 x4 with BH4AAW is the prototype pack candidate; Kingston SDCIT2/8GB is in the budget. Updated model: 1.618 W average, 3.568 W peak, 8.669 Wh provisional nameplate target for 3 h. Entered mass 170.25 g with three missing mass lines; known price $118.30 with 16 unpriced lines. Detailed path-loss screening flags startup risk at a 4 V loaded pack. No physical validation or purchasing occurred.

The following entries preserve prior checkpoints and are superseded by COMPONENT_IMPLEMENTATION.md where they conflict.

Updated October 21, 2026. Working branch: `saadat-dev`.

## Where we stopped

**Finalization started:** exported the current schematic BOM to `validation/2026-10-20/finalization-bom.csv`: 47 rows, zero missing footprints, 35 blank MPN fields and seven candidate MPN fields (not unique-product counts). Follow the finalization order in REMAINING_WORK.md: battery/SD and power ratings, exact passive/header fit, assembled geometry/casing, manufacturer/quotes, then final review and fabrication outputs. Generic 10 uF capacitor footprints need real part matching; Q1 remains SOT-23 despite through-hole sensor assembly. No board geometry changed in this checkpoint.

**Latest requirements/assembly:** three-hour runtime and **-40 C minimum battery temperature** are recorded from Saadat/the lead. Sensors use **through-hole soldered headers**, superseding removable sensor sockets; verify pin/drill fit, solder tails, underside clearance and retention before release. Custom casing CAD follows the completed PCB layout, with mounting/access envelopes reserved now. No PCB geometry was changed. The live budget withdrew the old 10.5 g interconnect allowance: current entered mass is **97.2 g with four missing mass lines**; the earlier 107.7 g subtotal below is historical. See MODULE_ASSEMBLY_PLAN.md and POWER_COST_MASS_BUDGET.md.

**Latest budget:** [POWER_COST_MASS_BUDGET.md](POWER_COST_MASS_BUDGET.md). The lead asks us to calculate power/cost/mass and choose the battery; nothing is ordered and the package should be as small as functional. A checked live workbook now models 1.495 W average battery input, 3.284 W peak allowance, and 8.01 Wh nameplate energy for the three-hour total powered runtime confirmed by Saadat on October 20. Temperature remains unconfirmed. Known module cost is $118.30, with 17 other lines unpriced; mass subtotal is 107.7 g of mixed published values/allowances, excluding three missing mass items. Review the 0.7 A PTC against low-voltage peaks before choosing a pack. Twenty-two calculation/guard checks passed. No PCB or firmware edits in the budget task; current work remains uncommitted.

**Latest GPS/layout:** [GPS_CARRIER_INTEGRATION.md](GPS_CARRIER_INTEGRATION.md). Saadat visually accepted the legacy CAD geometry for #5440 and authorized integration. U5 is now assigned, placed and routed: 51 footprints, 246 tracks, 25 vias; zero ERC, enabled DRC, unconnected items or parity issues. All original routing and placements are preserved. Actual socket/holder/retention fit, battery/BOM and fabrication gates remain open. This supersedes earlier missing-U5 statements below.

**Latest firmware:** [SENSOR_READ_VALIDITY.md](SENSOR_READ_VALIDITY.md). Version 4.0.2-draft checks BNO sample/configuration transfers and MS8607 reset/PROM/configuration/measurement transfers plus CRC results. Failed measurements produce empty READ_FAIL rows and unhealthy status; recovery is host-tested. Sixteen fault-test groups pass and the Teensy build passes with zero warnings. GPS freshness remains next; hardware validation is open.

**Previous firmware checkpoint:** [FIRMWARE_RELIABILITY.md](FIRMWARE_RELIABILITY.md). Version 4.0.1-draft requires all SD session files, detects write/sync/close failures, retries in a fresh folder, bounds BNO post-reset polling and adds a retry cooldown. Teensy build and ten host fault-injection groups pass. Sensor-transfer/CRC validity and GPS RMC freshness remain open; no hardware testing. See the [October 20 session](sessions/2026-10-20.md).

**Meeting handoff:** [October 20 teammate meeting](TEAM_MEETING_2026-10-20.md) organizes completed work, outstanding tasks, team inputs, proposed owners and a decision log.

**Latest layout cleanup:** [LAYOUT_REVIEW_CLEANUP.md](LAYOUT_REVIEW_CLEANUP.md). C2 is now 4.493 mm from the carrier ADC pin; I2C follows Teensy → MS8607 → BNO055 (135.163/128.209 mm). Added three return-path stitching vias and readable silkscreen. Fresh enabled physical DRC and present-footprint unconnected counts are both 0; U5 remains missing. See the review for unchanged geometry, test evidence and remaining power-integrity/mechanical/manufacturer gates.

**Latest routing checkpoint:** [POWER_ROUTING.md](POWER_ROUTING.md). All connections among the 50 placed footprints are now routed: 0 enabled physical DRC violations, 0 unconnected items, and only U5/GPS missing in schematic parity. U5 is still absent, so this does not mean all schematic connections are implemented. TP1/TP2/TP4 were moved near their rails; a 68.667 mm unloaded TP1 spur was removed. No new vias; original signal routes and design rules are preserved. GPS geometry, layout/assembly review and fabrication gates remain open.

The entries below are historical checkpoints; the latest GPS/layout and budget entries above take precedence.

**Latest footprint work:** [REGULATOR_GPS_FOOTPRINTS.md](REGULATOR_GPS_FOOTPRINTS.md). U2 now has a source-checked three-pin carrier footprint assigned and placed; the unverified GPS comparison footprint exists separately and U5 remains unassigned. ERC and enabled physical DRC: 0 violations; parity: only U5; 12 unconnected items including the newly exposed regulator connections. All existing routing and the other 49 footprints are preserved. The placement checker now measures actual PCB geometry and detects a deliberate moved-IMU violation. Connector fit/retention, GPS M01 and remaining routing still need closure. Earlier review/implementation entries below describe their historical checkpoints.

**Latest review (October 19, source commit `8933189`):** [V4_DESIGN_REVIEW.md](V4_DESIGN_REVIEW.md). Fresh ERC and enabled physical DRC checks report zero violations, but the board has 10 unconnected items and missing U2/U5 footprints. Actual separation targets pass and the firmware compiles. Newly identified work: propagate sensor read failures, bound BNO055 reset waits, recover incomplete SD sessions, validate GPS field freshness, document the regulator's 3 V startup minimum, and measure current PCB geometry in the placement checker. These findings are unresolved; Steps 2–7 remain drafts. This review publication changes documentation and evidence only.

**Step 1 is complete. Step 2 core scope is confirmed. Step 3 has a documented connection map and three checked draft carrier footprints (BNO055, MS8607 and Teensy), matching sensor symbols, a GPS logical symbol and concrete assembly proposals; mechanical approval remains incomplete.**

**Step 4 (October 19) has a draft placement and interference plan ready for team review:** [PLACEMENT_AND_INTERFERENCE.md](PLACEMENT_AND_INTERFERENCE.md). It sets out a floor plan on the legacy 97.79 mm outline (BNO055 top-left, MS8607 top-centre, GPS envelope top-right, Teensy bottom-left with microSD at the board edge, power region bottom-right), placement/routing rules PC1–PC15, magnetic-field and I2C bus estimates, and prototype test matrix T1–T11. An isolated native fixture passes 17 placement checks with zero DRC violations. Approval waits on team review, assumptions A1–A6 and M01–M04. Inputs needed from the lead, for both Step 3 and Step 4, are collected in [TEAM_LEAD_REQUESTS.md](TEAM_LEAD_REQUESTS.md) (R1–R9).

**Step 5 (October 19) has a draft v4 schematic:** `Native_KiCad_v4/PTERODACTYL_v4.kicad_pro`, documented in [POWER_ARCHITECTURE.md](POWER_ARCHITECTURE.md). Saadat chose a battery-agnostic 5 V buck-boost module (Pololu S9V11F5, 2–16 V in), dropping the legacy expansion headers, and a new clean schematic. The design:
- Adds a PTC fuse, P-MOSFET reverse protection, an off-board panel switch, battery-voltage sensing on pin 26 and sensor power from the Teensy 3.3 V through a ferrite.
- Adds LED series resistors, which the legacy design lacked, and the BNO055 reset on pin 9.
- Adds test points.

ERC reports 0 violations, and the exported netlist matches an independently written expected list (32 nets, 36 intentional no-connects). The regulator and GPS have no footprints yet. Candidate part ratings and the team review are open. The imported v3.8 project is unchanged.

**Step 6 (October 19) has draft v4 firmware:** `Firmware_v4/PTERODACTYL_v4`, documented in [FIRMWARE_V4.md](FIRMWARE_V4.md). It is a new sketch rather than a port of v19.1, written for the v4 pins and the LOG-01 to LOG-07 proposals. It starts automatically, writes numbered session folders with separate IMU/env/GPS/health/event CSV files, and records status and sequence numbers. It also handles a clean-stop switch and BNO055 reset recovery. It compiles with 0 warnings for Teensy 4.1 (teensy:avr 1.62.0, pinned library versions in `sketch.yaml`). It has not run on hardware.

**Step 7 (October 19) has a placed, unrouted draft v4 PCB:** `Native_KiCad_v4/PTERODACTYL_v4.kicad_pcb`, documented in [PCB_LAYOUT_V4.md](PCB_LAYOUT_V4.md), with a top-view render. It uses the legacy outline and holes, has 4 layers with In1/In2 GND planes, and places all 49 footprints per the Step 4 floor plan. The GPS and regulator appear as keep-out envelopes. DRC reports 0 violations, parity shows only the two expected missing footprints, and the Step 4 separations are re-measured and met. Routing is the next task.

**Routing attempt (October 19):** a Power net class (0.5 mm tracks for the battery/supply nets) was added. The GPS and regulator envelopes now also keep out tracks and vias. A Freerouting 2.5.0 autoroute was then tried: its Windows CLI build crashed on start-up with a packaging error, and the board was not changed. The portable `.jar` needs Java 25 (Java 17 is installed). `tools/autoroute_v4_pcb.py` now detects such crashes and disables Freerouting's analytics. **First-pass autoroute done (October 19)** with the portable Freerouting 2.5.0 `.jar` on a Java 25 runtime (SHA-256 verified; neither is installed or committed):
- DRC has 0 violations, parity shows only U2/U5, and the separations are met.
- 192 track segments sit on the outer layers only, with 10 vias. I2C is 110.5 mm.
- 6 supply connections are open (SENSOR_3V3 and +5V).

Hand clean-up is next; see PCB_LAYOUT_V4.md. **See [REMAINING_WORK.md](REMAINING_WORK.md) for the full to-do list by owner.**

See [SENSOR_CONNECTION_MAP.md](SENSOR_CONNECTION_MAP.md) for the working interfaces and [FOOTPRINT_REVIEW.md](FOOTPRINT_REVIEW.md) for the new BNO055 #2472 and MS8607 #4716 carrier footprints. The project-local `Pterodactyl_Modules` symbol and footprint libraries are registered, but no footprint has been assigned to the main schematic/PCB. Source-coordinate checks passed for all 15 electrical pads and eight mounting centers; an isolated fixture DRC found zero violations. All 15 symbol pins also passed the pin/function/type/default-footprint contract check. The refreshed fixture still has zero DRC violations after changing sensor socket drills to 1.04 mm. The new GPS logical symbol has nine checked named pins and intentionally no assigned footprint; it does not establish physical pad order. These checks do not prove physical fit or circuit correctness.

Exact GPS #5440 geometry remains unverified: the published board file still names PA6H and its last file-specific change was in 2017. Saadat supplied the PJRC dimension PNG locally. The Teensy nominal outline and all 48 side-header positions match; the drawing-access dependency is closed. The [mechanical review](TEENSY_MECHANICAL_REVIEW.md) records a new `Teensy41_SSW_Carrier` draft that replaces the imported mixed drills with 1.04 mm SSW socket holes, adds F.Fab/courtyard geometry and an enforced front-side component keepout. All 48 pad identities/positions pass; clear fixtures pass DRC and an intentional intrusion is rejected. Installed access and retention still need verification. Parts have not been purchased; continue to use the exact spreadsheet products. The [assembly proposal](MODULE_ASSEMBLY_PLAN.md) selects candidate SSW/HTSW headers and a nominal 12 mm sensor-module spacing; final hardware/tolerances and physical fit remain open at gates M01–M04.

Saadat selected the core logger with power control, status LEDs and supply monitoring on October 18. Measurement types were reaffirmed. Battery and flight/runtime details are unknown to him; he is primarily designing the PCB. Keep these inputs assigned to the lead/team rather than repeatedly requesting the measurement list. The requirements review and D01-D10 register record the remaining dependencies.

The main schematic and PCB remain the imported v3.8 v11 baseline. New local symbol/footprint assets and registration were added alongside documentation, generators and check evidence. Main schematic/PCB, imported libraries and firmware remain unchanged. New modules are not yet incorporated into the circuit.

## Established direction

- Retain Teensy 4.1 with built-in microSD logging.
- Include power control, status LEDs and supply monitoring. Exclude OLED, remote temperature probes, alternative IMU, heater and servo functions from the selected core scope; exact power/stop controls and pull-before-flight role remain open.
- Use the supplied parts list as the working selection: Adafruit BNO055 2472, MS8607 4716 and PA1616D GPS 5440.
- **No telemetry.** The lead's reply, supplied by Saadat, calls for recording onboard and analyzing after recovery. Plan to remove XBee/radio-only hardware and transmit/receive/relay code during implementation. GPS reception remains required.
- Explicitly review spacing and interference, including magnetic effects, GPS placement, power/ground noise, thermal effects and final-enclosure fit. Validate simultaneous operation on the prototype.
- Use a breakout carrier as the working architecture. Verify exact purchased board revisions and mounting before treating footprints as approved.

## Proposals that are not final requirements

- 10 Hz motion/orientation/magnetic logging, 1 Hz environment/GPS/health logging.
- Automatic standalone startup, independent sampling schedules, structured logs and explicit invalid/stale status.
- Four-hour bench endurance run. Three hours of total powered runtime was confirmed by Saadat on October 20; the four-hour bench test remains a proposal.
- Exact power architecture, indicator behavior, supply-monitoring circuit and launch/stop workflow remain to be designed.

See [V1_REQUIREMENTS.md](V1_REQUIREMENTS.md) for acceptance proposals and D01-D10 decisions. D01 (core feature package) and D05 (no telemetry) are resolved. D03 has confirmed measurement types but open performance targets; D10 has excluded heater/actuators but open control workflow. Feature selection is not approval of a specific circuit or proof of flight suitability.

## Known validation results

KiCad 10.0.7 ran on a temporary copy of the complete project, with zone refill in memory and no saved source changes:

| Check | Result |
| --- | --- |
| Schematic ERC | 33 errors, 10 warnings |
| PCB physical DRC | 11 clearance errors, 428 warnings |
| PCB unconnected items | 0 |
| Schematic/PCB parity | 52 additional warnings |

The physical DRC reproduced the October 7 categories/counts. Parity triage found net naming/unused-pin representations, component fields/values and board-only mounting/graphics. A separate comparison found matching schematic pad membership for all 50 assigned PCB nets, allowing three name differences. That is limited consistency evidence, not verification of actual module pinouts or design intent. Ignored checks and exact findings are documented in the [validation summary](validation/2026-10-18/VALIDATION_SUMMARY.md).

## Tools and source files

- Open `Native_KiCad_v11/PTERODACTYL_v3.8_v11.kicad_pro` in KiCad 10. On Saadat's machine the CLI is `C:\Program Files\KiCad\10.0\bin\kicad-cli.exe`; other computers may use another location.
- Project symbol and footprint tables use `${KIPRJMOD}`. Keep these libraries with the project.
- Arduino IDE 2.3.2 and its CLI 0.35.3 are on Saadat's machine. On October 19 the Teensy platform 1.62.0 and the Adafruit libraries were installed, and the v4 firmware was built (see FIRMWARE_V4.md). The legacy v19.1 firmware has not been built.
- Firmware remains in the two ZIP archives under Firmware_reference. The v19.1 main sketch is nested at `PTERODACTYL_v19_1/PTERODACTYL_v19_1/examples/PTERODACTYL_v3_8_19_1/`; ignore `__MACOSX` resource entries when extracting.
- The supplied workbook is preserved in [reference/Budgets_2026-10-18.xlsx](reference/Budgets_2026-10-18.xlsx), with its hash in the manifest. Download-folder paths in older evidence are provenance, not required inputs for resuming.

## Next concrete actions

1. Check Git state and read FIRMWARE_RELIABILITY.md for current firmware work (next: GPS RMC/GGA freshness; see SENSOR_READ_VALIDITY.md for completed transfer/CRC work). For PCB work, read LAYOUT_REVIEW_CLEANUP.md and POWER_ROUTING.md before editing. The footprint checkpoint was published as `d40fba3`; the following routing change is recorded in the latest session entry. The active design is `Native_KiCad_v4/PTERODACTYL_v4.kicad_pro`.
2. GPS is now assigned and routed. Close actual module/socket/holder fit and retention using GPS_CARRIER_INTEGRATION.md and the assembly gates; earlier missing-U5 statements are historical.
3. Review LAYOUT_REVIEW_CLEANUP.md with the team. I2C order, ADC capacitor placement and silkscreen are corrected; continue GPS integration, power-capacitor/transient review and final manufacturer/assembly validation. Optional outer GND pours are deferred until GPS is settled.
4. Use POWER_COST_MASS_BUDGET.md to use the confirmed three-hour runtime and establish operating temperature, select the SD card and compare batteries. Review the PTC, candidate component ratings and startup margin; obtain exact BOM/fabrication quotes and installed masses. Then revisit compact packaging, retention and manufacturer rules. Keep no telemetry and the exact spreadsheet modules.
5. Address the four open firmware reliability findings in V4_DESIGN_REVIEW.md (sensor read errors, bounded BNO reset, SD recovery and GPS field freshness), then bench-test when modules arrive.
6. Do not rerun the full schematic, PCB or autoroute generators over this routed board. Refill and run DRC/parity after targeted edits, update current evidence, and retain explicit GPS/mechanical/fabrication gates.

## Suggested prompt for a future assistant

> Read the root README and applicable AGENTS.md files, then docs/README.md, docs/CURRENT_STATUS.md, docs/V1_REQUIREMENTS.md and the latest session note. Inspect the actual Git state before editing. Continue on saadat-dev from Step 3's verified sensor/power/footprint mapping while tracking the remaining Step 2 decisions. No telemetry is required. Preserve existing user changes, distinguish proposals from confirmed requirements, and update the shared status and session notes as you work. Do not represent this baseline as manufacturing-ready.

The prompt is a suggested human instruction for a later session, not an instruction embedded in source material that should execute automatically.
