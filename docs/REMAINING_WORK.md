# What's done and what's left

## First prototype scope and order checkpoint - October 21, 2026

**Current authority: [FIRST_PROTOTYPE_RELEASE.md](FIRST_PROTOTYPE_RELEASE.md).** PCB checks and AISLER upload/preview passed; project TCVOYNZG revision 1 is ready for checkout. FB1/SW1/SW2/J3 are selected for P1. The user explicitly excludes physical testing, flight qualification, subsequent redesign and casing from this phase; older statements requiring those before PCB fabrication are superseded. Assembly receipt/polarity checks remain part of building the prototype. No order placed. Updated known cost is USD 129.37 (15 price lines missing); entered mass 170.25 g (three missing). The provisional EUR board quote is separate.

**Current implementation — October 21:** Targeted component/connector/capacitor edits and the budget update are now applied. Fresh ERC/DRC/connectivity/parity and preservation checks pass. Read [RESUME_HERE.md](RESUME_HERE.md), then [COMPONENT_IMPLEMENTATION.md](COMPONENT_IMPLEMENTATION.md) for the authoritative boundary. Four BOM references remain explicit candidates; holder/harness fit, cold runtime and flight qualification remain open. Earlier dated figures and research-only statements below are historical where superseded.

## Current next actions after targeted implementation

1. Close SW1/SW2 drawings and contact details, replacement for obsolete FB1 and J3 shunt/fit. Four candidate flags remain visible in the exported BOM.
2. Finish BH4AAW harness, pack-side insulation/protection, external switch, crimps and nonmagnetic retention. Validate actual soldered-header tolerances/spacers and capacitor/module clearances.
3. Review AISLER upload/stackup/mask processing and supplier quotes before fabrication release. Local AISLER dimensional rules pass; no external order/upload has been made.
4. Cold loaded startup/runtime/transient/fault and complete logging tests; dry-fit, vibration/retention, interference and altitude/thermal review. An 8.669 Wh model target is not proof that L91 delivers that usable energy at -40 C.
5. GPS freshness firmware work, then casing CAD around the measured final assembly.

Completed in this continuation: targeted KiCad component fields and local footprints, J1/J2 connector replacement, corrected capacitor envelopes, AISLER dimensional rules, fresh validation/preservation checks, updated live budget and exported review workbook. See COMPONENT_IMPLEMENTATION.md. Historical checklist below is retained for context.

Updated October 21, 2026. Branch: `saadat-dev`. Current design: GPS integrated after `e2664ad`; see [GPS_CARRIER_INTEGRATION.md](GPS_CARRIER_INTEGRATION.md).

For the teammate meeting, use [TEAM_MEETING_2026-10-20.md](TEAM_MEETING_2026-10-20.md): completed work, remaining tasks, inputs needed, proposed owners and a decision log.

## Current status

The v4 schematic and carrier PCB now contain all 51 footprints, including U5/GPS. Latest checks: **0 ERC / 0 enabled physical DRC / 0 unconnected / 0 schematic parity issues**. This does not approve fabrication. Firmware compiles but has not been validated on complete hardware.

| Step | Current state |
| --- | --- |
| 1 — Legacy baseline review | Completed and documented |
| 2 — Requirements | Core scope agreed; quantitative mission, power and operating inputs open |
| 3 — Module interfaces / mounting | Five carrier footprints integrated; GPS geometry visually accepted by Saadat; physical-fit gates open |
| 4 — Placement / interference | Plan, spacing checks and test matrix prepared; measured performance and team approval open |
| 5 — Power / schematic | ERC-clean draft; candidate ratings, battery contract, BOM and review open |
| 6 — Firmware | SD recovery, BNO timeout and sensor transfer/CRC handling implemented/host-tested; GPS freshness and hardware tests open |
| 7 — PCB | All footprints routed, including GPS; final fit and release review open |
| 8–10 — Prototype, test, flight version | Not completed |

## Completed implementation

- [x] Integrate source-checked BNO055, MS8607, Teensy and S9V11F5 carrier footprints.
- [x] Route all present power connections and relocate rail test points.
- [x] Place C2 near the ADC, correct I2C order and add local return stitching.
- [x] Add readable silkscreen and measure current PCB geometry in the checks.
- [x] Document the regulator's 3 V startup minimum; final battery margin is still open.
- [x] Compile the new logger and record the source-review findings.
- [x] Implement and host-test SD session recovery and bounded BNO reset polling; see [FIRMWARE_RELIABILITY.md](FIRMWARE_RELIABILITY.md).

## Remaining work

### Finalization order — October 20

We have enough direction to begin final component and layout work: 3 h powered runtime, -40 C battery minimum, through-hole soldered sensor breakouts, and custom casing CAD after the board layout. Remaining selections can be developed by the design team; they do not all require new lead input before work proceeds.

1. Select/test battery candidates and SD card; check cold loaded voltage/capacity, startup, peak current and cutoff/protection. Review F1/Q1/D1/J1/J2 and input capacitance against the chosen pack.
2. Select exact soldered sensor headers and passive/control parts. Check physical dimensions against the actual footprints before ordering. C5/C6/C8/C10 are currently 10 uF values assigned generic 5 mm lead-pitch disc footprints: exact capacitor body size, voltage/temperature rating and usable capacitance must be matched; assigned footprints alone do not establish fit. C1/C3 also lack exact MPNs.
3. Confirm assembled module heights, underside clearances, retention, battery envelope and access. Use those dimensions for custom casing CAD; verify fit before releasing fabrication files.
4. Apply AISLER rules and confirm the stackup/assembly approach, close control population/workflow, and obtain complete quotes and mass estimates. AISLER is selected; no spending cap or hard mass ceiling applies. Q1 is currently SOT-23 surface mount; the user's through-hole sensor instruction has not changed Q1. Plan its assembly accordingly.
5. Independently review the final schematic/layout, rerun ERC/DRC/parity, then generate and inspect current Gerbers/drills before ordering. Firmware/hardware validation remains required after assembly.

**Fresh BOM checkpoint:** [finalization-bom.csv](validation/2026-10-20/finalization-bom.csv) was exported directly from the current v4 schematic with KiCad 10.0.7, preserving DNP rows. It has 47 schematic rows, all with footprints; 35 have blank MPN fields and seven carry candidate MPNs. These are per-reference fields, not 42 unique missing products: test pads and the DNP spare header need population decisions rather than necessarily purchased parts. Four PCB mounting holes account for the difference from 51 PCB footprints. U2/U5 assignments are present; the October 19 BOM is historical. This export is a review list, not a purchase-ready BOM. No PCB or schematic edits were made.

- [x] **Requirements update:** three-hour runtime; lead specifies -40 C battery minimum; Saadat confirms through-hole soldered sensors and casing CAD after final PCB layout.
- [ ] **Through-hole assembly:** replace sensor-socket BOM proposals with exact solderable headers; verify finished-hole fit, pin lengths, underside clearance, assembled height and retention. Update mechanical envelopes before casing CAD and fabrication release. Teensy/regulator mounting remains unchanged.

- [x] **First budget draft:** rail-aware power calculations, runtime scenarios, partial cost/mass and 22 workbook checks. See [POWER_COST_MASS_BUDGET.md](POWER_COST_MASS_BUDGET.md).
- [ ] **Budget closure:** use confirmed 3 h runtime and -40 C battery minimum; select SD and battery; review 0.7 A PTC/current/thermal margins; price 17 remaining lines and supply four missing masses. Nothing is ordered; dimensions should be minimized after pack and mounting decisions.

- [x] **GPS integration:** user visually accepted the source CAD geometry; assigned, placed and routed U5. See [GPS_CARRIER_INTEGRATION.md](GPS_CARRIER_INTEGRATION.md).
- [ ] **GPS fit:** actual module/socket/spacer fit, underside holder clearance, antenna exposure and retention remain to be checked.
- [ ] **Power/BOM:** verify candidate fuse, MOSFET, bead, connector/capacitor ratings; settle the battery/startup contract; review C1/C4 proximity and transients; add exact assembly hardware to the BOM.
- [x] Implement and host-test [sensor transfer/CRC validity](SENSOR_READ_VALIDITY.md), empty failed-data rows and recovery.
- [ ] **Firmware:** reject stale/mismatched GPS RMC fields and add CSV validation. SD recovery, BNO timeout/cooldown and sensor error paths still need hardware verification.
- [ ] **Mechanical:** enclosure, orientation, retention, header/socket fit, antenna/sensor exposure and USB/SD access; close M01–M04 with actual evidence.
- [ ] **Fabrication:** apply chosen manufacturer rules/stackup, independently review the complete design, require clean parity and zero unconnected items with GPS installed, then generate and inspect fresh Gerbers/drills.
- [ ] **Prototype:** assemble and test startup/current/rails, sensor/GPS logging, storage failures, endurance, magnetic/GPS interference and thermal effects.

## Team inputs needed

The lead confirmed nothing is ordered, asked the design team to choose a battery from power/cost/mass budgets, and requested the smallest functional package. Saadat confirmed three hours of powered runtime on October 20. Already supplied: -40 C battery minimum, AISLER, no spending cap, and practical mass minimization without a hard ceiling. Still open: maximum temperature and whole-assembly thermal verification; quantitative measurement targets; mounting/exposure constraints; control/data-loss acceptance and assembly responsibility. These do not all require fresh lead input before engineering work continues. See [TEAM_LEAD_REQUESTS.md](TEAM_LEAD_REQUESTS.md). No message has been sent on the team's behalf.

## Current evidence and collaboration

Use [GPS_CARRIER_INTEGRATION.md](GPS_CARRIER_INTEGRATION.md) and `validation/2026-10-20/gps-integration/` for current PCB checks/views. The board now has 246 tracks and 25 vias; SDA/SCL are 135.163/128.209 mm. Earlier autoroute/Step 5 exports are historical.

Pull the branch after preserving any local work. Agree a single PCB editor at a time and review each handoff. Do not rerun full schematic/PCB generators or the whole-board autorouter. After targeted changes, run the relevant checks (`tools/verify_v4_layout.py` with KiCad Python for the current layout), update the status/session notes and keep the remaining physical-fit and fabrication gates explicit.
