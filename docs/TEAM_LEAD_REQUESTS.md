# Open requests for the team lead

**Current implementation — October 21:** Start with [RESUME_HERE.md](RESUME_HERE.md) and [COMPONENT_IMPLEMENTATION.md](COMPONENT_IMPLEMENTATION.md). Targeted component changes and the budget update are applied; fresh native checks pass. FB1 needs replacement and switch/header, harness, physical-fit and cold-test gates remain open. Earlier dated statements below are historical where superseded.

**Latest answers, October 20:** three-hour runtime and **-40 C minimum battery temperature** are now supplied. Saadat confirms **through-hole soldered sensors**, with custom casing CAD after the board layout is complete. Do not keep requesting these choices; header geometry/retention, cold performance, maximum temperature, attachment constraints and final enclosure fit remain design/validation tasks. Earlier sensor-socket requests are superseded for BNO055/MS8607/GPS.

**October 20 budget reply:** the lead confirmed nothing is ordered, asked us to make power/cost/mass budgets and then choose a battery, and requested the smallest functional package. The first [budget draft](POWER_COST_MASS_BUDGET.md) is calculated and checked. Saadat confirmed three hours of powered runtime on October 20. We still need operating temperatures and any cost/mass/mounting constraints from the team; battery selection and enclosure sizing are design tasks, not unanswered requests for the lead to nominate products.

**October 20 GPS update:** [U5 is now assigned, placed and routed](GPS_CARRIER_INTEGRATION.md) after Saadat visually accepted the source CAD geometry. Earlier requests to obtain geometry before assignment are superseded. Actual-module fit, socket/spacer choice, underside holder clearance, antenna exposure and retention still need evidence; this is not manufacturer confirmation or fabrication approval.

Prepared October 19, 2026. Working branch: `saadat-dev`.

This page lists the inputs needed from the team lead or team to close Step 3 and approve Step 4 placement, plus inputs Step 5 will need soon. It also gives a short plain-language summary of Steps 1–3 for teammates. Details and evidence live in the linked documents; [CURRENT_STATUS.md](CURRENT_STATUS.md) remains the authoritative resume point.

**Current checkpoint:** all five module carrier footprints, including GPS, are integrated and routed in v4. Physical fit, battery/mission inputs and manufacturer approval remain open. The original Steps 1–3 explanation below is historical where it describes missing GPS; use [GPS_CARRIER_INTEGRATION.md](GPS_CARRIER_INTEGRATION.md) for current geometry and checks.

## Steps 1–3 in brief

**Goal:** redesign the PTERODACTYL v3.8 balloon payload board around a Teensy 4.1 and three Adafruit sensor breakouts, logging to microSD for analysis after landing. No telemetry radio.

- **Step 1 — starting point recorded.** The imported v3.8 KiCad design was checked unchanged: 33 ERC errors/10 warnings, 11 DRC errors/428 warnings, 0 unconnected items, and 52 schematic/PCB parity warnings. These are inherited problems to clean up during redesign, not new ones. See [VALIDATION_SUMMARY.md](validation/2026-10-18/VALIDATION_SUMMARY.md).
- **Step 2 — scope chosen.** Teensy 4.1, BNO055 #2472, MS8607 #4716, PA1616D GPS #5440 (exact spreadsheet products). Core logger with power control, status LEDs and supply monitoring. Radio/XBee, OLED, remote probes, heater, servos and alternative IMU are excluded. Sample rates and startup behavior are proposals only. See [V1_REQUIREMENTS.md](V1_REQUIREMENTS.md).
- **Step 3 — connections and mounting drafted.** Every module pin has an assigned connection or a deliberate unused disposition. BNO055 and MS8607 share I2C on Teensy pins 18/19 (no address conflict); GPS uses Serial2 on pins 7/8; each breakout takes 3.3 V on VIN. The old BNO055 footprint was found to match the STEMMA QT version, not #2472. New project-local footprints (BNO055, MS8607, Teensy) and symbols (BNO055, MS8607, GPS logical) were built from manufacturer files and pass automated checks. A socket/spacer mounting proposal exists. The current #5440 GPS has an unverified legacy comparison footprint only; U5 remains unassigned. The other four carrier footprints, including the regulator, are integrated into the active v4 design. See [SENSOR_CONNECTION_MAP.md](SENSOR_CONNECTION_MAP.md) and [MODULE_ASSEMBLY_PLAN.md](MODULE_ASSEMBLY_PLAN.md).

Step 3 is drafted and checked on screen but cannot be signed off without the inputs below.

## Needed to close Step 3

| # | Request | Why it is needed | Closes |
| --- | --- | --- | --- |
| R1 | **Coordinate purchasing for dry-fit modules**, including the regulator | Nothing ordered as of the lead's October 20 reply. Footprints are integrated; actual module/socket/holder fit still needs evidence. | M01, M04 |
| R2 | **Manufacturer drawing if physical fit reveals a mismatch** | Earlier requirement to obtain new CAD before assignment is superseded by Saadat's visual acceptance. No Adafruit message was sent. | M01 |
| R3 | **Mounting/environment constraints**; design team proposes compact enclosure | Lead wants the smallest functional package. Final size depends on battery, headers, access, antenna and sensor exposure. | M02 |
| R4 | **Approval of headers/sockets and mounting hardware** — proposed Samtec SSW sockets with HTSW headers; spacer and screw material rules | Locks the assembled height and connector engagement. Any temperature, vibration or material rules for flight hardware apply here; stainless fasteners may be slightly magnetic near the BNO055. | M03 |
| R5 | **Resolved: AISLER** | Their finished-hole tolerance and annular-ring rules confirm the 1.04 mm socket holes and 1.8 mm pads. | M03 |

Gate definitions (M01–M04) and the measurement record template are in [MODULE_ASSEMBLY_PLAN.md](MODULE_ASSEMBLY_PLAN.md).

## Needed to approve Step 4 placement

The draft floor plan in [PLACEMENT_AND_INTERFERENCE.md](PLACEMENT_AND_INTERFERENCE.md) assumes the answers below. Confirm or correct them.

| # | Request | Why it is needed |
| --- | --- | --- |
| R6 | **How is the board mounted in flight?** Horizontal with components facing up is assumed. | The GPS patch antenna needs to face the sky; the BNO055 axis setup depends on orientation. |
| R7 | **Review proposed battery placement after design-team selection** | Battery material/current can disturb the BNO055 magnetometer; maintain separation and verify on hardware. |
| R8 | **Is the enclosure vented, and should temperature/humidity be outside air or inside the box?** | A sealed box gives wrong pressure readings. Outside-air temperature needs the sensor exposed, and remote probes were excluded. |
| R9 | **Must the status LEDs be visible from outside the enclosure?** | Decides LED position and whether a window or light pipe is needed. |

## Needed soon for Step 5

The v4 schematic uses the S9V11F5 regulator: at least 3 V at regulator VIN is required for startup; 2 V is only the running minimum. The selected battery must provide startup margin after sag and upstream losses. Battery choice still determines protection, connectors, switch/fuse and capacitor ratings. Ask at the same time:

- Total powered duration is three hours (Saadat, October 20). Minimum/maximum operating temperatures remain open. The design team then selects battery type, nominal/minimum voltage, capacity and protection from the budget.
- Any maximum cost, installed mass and mounting constraints. The logger now uses the confirmed three-hour runtime; two, four and six hours remain comparisons.
- Required sample rates and measurement accuracy, if any.
- Power switch and pull-before-flight behavior (how the logger is started and stopped).

These correspond to open decisions in the D01–D10 register in [V1_REQUIREMENTS.md](V1_REQUIREMENTS.md).

## Recording answers

When an answer arrives, record it with its source and date in the relevant document (requirements decision register, assembly closure record or session note), update CURRENT_STATUS.md, and mark the request here as answered rather than deleting it.

| # | Status | Answer, source and date |
| --- | --- | --- |
| R1 | Purchasing open | Lead confirms nothing ordered; supplied by Saadat, October 20. |
| R2 | Superseded before assignment | GPS integrated after Saadat's visual acceptance; actual fit remains open. |
| R3 | Direction received; design open | Smallest functional package; no fixed dimensions, October 20 lead reply. |
| R4 | Open | |
| R5 | Open | |
| R6 | Open | |
| R7 | Design-team proposal pending | Lead asks us to select battery from budgets, October 20. |
| R8 | Open | |
| R9 | Open | |
