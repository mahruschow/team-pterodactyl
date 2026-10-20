# PTERODACTYL teammate meeting — October 20, 2026

Updated October 20 from branch `saadat-dev`; PCB design commit `f55657f` (October 19), firmware 4.0.2-draft checkpoint described in [SENSOR_READ_VALIDITY.md](SENSOR_READ_VALIDITY.md). Proposed owners below are suggestions to agree at the meeting, not assigned commitments.

**Opening summary:** We have a new v4 schematic, a routed carrier PCB for the components currently placed, and firmware that compiles. The regulator and sensor/Teensy carrier footprints are implemented. The GPS footprint still needs exact #5440 geometry. We have not built or tested the complete hardware, and the board is not ready to order.

## 1. What is completed

| Area | Completed deliverable | Limit / remaining approval |
| --- | --- | --- |
| Baseline review | Recorded the legacy board, its issues and the official parts workbook. | Old fabrication files are reference only. |
| Core scope | Teensy 4.1, BNO055 #2472, MS8607 #4716, GPS #5440, microSD logging, power control, LEDs and supply monitoring. No telemetry. | Mission duration, ranges, accuracy and rates still need confirmation. |
| Schematic | New v4 design with protection, regulator, sensor power, battery sensing and module connections; latest recorded ERC has zero violations. | Candidate part ratings, battery contract and team review remain. |
| Carrier footprints | BNO055, MS8607, Teensy and Pololu S9V11F5 nominal geometry checked and integrated. | Real connector engagement, module revisions and retention need a dry fit. GPS comparison geometry is explicitly unverified. |
| PCB routing | All connections among the 50 placed footprints are routed. ADC capacitor moved near its input; I2C order corrected; ground stitching and readable silkscreen added. | GPS is absent. Zero unconnected items excludes its missing connections. |
| Digital checks | Latest enabled physical DRC: 0 violations; unconnected items: 0; only missing U5/GPS in schematic parity. I2C order/length, ADC proximity, separation and width checks pass. | These are checks under the current project rules, not a manufacturer's approval or measured interference results. |
| Firmware foundation | New logger compiles; SD recovery, BNO reset timeout/cooldown and sensor transfer/CRC handling pass sixteen host fault-test groups. | GPS freshness remains open; no complete-system hardware tests. |
| Handoff | Shared plans, source evidence, review reports, validation tools and session notes are in `docs/`. | Use the latest checkpoint; older reports describe historical boards. |

The measured quantities in scope are acceleration, gyro/rotation, orientation/magnetic field, GPS position/altitude/time, pressure, sensor temperature, humidity, derived pressure altitude and supply health. **10 Hz IMU, 1 Hz environment/GPS and a four-hour bench test remain proposals.** The workbook's three hours is a budget assumption.

## 2. What is left, in practical order

| Priority | Work | Can start now? | Evidence that closes it |
| --- | --- | --- | --- |
| 1 | Verify current Adafruit GPS #5440 geometry, then assign U5 and route it. | Obtain matching CAD/drawing now, or measure an actual module when available. | Confirmed revision, pin order/coordinates, holes, outline, antenna and underside battery-holder clearance; updated schematic/PCB with clean parity and no unconnected items. |
| 2 | Finalize power and procurement details. | Yes: datasheet/rating review and decision list. | Battery/input limits including startup margin, connector/switch/fuse ratings, capacitor/bead ratings, completed BOM with sockets, headers, spacers and fasteners. |
| 3 | Fix firmware reliability. | Yes, independently of PCB work. | Next: reject stale/mismatched GPS RMC fields and add CSV validation. Sensor-transfer/CRC reporting, SD recovery and BNO timeout/cooldown are implemented and host-tested; hardware verification remains. |
| 4 | Confirm mechanical assembly and enclosure. | Nominal review now; physical fit needs modules/hardware. | M01–M04 records: hole/pin alignment, connector engagement, retention, USB/SD access, antenna view, sensor exposure and mounting orientation. |
| 5 | Final board review and fabrication preparation. | Review now; release waits for GPS, mechanical and manufacturer decisions. | Apply actual manufacturer rules/stackup, review power-capacitor placement/transients, rerun checks and inspect newly generated Gerbers/drills. Independent teammate sign-off. |
| 6 | Assemble and test a prototype. | Prepare the test plan/equipment now; execution needs hardware. | Startup/current/rail tests, sensor and GPS logs, SD faults/recovery, endurance and interference/thermal tests with results recorded. |
| 7 | Decide whether a revision is needed before flight use. | After prototype results. | Required corrections implemented and verified; flight requirements accepted by the team. |

Power/layout items still needing attention include C1/C4 proximity and rail-transient behavior. Optional outer copper pours are deferred until GPS routing is settled; two inner GND planes are already present. No decision to order or fly is implied by a clean DRC.

## 3. What we need from the lead/team

Bring back explicit answers; do not guess them during PCB work.

- **Parts and purchasing:** confirm what is actually on hand, approval/budget to obtain the exact modules, and who will obtain the #5440 drawing or measurements. Latest recorded status is that the sensor boards were not purchased; verify whether that changed.
- **Battery and runtime:** chemistry/cell count, minimum/maximum loaded voltage, capacity, connector, placement and total powered time including prelaunch/recovery. Regulator startup requires at least 3 V at its VIN, plus upstream-loss/sag margin at the battery; the running minimum alone is insufficient.
- **Mission measurements:** required range, accuracy, fastest event/sample rate, temperature/pressure environment and what altitude reference is wanted. Confirm whether the provisional rates meet the actual objective.
- **Enclosure and installation:** internal dimensions, mounting holes/orientation, board/assembly height and weight constraints, GPS antenna view, pressure venting, whether temperature/humidity should describe outside air, USB/SD access and LED visibility.
- **Operation:** power/start/stop workflow, role of the button and pull-before-flight input, acceptable data loss after sudden power removal, and USB/bench-power procedure.
- **Manufacturing:** chosen PCB supplier, stackup/thickness, drill/clearance/silkscreen rules, prototype quantity, assembly owner and budget. Close candidate component and mechanical BOM choices before ordering.

Supplies/equipment to arrange for validation: exact modules and intended headers/sockets/spacers; a suitable microSD card; calipers; current-limited bench supply and multimeter; access to an oscilloscope and, preferably, an I2C/UART logic analyzer; agreed reference instruments for environmental checks. This is an availability checklist, not a purchase order.

## 4. Suggested work split

| Proposed owner | Next deliverable |
| --- | --- |
| Saadat — PCB | Incorporate verified GPS geometry, complete its routing, maintain schematic/PCB consistency, and apply manufacturer rules. |
| Teammate — independent review / firmware | Review power/BOM and module pinouts; take the four firmware fixes or identify a firmware owner; prepare the CSV log checker and fault-test checklist. |
| Lead / team | Decide battery, mission/runtime, enclosure, controls, supplier and purchasing. |
| Both | Review final design together, dry-fit modules, assemble/test the prototype, and record evidence/sign-off. |

If the teammate is also mainly a PCB designer, prioritize an independent schematic/BOM review and assign firmware explicitly instead of assuming someone will cover it. Avoid both people editing the same PCB simultaneously; agree one PCB editor per change and a review handoff.

## 5. Suggested 40-minute meeting

1. **5 minutes:** agree the scope and current status; open the current v4 board.
2. **10 minutes:** examine the GPS gap, power/BOM, enclosure and exact parts available.
3. **10 minutes:** review the four firmware issues and the test plan; assign owners.
4. **10 minutes:** write the consolidated questions for the lead and choose the next milestone.
5. **5 minutes:** record owner, due date and evidence required for each task below.

**Aim to leave with:** an owner for GPS geometry, an owner for firmware reliability, one consolidated lead-question list, and a dated next checkpoint. The next milestone is a complete, independently reviewed design ready for prototype fabrication—not flight qualification.

| Action / decision | Owner agreed | Due date | Answer or evidence link |
| --- | --- | --- | --- |
| Confirm parts on hand / module purchasing | | | |
| Obtain current #5440 geometry | | | |
| Battery, runtime and operating workflow | | | |
| Mission rates/ranges/environment | | | |
| Enclosure and mounting | | | |
| Manufacturer, BOM and budget | | | |
| Firmware fixes and failure tests | | | |
| Independent design review / next checkpoint | | | |

## 6. Files to open together

- Active KiCad project: `Native_KiCad_v4/PTERODACTYL_v4.kicad_pro` on `saadat-dev`.
- [Current copper/silkscreen view](validation/2026-10-19/layout-review/copper.svg) and [latest layout review](LAYOUT_REVIEW_CLEANUP.md).
- [GPS/regulator geometry status](REGULATOR_GPS_FOOTPRINTS.md) and [assembly gates M01–M04](MODULE_ASSEMBLY_PLAN.md).
- [Power architecture](POWER_ARCHITECTURE.md) and the [historical candidate BOM](validation/2026-10-19/step5-schematic/bom.csv); refresh the BOM before procurement.
- [Firmware review findings](V4_DESIGN_REVIEW.md), finding 6 remains open; finding 2 has software fixes in [SENSOR_READ_VALIDITY.md](SENSOR_READ_VALIDITY.md), and findings 3 and 4 have software fixes in [FIRMWARE_RELIABILITY.md](FIRMWARE_RELIABILITY.md). Its old PCB counts are historical.
- [Interference and bench-test matrix](PLACEMENT_AND_INTERFERENCE.md), [requirements](V1_REQUIREMENTS.md), and [lead questions](TEAM_LEAD_REQUESTS.md).

Open the native schematic for the current regulator symbol. The earlier Step 5 PDFs/renders are historical exports and should not be treated as the latest release. Do not rerun the full generators or whole-board autorouter over the hand-edited board.
