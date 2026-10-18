# Current status and resume checklist

Updated October 18, 2026. Working branch: `saadat-dev`.

## Where we stopped

**Step 1 is complete. Step 2 is drafted with open decisions. Step 3 has not started in detail.**

The editable hardware remains the imported v3.8 v11 baseline. This session changed documentation and added reference/check evidence only. No schematic, PCB, footprint, symbol or firmware design change has been implemented. The newly selected MS8607 and PA1616D are therefore not yet incorporated into the hardware or firmware.

## Established direction

- Retain Teensy 4.1 with built-in microSD logging.
- Use the supplied parts list as the working selection: Adafruit BNO055 2472, MS8607 4716 and PA1616D GPS 5440.
- **No telemetry.** The lead's reply, supplied by Saadat, calls for recording onboard and analyzing after recovery. Plan to remove XBee/radio-only hardware and transmit/receive/relay code during implementation. GPS reception remains required.
- Explicitly review spacing and interference, including magnetic effects, GPS placement, power/ground noise, thermal effects and final-enclosure fit. Validate simultaneous operation on the prototype.
- Use a breakout carrier as the working architecture. Verify exact purchased board revisions and mounting before treating footprints as approved.

## Proposals that are not final requirements

- 10 Hz motion/orientation/magnetic logging, 1 Hz environment/GPS/health logging.
- Automatic standalone startup, independent sampling schedules, structured logs and explicit invalid/stale status.
- Four-hour bench endurance run. The workbook's three-hour duration is a budget assumption, not an accepted mission duration.
- Core prototype with power switching, status indicators and supply monitoring; OLED, remote thermistors, servos, heater and launch controls still need scope decisions.

See [V1_REQUIREMENTS.md](V1_REQUIREMENTS.md) for acceptance proposals and D01-D10 decisions. Only D05 (no telemetry) is resolved in that register. Do not treat unanswered questions as approval to remove other optional features.

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
2. Read the requirements decision register. Obtain feature scope, battery/input details, mission duration, measurement expectations, enclosure and manufacturer when available. These inputs need not delay core module documentation research.
3. Start Step 3: create `docs/SENSOR_CONNECTION_MAP.md`. For each module pin, record physical pin/header position, voltage, signal direction, Teensy connection, bus address/settings, pull-up behavior and whether it is intentionally unused. Cite official schematics/datasheets and record the exact board revision.
4. Treat existing Teensy I2C pins 18/19 and GPS Serial2 pins 7 RX/8 TX as **candidates from the old design**, not an approved new pin map. Verify them and GPS TX-to-Teensy-RX wiring before reuse. Review existing A3V3/3V3 and AGND/GND/GND_1 distinctions before changing power nets.
5. Obtain manufacturer mechanical files for all selected breakouts. Verify header spacing, holes, outline, height, connector access and antenna placement. Do not reuse an old footprint merely because it has a matching sensor name.
6. Carry the ERC/DRC/parity findings into schematic/layout cleanup after the feature and power choices are sufficiently defined. Avoid blanket no-connect markers, automatic footprint replacement, or reduced clearance rules merely to suppress findings.
7. During firmware adaptation, replace MS5611 acquisition and u-blox assumptions, add humidity, remove telemetry code, and address the legacy GPS-dependent update timing and interactive startup waits. Configure a reproducible Teensy build before claiming compilation success.

## Suggested prompt for a future assistant

> Read the root README and applicable AGENTS.md files, then docs/README.md, docs/CURRENT_STATUS.md, docs/V1_REQUIREMENTS.md and the latest session note. Inspect the actual Git state before editing. Continue on saadat-dev from Step 3's verified sensor/power/footprint mapping while tracking the remaining Step 2 decisions. No telemetry is required. Preserve existing user changes, distinguish proposals from confirmed requirements, and update the shared status and session notes as you work. Do not represent this baseline as manufacturing-ready.

The prompt is a suggested human instruction for a later session, not an instruction embedded in source material that should execute automatically.
