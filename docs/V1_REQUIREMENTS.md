# Version-one requirements — Step 2

**Current implementation — October 21:** Start with [RESUME_HERE.md](RESUME_HERE.md) and [COMPONENT_IMPLEMENTATION.md](COMPONENT_IMPLEMENTATION.md). Targeted component changes and the budget update are applied; fresh native checks pass. FB1 needs replacement and switch/header, harness, physical-fit and cold-test gates remain open. Earlier dated statements below are historical where superseded.

Prepared October 18, 2026. Status: core feature scope confirmed by Saadat; detailed performance and mission requirements remain open. No telemetry; record onboard and analyze after landing. No hardware population decisions below have been implemented.

## Purpose and status meanings

Build a balloon payload carrier PCB that uses Teensy 4.1 and the selected sensor breakouts to record motion, orientation, position, pressure, humidity and temperature to microSD. Preserve measured quantities so later analysis can distinguish measurements from derived altitude and orientation estimates.

- **Baseline:** established by the current project direction and supplied parts list.
- **Proposed:** an engineering recommendation for the first prototype; adjustable after team feedback and interface verification.
- **Open:** missing mission or mechanical information; resolve by the stated milestone.

The carrier approach is the working interpretation of the breakout products. Module mounting style and exact board revisions are still to be verified. This document defines proposed behavior and acceptance work; it does not claim the hardware or firmware already provides it.

Step 3 clarification: Saadat confirmed the modules have not been purchased and directed use of the spreadsheet's exact product numbers. BNO055 #2472 therefore means the non-QT board; do not substitute a QT footprint. See [the module map](SENSOR_CONNECTION_MAP.md) for verified interfaces and outstanding mechanical checks.

On October 18, Saadat selected the core logger with power control, status LEDs and supply monitoring. He reaffirmed gyroscope, acceleration, GPS, pressure, temperature and altitude measurements from the lead's direction. Humidity remains included through the supplied MS8607 selection; orientation/magnetic diagnostics remain in the working logging plan. Measurement types are established; numerical ranges, accuracy and sampling targets are not yet approved. Saadat is primarily designing the PCB and does not currently know the battery or flight duration. Those inputs remain assigned to the lead/team and do not block Step 3 interface research.

## Team clarification supplied by Saadat

**Latest temperature and assembly decisions, October 20:** the lead specifies -40 degrees, recorded as **-40 C minimum battery operating temperature** (also -40 F), superseding the earlier -45 C screening assumption. Saadat confirms **through-hole soldered sensors** and a custom casing to be CAD-designed after the PCB layout is complete. Working implementation uses soldered header pins at the breakout and carrier holes, not removable sensor sockets. Exact header dimensions, assembled height and mechanical retention still require fit review; Teensy/regulator mounting is unchanged. Three-hour powered runtime remains confirmed. Cold capacity and the entire assembly's thermal suitability still require verification; see MODULE_ASSEMBLY_PLAN.md.

**Altitude/mounting update, October 20:** Saadat expects about 30,000 ft altitude and does not yet know the battery/PCB mounting arrangement. Record altitude as supplied; operating-temperature limits remain open. Approximately -44.5 C is a standard-atmosphere ambient reference at that altitude, not a confirmed component temperature. Continue component/BOM work while retaining mechanical and thermal release gates; see POWER_COST_MASS_BUDGET.md for sources and implications.

**Runtime confirmation, October 20:** Saadat states runtime will be three hours. Use three hours of total powered operation for battery sizing. Current planning allowances give 4.48 Wh consumed and an 8.01 Wh nameplate energy target. Temperature, battery selection and reserve/usable-energy validation remain open. This supersedes the earlier unknown/provisional-duration notes below.

**October 20 update:** the lead says nothing has been ordered, directs the design team to create power/cost/mass budgets and select a battery from them, and requests dimensions as small as possible while remaining functional. No exact enclosure size or approved duration was supplied. See [POWER_COST_MASS_BUDGET.md](POWER_COST_MASS_BUDGET.md); the comparison scenarios and usable-energy/reserve assumptions are not approved requirements.

The lead's replies, supplied in this chat on October 18, establish local recording with post-recovery analysis and request sufficient component spacing to avoid interference. The supplied parts spreadsheet remains the component-selection baseline. These messages are requirements evidence, not authorization to contact anyone or order hardware.

For version one, exclude the XBee radio, telemetry-specific connectors and radio transmit/receive/relay firmware from the planned implementation. No future-radio expansion header is required. Preserve historical source archives. GPS remains required as a receiver for position/time. Check component spacing using exact module guidance and final-enclosure tests; no universal separation distance or interference-free performance is assumed.

## Feature decisions

| Function | Existing reference | Version-one treatment | Status / reason |
| --- | --- | --- | --- |
| Processor and microSD | U$3, Teensy 4.1 | Retain Teensy and built-in microSD; record onboard for analysis after recovery. | Baseline; lead clarification |
| Motion and orientation | U$17 BNO055 | Use Adafruit product 2472; verify purchased PCB revision and footprint. Record calibration/validity with measurements. | Baseline |
| Alternative IMU | U$10 LSM9DS1 | Exclude from the core design; BNO055 is selected. Preserve original reference files. | Core scope confirmed by Saadat |
| Pressure, humidity and temperature | U$11 MS5611 | Replace with Adafruit MS8607 product 4716 and add humidity logging. | Baseline |
| GPS position and time | U$12/U$13/U$15/U$22/U$29 alternatives | Replace populated GPS alternatives with Adafruit PA1616D product 5440. Retain NMEA fields actually available from this receiver. | Baseline |
| Power entry and switching | U$5/U$6/U$7/U$8/U$28 | Choose one battery/input architecture after voltage range is known; provide on/off control and reviewed USB/external-power behavior. | Function confirmed; circuit open |
| Status indicators | D1-D4 | Include status LEDs. Proposed indications distinguish logging, degraded sensors and storage failure; exact LED count/pins and patterns to be selected. | Function confirmed; indication scheme proposed |
| Supply monitoring | Pin 26 and existing divider | Include supply-voltage monitoring. Recalculate the divider and protection for maximum input voltage; do not reuse values blindly. | Function confirmed; monitored rail and circuit open |
| OLED | U$9 | Exclude from the selected core package. | Core scope confirmed by Saadat |
| External/internal thermistors | U$16 and firmware pins 40/41 | Exclude remote probes from the selected core package. MS8607 temperature is a local sensor reading, not an assumed battery or external-air temperature. Revisit scope only if the required measurement location needs a remote probe. | Core scope confirmed; measurement location open |
| Telemetry | U$14 XBee, firmware pins 34/35 | Exclude from version one: remove radio-only circuitry and transmit/receive/relay code during implementation. Review shared signals before removal; pins become available only after mapping. | Resolved: no telemetry, per lead clarification supplied by Saadat |
| General button and switch | U$25/U$26, firmware pins 31/30 | A user control may mark events or request a clean logging stop. Avoid mandatory startup interaction in the proposed flight mode. | Proposed; workflow to agree |
| Pull-before-flight | U$24 | Keep decision open until its actual intended power/arming role is traced and the team confirms the launch workflow. Logging should not depend on an inferred launch event. | Open before schematic freeze |
| Servo outputs | U$23/U$27 | Exclude from the selected core package; no actuation behavior required. | Core scope confirmed by Saadat |
| Heater control | Firmware pins 28/29, thermistor pin 20 | Exclude from the selected core package. If later thermal requirements require heating, explicitly revise scope and power budget. | Core scope confirmed; thermal suitability unverified |
| General breakout/terminal connectors | U$1/U$2/U$4 | Retain only interfaces needed by the selected core package; identify every signal and power pin. | Scope set; interface mapping pending |
| Mounting and orientation markings | U$18-U$21 holes, U$30/U$32 graphics | Retain mounting intent and visible axes; verify coordinates, fasteners and enclosure fit before layout approval. | Baseline intent, dimensions open |

Selected package: the four selected modules, microSD, power control, status LEDs and supply monitoring. Telemetry, the alternative IMU, OLED, remote temperature probes, servos and heater are outside this version-one core scope. Exact power/stop controls and any pull-before-flight role remain open. No existing connector or component has been removed during this requirements step.

## Proposed measurement and logging behavior

These are prototype starting targets, not final science requirements or sensor maximum ratings. The selected operating modes, timing and bus loading must be verified in Step 3 and demonstrated in Step 6.

| Data | Proposed stored rate | Units and required context |
| --- | --- | --- |
| Acceleration and angular velocity | 10 Hz | m/s² and rad/s; X/Y/Z in a documented board frame. Label whether acceleration includes gravity; use distinct fields if linear acceleration is also recorded. |
| Orientation | 10 Hz | Quaternion w/x/y/z as the primary representation; optional Euler angles in degrees with documented rotation order and frame. Record fusion mode and calibration state. |
| Magnetic field | 10 Hz | µT X/Y/Z; useful for diagnosing orientation interference. Reads must not be advertised as independent new internal sensor conversions without evidence. |
| Pressure | 1 Hz | Pa, with acquisition timestamp and validity. |
| Humidity | 1 Hz | %RH, with acquisition timestamp and validity. |
| MS8607 temperature | 1 Hz | °C at the sensor location; do not label as ambient or battery temperature without placement validation. |
| GPS | Configure 1 Hz solutions initially; record each complete selected solution | Latitude/longitude in decimal degrees, altitude in m with its datum documented, UTC date/time when valid, fix quality, satellites and available quality indicators. Preserve source time and receive time. |
| Derived pressure altitude | 1 Hz, only from valid pressure | m; store the model/version and reference pressure, and distinguish standard-pressure or launch-relative altitude from GPS altitude. |
| Supply voltage and system health | 1 Hz proposed | V, per-device status, communication errors, dropped-record count, buffer high-water mark and SD-write failures. |

The legacy sketch initializes a 100 ms data delay, but GPS initialization changes that delay. The proposed design uses separate schedules so a GPS setting or missing fix does not change IMU sampling or block environmental logging. Ten hertz is a starting rate for general motion tracking; vibration/shock characterization may need substantially different sampling and filtering, which must be specified before claiming that capability.

Adafruit documents BNO055 acceleration, gyro and orientation outputs up to 100 Hz, with magnetic field output at 20 Hz. That supports investigating a 10 Hz prototype schedule, not a guarantee of complete-system throughput. [BNO055 output documentation](https://learn.adafruit.com/adafruit-bno055-absolute-orientation-sensor/overview)

The PA1616D product page specifies a 1–10 Hz update range and notes combined-constellation NMEA talker prefixes. The proposed 1 Hz configuration and supported sentences must be verified with the actual module; the parser must not assume every sentence starts with GP. [PA1616D documentation](https://www.adafruit.com/product/5440)

The MS8607 product provides pressure, humidity and temperature measurements; conversion settings and operating limits remain Step 3 work. [MS8607 documentation](https://www.adafruit.com/product/4716)

## Proposed operational requirements and acceptance checks

| ID | Requirement | How we will verify it |
| --- | --- | --- |
| LOG-01 | Start a new recording session automatically on power-up with valid storage. Do not overwrite earlier sessions or wait indefinitely for USB, OLED, a button or a GPS fix. | Repeated standalone cold boots with the optional devices absent; check distinct session files and a recorded boot event. Proposed startup target: first local sensor record within 10 s on healthy hardware, subject to measured initialization time. GPS acquisition is excluded from that target. |
| LOG-02 | Give every record a session ID, stream sequence number, monotonic acquisition time and validity/status. Store UTC only with a declared source and synchronization status. | Check ordering, reboot boundaries, missing GPS time and later time acquisition. A new fix must not make elapsed time jump backward. |
| LOG-03 | Do not present a missing, invalid or old reading as a fresh valid measurement. A missing device must not block other healthy streams. | Disconnect or simulate failure of each sensor; ensure independent logging continues and invalid/stale state is visible. Determine field-specific freshness limits from verified timing before implementation. |
| LOG-04 | Use documented machine-readable logs, with a stable schema and units. Proposed files: separate IMU, environment, GPS and health CSV streams, events, and session metadata. Store firmware revision, configuration, board-axis definition, calibration details and pressure-altitude settings. | Parse files with an independent analysis script, check types/units and join streams by timestamps. Do not manufacture unavailable u-blox-specific accuracy or RTK fields. |
| LOG-05 | Capture data on independent schedules and buffer writes. Report missed deadlines, queue overflow and write failures. | Run all selected features together. Proposed nominal bench target: no unexplained lost records, no resets and stream counts within 1% of the configured schedule after startup, with every skip explicitly counted. Thresholds must be reviewed for the mission. |
| LOG-06 | Flush buffered data periodically and provide a clean-stop path if a control is retained. Proposed flush interval: at most 1 s during healthy operation. | Measure write latency and test clean shutdown and randomized power interruptions with the chosen card. A flush interval is not a guaranteed power-loss bound; maximum tolerable loss and filesystem recovery criteria remain open. |
| LOG-07 | Storage failure or a full card must produce a visible fault, never a false logging-success indication. Do not erase data automatically to recover space. | Test absent, full and failing cards; verify status and bounded recovery behavior without hanging all processing. |
| PWR-01 | Operate across the selected battery's full input range and selected load peaks, with documented USB/external-power behavior. | Review regulator/divider limits and measure rails during startup, SD writes and other retained loads. Exclude telemetry loads from the version-one budget. Exact voltages, transient limits and margin await the power choice. |
| RUN-01 | Required total powered runtime is three hours (Saadat, October 20). Proposed first endurance test: four continuous hours at the selected rates, initially on a bench supply. | Record sample counts, timing, resets, errors, current and rail behavior. For four hours the nominal targets are 144,000 records per 10 Hz stream and 14,400 per 1 Hz stream, adjusted for defined start/stop boundaries. This is not battery or flight qualification. |
| INT-01 | Space and arrange components to control interference, and demonstrate that simultaneous operation does not materially degrade sensor or GPS performance. | Apply the interference matrix in DEVELOPMENT_PLAN.md. Review module-specific placement guidance, magnetic sources, GPS surroundings, power/ground paths and thermal separation; compare operation with SD activity and other retained loads on/off in the final mounting/enclosure. Numerical allowable changes depend on required measurement accuracy and the reference instrument. |
| MECH-01 | Fit modules, mounting hardware, wiring and enclosure; allow USB/microSD access and appropriate sensor exposure. | Verified drawings, assembly inspection and a physical fit check. The approximately 97.79 mm square original outline is a reference, not a new enclosure specification. |
| REL-01 | Keep library, schematic, PCB, BOM and firmware configuration consistent and versioned. | Review ERC/DRC/parity results and justified exceptions, manufacturer files, build instructions and prototype test evidence before release. |

No battery endurance, accuracy, temperature capability or interference performance is claimed by setting these requirements.

## Decisions to resolve and when they matter

| ID | Decision / current state | Owner | Required by | Work that can proceed now |
| --- | --- | --- | --- | --- |
| D01 | Resolved October 18: Saadat selected core logger with power control, status LEDs and supply monitoring. OLED, remote probes, alternate IMU, servos and heater excluded from core scope. | Saadat, direct reply | Apply during Steps 3-7 | Map selected interfaces and review shared circuitry before implementation. |
| D02 | Battery chemistry, cell count, capacity, maximum/minimum voltage, connector and USB use: unknown. | Team; design calculations by Codex | Before power schematic (Step 5) | Inventory loads and verify module supplies. |
| D03 | Measurement types reaffirmed October 18: gyro, acceleration, GPS, pressure, temperature and altitude; humidity retained from workbook selection. Quantitative ranges, accuracy and rates remain open; rates above proposed. | Lead/team | Before final sensor configuration, firmware performance acceptance and design sign-off | Prepare configurable logging architecture and datasheet comparison without requesting the measurement list again. |
| D04 | Total powered duration confirmed at three hours by Saadat, October 20; 25% energy reserve remains proposed. | Lead/team | Before battery sizing and endurance acceptance | Use the explicitly provisional four-hour bench scenario. |
| D05 | Resolved: no telemetry. Local microSD recording and analysis after recovery. | Lead, clarification supplied by Saadat | Apply during Steps 3-7 | Remove radio-only requirements from pin, power, layout and firmware plans; retain GPS reception. |
| D06 | Enclosure, mount dimensions, weight limit, module retention and remote temperature locations: unknown. | Team | Before placement/layout approval (Step 7); earlier for connector choices | Verify module mechanical drawings. |
| D07 | Expected external/internal temperatures, pressure/altitude profile and sensor exposure: unknown. | Lead/team | Before environmental acceptance and final hardware sign-off | Continue with selected sensors; document specific conflicts only if found. |
| D08 | Manufacturer, stackup, board thickness, quantities, assembly responsibility and total budget: unknown. | Team/manufacturer | Rules before layout sign-off; commercial details before order | Keep design portable; do not assume historical Gerbers define the release. |
| D09 | Acceptable data loss after abrupt power removal and whether a clean-stop control is required: unknown. | Lead/team | Before storage strategy and power design freeze (Steps 5-6) | Define fault logging and measure actual SD behavior. |
| D10 | Heater and actuators excluded by selected core scope. Launch/power/stop workflow and pull-before-flight role remain open. | Lead/team | Before power/control circuitry freeze (Steps 5-6) | Trace original control circuits; do not carry legacy actuation behavior into the logger. |

Unknowns remain explicit. A proposed default is not a team-approved flight requirement. Resolve decisions at their dependency milestone rather than blocking unrelated module research.

## Evidence used in this draft

- Current README, CUSTOM_BOARD_BRIEF and DEVELOPMENT_PLAN; supplied workbook source selection already recorded in docs/reference.
- Native KiCad-exported component list in `docs/validation/2026-10-18/schematic-netlist.xml` identifies the optional hardware references above.
- `Firmware_reference/PTERODACTYL_v19_1.zip`, main sketch `PTERODACTYL_v19_1/PTERODACTYL_v19_1/examples/PTERODACTYL_v3_8_19_1/PTERODACTYL_v3_8_19_1.ino`: pins/configuration near lines 29-40; log header at 204; timing at 229; heater setup at 255-266; interactive setup beginning at 319; scheduler at 837; batched SD writes at 1264-1271. Its companion GPS.ino changes `dataDelay` during receiver configuration. These are source-code observations, not tested runtime results.
- Manufacturer pages linked above were consulted October 18, 2026 for high-level capability checks. Exact interfaces, timing, footprints and electrical operating limits are Step 3 deliverables.

## Step 2 completion state

Feature inventory, proposed behavior, acceptance checks and decision deadlines are documented. Core scope and no telemetry are resolved; the lead's interference/spacing requirement is explicit. Step 2 is ready to support Step 3 interface work. Full requirements freeze remains open for mission, power, mechanical and quantitative performance inputs from the team.

## Step 2 working review — October 18 continuation

Saadat requested continuing Step 2 after the handoff was published. The immediate task is to settle product scope and mission needs. The questions below collect missing requirements; none of the suggested answers becomes approved through silence.

### Decisions to address first

1. **Feature package (D01/D10):** core package selected by Saadat. Power/stop controls and any pull-before-flight role still need definition. The selection does not approve a particular power circuit.
2. **Power and runtime (D02/D04):** unknown to Saadat, who is primarily designing the PCB. Lead/team to supply battery and runtime information by the decision-register milestones. Continue module supply/load research without assuming a battery voltage or treating the workbook's three hours as a flight requirement.
3. **Measurement purpose (D03/D07):** measurement types have been supplied. The table below concerns remaining numerical performance and placement needs for the lead/team; it is not a request to repeat the sensor list or choose new sensors.

| Measurement | Information needed from the team | Consequence for the design |
| --- | --- | --- |
| Acceleration and rotation | General payload motion, or vibration/shock analysis? Expected range and fastest event of interest? | Sets sampling/filtering requirements and determines whether the proposed 10 Hz logs meet the objective. |
| Orientation and magnetic field | Relative attitude changes or absolute heading? Required error and mounting-axis definition? | Sets calibration procedure and allowable magnetic interference during combined operation. |
| Position and altitude | Track reconstruction, peak altitude, or both? Required position/altitude error and time resolution? | Sets GPS logging expectations and how pressure-derived altitude is compared with GPS altitude. |
| Pressure, humidity and temperature | Measure air inside the enclosure, outside air, or a specific component? Expected conditions and acceptable error? | Sets exposure, probe needs, thermal placement and reference-test conditions. |
| Timing | Is correlation with another payload or event required, and to what precision? | Sets synchronization and timestamp acceptance requirements. |

### Information to collect before the later design gates

Keep D06-D10 in the decision register until answered: enclosure/mounting and weight allowance; operating environment; manufacturer and build budget; tolerated power-loss data loss and stop procedure; launch/arming and any actuation needs. These have different deadlines and do not all prevent interface research.

An unsent brief for the team/lead, if Saadat chooses to share it:

> We have selected the core logger: Teensy 4.1, BNO055, MS8607, PA1616D, microSD, power control, status LEDs and supply monitoring, with no telemetry. The measurement list is recorded. To finalize the PCB and test requirements, please share battery/input details, total powered duration and reserve, measurement ranges/accuracy/timing targets, intended temperature measurement location, enclosure/mounting limits, operating conditions, manufacturing/budget constraints and the power/recording-stop workflow when available.

### Completion checklist

- [x] Selected modules, local recording and no telemetry recorded with their source.
- [x] Legacy features inventoried; proposed logging behavior and verification methods documented.
- [x] Interference review and simultaneous-operation testing required.
- [x] Open decisions assigned an owner and a design milestone.
- [x] Saadat selected the core feature package; heater/actuators are outside scope (D01 and part of D10).
- [ ] Team has defined launch/power/stop workflow and any pull-before-flight role (remaining D10).
- [ ] Team has accepted measurement goals and initial logging targets, or explicitly assigned unresolved targets to a later milestone (D03).
- [ ] Power/runtime inputs and mechanical/environmental constraints are recorded as confirmed values or explicitly deferred decisions with owners (D02/D04/D06/D07).
- [ ] Manufacturing and data-retention constraints have an agreed resolution milestone (D08/D09).

The documentation deliverable for Step 2 exists. Requirements freeze remains open. Record each answer in the existing decision register with its source/date, update affected requirements, and keep deferred decisions visible at their downstream gates. A completed planning checklist does not establish tested hardware performance.
