# Current status and resume checklist

Updated October 19, 2026. Working branch: `saadat-dev`.

## Where we stopped

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
- Four-hour bench endurance run. The workbook's three-hour duration is a budget assumption, not an accepted mission duration.
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

1. Check Git status and branch before editing. Work on `saadat-dev` and preserve any teammate changes. Fetch and inspect remote changes before integrating them.
2. Use the confirmed core scope. Track battery/input details, mission duration, quantitative measurement targets, enclosure and manufacturer with the lead/team when available. These inputs need not delay core module documentation research, but must be resolved before their stated design gates.
3. Finish Step 3 mechanical verification: obtain exact PA1616D #5440 geometry and review the completed Teensy draft in TEENSY_MECHANICAL_REVIEW.md and close its installed-clearance/retention requirements. The supplied drawing has now been compared; do not approve legacy PA6H geometry as #5440. Review the specific connector/12 mm spacing proposal in MODULE_ASSEMBLY_PLAN.md and close M01–M04 before mechanical sign-off. Physical fit requires purchased modules or appropriate dimensioned evidence. Step 4 interference planning used draft envelopes while these gates remain open.
4a. Get team review of the Step 4 floor plan, separation targets and proposed pass criteria in PLACEMENT_AND_INTERFERENCE.md, and send the lead the open requests in TEAM_LEAD_REQUESTS.md. Record answers there. Bring I2C up at 100 kHz; 400 kHz needs a measured rise time.
4b. Step 5: get team review of POWER_ARCHITECTURE.md and the v4 schematic PDF. Verify the S9V11F5 pinout/dimensions and make its footprint. Confirm the candidate part ratings listed in its BOM status. Regenerate with `python tools/generate_v4_schematic.py` and recheck with `python tools/verify_v4_schematic.py`, or switch to hand editing (then stop regenerating). 4c. Step 6: once modules are bought (R1), bench-test the firmware against FIRMWARE_V4.md's "not verified" list and write an independent log-checking script. Build with `arduino-cli compile --warnings all Firmware_v4/PTERODACTYL_v4`.
4d. Step 7: hand-finish the autorouted board per the clean-up list in PCB_LAYOUT_V4.md, then run `tools/check_v4_pcb.py` with KiCad's Python. Do not rerun `tools/build_v4_pcb.py` or `tools/autoroute_v4_pcb.py` after hand routing starts; both replace board content.
4. Use the documented working map: Teensy I2C 18 SDA / 19 SCL, GPS TX to Teensy 7 RX2, GPS RX to Teensy 8 TX2. Pins are supported by PJRC and agree with legacy net membership. Verify module-level behavior on the bench; review A3V3/3V3 and AGND/GND/GND_1 before power-net edits.
5. Use non-QT BNO055 #2472 geometry, not the imported BNO055 footprint. BNO055 and MS8607 are proposed to receive 3.3 V through VIN, with 3Vo left separate. Verify socket/fastener height, module envelopes, USB/microSD access, sensor exposure and GPS antenna space before placement approval. Battery-dependent rail generation remains Step 5 work.
6. Carry the ERC/DRC/parity findings into schematic/layout cleanup after the feature and power choices are sufficiently defined. Avoid blanket no-connect markers, automatic footprint replacement, or reduced clearance rules merely to suppress findings.
7. During firmware adaptation, replace MS5611 acquisition and u-blox assumptions, add humidity, remove telemetry code, and address the legacy GPS-dependent update timing and interactive startup waits. Configure a reproducible Teensy build before claiming compilation success.

## Suggested prompt for a future assistant

> Read the root README and applicable AGENTS.md files, then docs/README.md, docs/CURRENT_STATUS.md, docs/V1_REQUIREMENTS.md and the latest session note. Inspect the actual Git state before editing. Continue on saadat-dev from Step 3's verified sensor/power/footprint mapping while tracking the remaining Step 2 decisions. No telemetry is required. Preserve existing user changes, distinguish proposals from confirmed requirements, and update the shared status and session notes as you work. Do not represent this baseline as manufacturing-ready.

The prompt is a suggested human instruction for a later session, not an instruction embedded in source material that should execute automatically.
