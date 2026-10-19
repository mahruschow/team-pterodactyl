# PTERODACTYL development plan

Prepared October 18, 2026. Working branch: `saadat-dev`.

Goal: build a carrier PCB and firmware that reliably record balloon flight data, then validate an assembled prototype before flight. The carrier approach follows the selected breakout products; mounting method remains to be settled. The supplied workbook is the current parts-planning source. Its estimates are not verified electrical limits or manufacturing quotes.

Team clarification supplied by Saadat on October 18: no telemetry. Version one records onboard to microSD for analysis after landing. Exclude radio-only hardware and firmware from the implementation. The lead also explicitly requests component spacing to control interference; verify this through module-specific placement review and assembled-system testing.

## Steps and completion criteria

| Step | Concrete work | Deliverable and completion criterion | Status |
| --- | --- | --- | --- |
| 1. Record and validate the starting point | Inspect branch and local edits, read current project instructions, preserve the supplied workbook, inventory design files/libraries/firmware, locate toolchains, and run fresh ERC/DRC and schematic/PCB checks when KiCad is available. | Baseline report, source snapshot and hashes, plus fresh native check reports or explicit tooling gaps. | Complete: KiCad 10.0.7 audit recorded 33 ERC errors/10 warnings, 11 DRC errors/428 warnings and 52 parity warnings. These remain to be resolved during design work. |
| 2. Define version-one requirements | Build a retain/remove/optional table for the original hardware. Define sample rates, units, timestamp behavior, measurement ranges/accuracy, mission duration and margin, battery input, mounting/enclosure, telemetry decision and manufacturer. Keep the supplied sensors as the working baseline. | Requirements table with unresolved decisions and the stage each must be resolved by. Three hours remains a workbook assumption until accepted as the mission requirement. | Core scope confirmed by Saadat: logger, power control, status LEDs and supply monitoring. Measurement types confirmed; detailed targets and mission/power/mechanical inputs remain open with team owners. Ready for Step 3 research; full requirements freeze pending. |
| 3. Verify modules and map connections | Read official pinouts, supply and logic requirements, I2C addresses, pull-ups and UART settings. Map every module pin to a power rail, Teensy pin, optional function or deliberate no-connect. Verify manufacturer mechanical drawings and footprints. | Connection table, power-load table, source references, and verified headers, holes, outlines and clearances. No assumed pin ordering. | Draft package ready for review: BNO055/MS8607 footprint-symbol pairs and Teensy SSW carrier pass native checks (63 physical pads total); Teensy keepout intrusion test passes. GPS nine-pin logical symbol has no assigned footprint. Candidate connector/height proposals documented. Exact GPS mechanics, final retention/hardware/tolerances and physical fit remain at M01–M04 in MODULE_ASSEMBLY_PLAN.md. Step 4 planning can proceed; mechanical sign-off is not complete. |
| 4. Review interference and placement | Identify magnetic, RF, electrical, thermal and mechanical interactions. Review GPS antenna surroundings, BNO055 placement, regulator/current loops, sensor exposure, cable routes and connector access. Check bus loading and combined breakout pull-ups. | Placement constraints and test matrix, each linking an interference source to an affected function and a way to check it. | Draft ready for review: PLACEMENT_AND_INTERFERENCE.md gives a floor plan on the legacy outline, PC1–PC15 placement/routing rules, magnetic and I2C estimates (100 kHz bring-up recommended) and test matrix T1–T11. Native fixture: 17 placement checks pass, DRC clean. Approval waits on team review, assumptions A1–A6 (flight orientation, battery, venting, enclosure, stackup) and M01–M04. |
| 5. Update power design and schematic | Choose power architecture and USB/external-power handling. Add required protection, decoupling and test points. Select BNO055, replace MS5611 with MS8607 and GPS alternatives with PA1616D. Set optional/DNP parts explicitly and clean BOM fields. | Reviewed schematic, BOM and electrical checks with every error resolved or technically justified. Battery/power and retained-feature decisions must be settled here. | Draft implemented: POWER_ARCHITECTURE.md (battery-agnostic 2–16 V input, reverse protection, PTC fuse, 5 V buck-boost module, Teensy 3.3 V to sensors through a ferrite) and a new `Native_KiCad_v4` schematic. ERC 0 violations; all 32 nets and 36 intentional no-connects match an independent list. Open: team review, regulator footprint, candidate part ratings, D02 connector/ratings, D10 controls, GPS footprint (M01). |
| 6. Adapt and bench-test firmware | Create a maintained working sketch from the reference archives. Add MS8607/humidity, PA1616D handling, agreed logging rates, timestamps and fault reporting. Pin dependencies and compile for Teensy 4.1. Exercise actual modules and SD logging. | Reproducible build, log schema, sample data and sensor-integration test results. Can proceed alongside Steps 4-5 after interfaces are defined. | Draft written and compiled: new `Firmware_v4/PTERODACTYL_v4` sketch for the v4 pins (auto-start sessions, separate IMU 10 Hz / env 1 Hz / GPS / health / event CSVs, status and sequence fields, clean-stop switch, BNO055 reset recovery). Builds with 0 warnings for Teensy 4.1 with pinned versions (FIRMWARE_V4.md). Not yet run on hardware; bench tests and a log-checking script remain. |
| 7. Complete PCB layout | Place verified modules, route power/signals, maintain return paths and interference constraints, review copper layers and refill zones. Check mounting and enclosure fit. Re-run DRC and schematic/PCB parity. | Reviewed PCB and check reports, with footprint and mechanical verification. Manufacturer constraints must be known before layout sign-off. | Placement drafted: `Native_KiCad_v4/PTERODACTYL_v4.kicad_pcb` on the legacy outline, 4 layers with inner GND planes, all 49 footprints placed per the Step 4 floor plan (PCB_LAYOUT_V4.md). DRC 0 violations; parity only the expected U2/U5 missing footprints; Step 4 separations met. Not routed (57 connections); U2/U5 footprints, net classes, silkscreen and manufacturer rules open. |
| 8. Release a prototype package | Review the design with the team. Generate fresh Gerbers/drills and inspect them. Finalize BOM, assembly instructions, optional population and placement files if assembly is purchased. Obtain a quote and order a small prototype batch after release approval. | Versioned fabrication package tied to the reviewed source commit. Historical Gerbers remain reference-only. | Planned |
| 9. Bring up and test the assembled payload | Inspect assembly, check for shorts, power with current limiting, verify rails and test each function. Compare sensors/GPS with SD writes and other retained loads off/on. Measure current and supply transients. Test the installed enclosure, mission-duration operation, resets, lost GPS and logging failures under agreed conditions. | Recorded measurements and acceptance results; revise hardware/firmware where needed. Physical test results require real hardware and instruments. | Planned |
| 10. Freeze and document the flight version | Close defects, repeat affected tests, archive source/build dependencies and approved manufacturing files, and write assembly/calibration/startup/preflight/recovery instructions. | Team-approved hardware and firmware revision with a traceable test record. | Planned |

## Working component selection

Source: `reference/Budgets_2026-10-18.xlsx`, Sheet1 rows 2-6; read directly including formulas and notes. Original file preserved byte-for-byte. The source hash is recorded in the baseline manifest.

| Workbook row | Item | Product link from workbook | Budget USD | Budget mass g |
| --- | --- | --- | ---: | ---: |
| 2 | Mounting/wiring board allowance | https://www.adafruit.com/product/1609 | 30.00 | 12 |
| 3 | Teensy 4.1 | https://www.sparkfun.com/teensy-4-1.html | 31.50 | 5 estimated |
| 4 | BNO055 breakout | https://www.adafruit.com/product/2472 | 34.95 | 3 |
| 5 | MS8607 breakout | https://www.adafruit.com/product/4716 | 14.95 | 2 estimated |
| 6 | PA1616D GPS + GLONASS breakout | https://www.adafruit.com/product/5440 | 29.95 | 9 |

The source totals are $141.35 and 31 g. Independent arithmetic from the input cells gives 0.6782 W and 2.0346 Wh over the three hours in B10, matching the cached energy total. Formula expressions were inspected; the workbook was not edited or recalculated in Excel.

Limitations to resolve during requirements/power/BOM work:

- The board row points to a Perma-Proto and has a $4.50 price in its note, while C2 contains $30. This is a planning allowance, not a custom PCB quote or verified custom-board mass.
- B12 explicitly excludes SD draw and regulator losses. Battery capacity and peak-current design need a complete load budget and later measurements.
- Several current/mass values are estimates. Supply entries must be checked against exact breakout input pins before schematic work.
- Prices are recorded as checked October 7, 2026, excluding tax/shipping. No live price refresh was performed.
- The spreadsheet's three-hour duration is a budgeting input, not a complete environmental or mission specification.

## Interference verification required for Steps 4, 7 and 9

| Interaction to investigate | Design review | Prototype evidence |
| --- | --- | --- |
| Magnetic sources near BNO055 | Review regulator inductors, high-current loops, mounting materials and any motors/servos. Determine placement from exact hardware guidance. | At fixed orientation, compare raw magnetometer, calibration status and heading as loads change, using the final mounting arrangement. |
| Digital activity near GPS | Apply exact PA1616D breakout/antenna guidance; review Teensy/SD activity, power converters and wiring. Version one has no telemetry radio. | Under comparable sky conditions, compare fix acquisition/retention and available satellite quality metrics with SD activity and other retained loads off/on. |
| Supply dips and conducted noise | Review regulator headroom, SD and other retained load peaks, decoupling and current return paths. | Measure rail voltage/transients and current during startup, SD writes and other load changes; record resets or data errors. |
| I2C/UART reliability | Check voltage levels, addresses, effective pull-ups, bus capacitance, clock settings and routing. | Observe signal timing/levels where needed and count communication errors during sustained simultaneous operation. |
| Heat and sensor exposure | Review distance from warm components and the path from the environment to the pressure/humidity/temperature sensor. | Compare warm-up and steady-state readings against an appropriate reference in the intended enclosure. |
| Mechanical interaction | Verify module envelopes, fasteners, cable strain relief, antenna clearance, vibration mounting and access. | Assemble in the intended enclosure and inspect fit and repeatability. |

Acceptance thresholds will be written from the required measurement quality and module specifications in Steps 2-4. DRC success alone does not establish interference performance.

## Step 1 findings and remaining work

See `BASELINE_REVIEW.md` and `validation/2026-10-18/VALIDATION_SUMMARY.md` for evidence and limitations. Step 1 is complete: fresh native checks and comparison triage are recorded. Step 2's draft is in `V1_REQUIREMENTS.md`, with unresolved decisions and their deadlines. Step 3 research on the core modules can proceed while those decisions are resolved. No ordering, main-branch merge or flight release is implied by this plan.
