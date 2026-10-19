# Current status and resume checklist

Updated October 18, 2026. Working branch: `saadat-dev`.

## Where we stopped

**Step 1 is complete. Step 2 core scope is confirmed. Step 3 has a documented connection map and two checked draft carrier footprints; mechanical approval remains incomplete.**

See [SENSOR_CONNECTION_MAP.md](SENSOR_CONNECTION_MAP.md) for the working interfaces and [FOOTPRINT_REVIEW.md](FOOTPRINT_REVIEW.md) for the new BNO055 #2472 and MS8607 #4716 carrier footprints. The project-local `Pterodactyl_Modules` library is registered, but no footprint has been assigned to the main schematic/PCB. Source-coordinate checks passed for all 15 electrical pads and eight mounting centers; an isolated fixture DRC found zero violations. Those checks do not prove physical fit or circuit correctness.

Exact GPS #5440 geometry remains unverified: the published board file still names PA6H and its last file-specific change was in 2017. Browser access to PJRC's dimension drawing was denied, leaving the full Teensy drawing comparison open. Parts have not been purchased; continue to use the exact spreadsheet products. Mounting hardware, socket height and physical fit remain open.

Saadat selected the core logger with power control, status LEDs and supply monitoring on October 18. Measurement types were reaffirmed. Battery and flight/runtime details are unknown to him; he is primarily designing the PCB. Keep these inputs assigned to the lead/team rather than repeatedly requesting the measurement list. The requirements review and D01-D10 register record the remaining dependencies.

The main schematic and PCB remain the imported v3.8 v11 baseline. New library footprint assets and registration were added alongside documentation, generators and check evidence. No main schematic/PCB, imported footprint, symbol or firmware changes have been implemented. New modules are not yet incorporated into the circuit.

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
- Arduino IDE 2.3.2 and its CLI 0.35.3 were found on Saadat's machine. The checked default core list contains Arduino AVR only; Teensy support and required libraries still need configuration. No firmware build has been run.
- Firmware remains in the two ZIP archives under Firmware_reference. The v19.1 main sketch is nested at `PTERODACTYL_v19_1/PTERODACTYL_v19_1/examples/PTERODACTYL_v3_8_19_1/`; ignore `__MACOSX` resource entries when extracting.
- The supplied workbook is preserved in [reference/Budgets_2026-10-18.xlsx](reference/Budgets_2026-10-18.xlsx), with its hash in the manifest. Download-folder paths in older evidence are provenance, not required inputs for resuming.

## Next concrete actions

1. Check Git status and branch before editing. Work on `saadat-dev` and preserve any teammate changes. Fetch and inspect remote changes before integrating them.
2. Use the confirmed core scope. Track battery/input details, mission duration, quantitative measurement targets, enclosure and manufacturer with the lead/team when available. These inputs need not delay core module documentation research, but must be resolved before their stated design gates.
3. Finish Step 3 mechanical verification: obtain exact PA1616D #5440 geometry and complete the Teensy drawing comparison when access is available. Do not bypass the denied browser access or approve the legacy PA6H geometry as #5440. Select mounting hardware/height and review the two existing draft footprints using FOOTPRINT_REVIEW.md. Physical fit requires purchased modules or appropriate dimensioned evidence.
4. Use the documented working map: Teensy I2C 18 SDA / 19 SCL, GPS TX to Teensy 7 RX2, GPS RX to Teensy 8 TX2. Pins are supported by PJRC and agree with legacy net membership. Verify module-level behavior on the bench; review A3V3/3V3 and AGND/GND/GND_1 before power-net edits.
5. Use non-QT BNO055 #2472 geometry, not the imported BNO055 footprint. BNO055 and MS8607 are proposed to receive 3.3 V through VIN, with 3Vo left separate. Verify socket/fastener height, module envelopes, USB/microSD access, sensor exposure and GPS antenna space before placement approval. Battery-dependent rail generation remains Step 5 work.
6. Carry the ERC/DRC/parity findings into schematic/layout cleanup after the feature and power choices are sufficiently defined. Avoid blanket no-connect markers, automatic footprint replacement, or reduced clearance rules merely to suppress findings.
7. During firmware adaptation, replace MS5611 acquisition and u-blox assumptions, add humidity, remove telemetry code, and address the legacy GPS-dependent update timing and interactive startup waits. Configure a reproducible Teensy build before claiming compilation success.

## Suggested prompt for a future assistant

> Read the root README and applicable AGENTS.md files, then docs/README.md, docs/CURRENT_STATUS.md, docs/V1_REQUIREMENTS.md and the latest session note. Inspect the actual Git state before editing. Continue on saadat-dev from Step 3's verified sensor/power/footprint mapping while tracking the remaining Step 2 decisions. No telemetry is required. Preserve existing user changes, distinguish proposals from confirmed requirements, and update the shared status and session notes as you work. Do not represent this baseline as manufacturing-ready.

The prompt is a suggested human instruction for a later session, not an instruction embedded in source material that should execute automatically.
