# What's done and what's left

Updated October 19, 2026. Branch: `saadat-dev`. Current design checkpoint: `f55657f`.

For the teammate meeting, use [TEAM_MEETING_2026-10-20.md](TEAM_MEETING_2026-10-20.md): completed work, remaining tasks, inputs needed, proposed owners and a decision log.

## Current status

The v4 schematic and carrier PCB are implemented for 50 placed footprints. Latest enabled physical DRC: **0 violations / 0 unconnected items**, with **only missing U5/GPS** in parity. This excludes the missing GPS connections and does not approve fabrication. Firmware compiles but has not been validated on complete hardware.

| Step | Current state |
| --- | --- |
| 1 — Legacy baseline review | Completed and documented |
| 2 — Requirements | Core scope agreed; quantitative mission, power and operating inputs open |
| 3 — Module interfaces / mounting | Four carrier footprints integrated; GPS geometry and physical-fit gates open |
| 4 — Placement / interference | Plan, spacing checks and test matrix prepared; measured performance and team approval open |
| 5 — Power / schematic | ERC-clean draft; candidate ratings, battery contract, BOM and review open |
| 6 — Firmware | Compiles; four reliability fixes and hardware tests open |
| 7 — PCB | Present footprints routed; ADC/I2C/silkscreen cleanup done; GPS and final release review open |
| 8–10 — Prototype, test, flight version | Not completed |

## Completed implementation

- [x] Integrate source-checked BNO055, MS8607, Teensy and S9V11F5 carrier footprints.
- [x] Route all present power connections and relocate rail test points.
- [x] Place C2 near the ADC, correct I2C order and add local return stitching.
- [x] Add readable silkscreen and measure current PCB geometry in the checks.
- [x] Document the regulator's 3 V startup minimum; final battery margin is still open.
- [x] Compile the new logger and record the source-review findings.

## Remaining work

- [ ] **GPS:** obtain current #5440 geometry, approve/assign U5 and route it. The legacy comparison footprint remains unverified.
- [ ] **Power/BOM:** verify candidate fuse, MOSFET, bead, connector/capacitor ratings; settle the battery/startup contract; review C1/C4 proximity and transients; add exact assembly hardware to the BOM.
- [ ] **Firmware:** propagate sensor transfer/CRC failures, bound BNO reset waits, recover SD partial-open/write failures, and reject stale GPS RMC fields.
- [ ] **Mechanical:** enclosure, orientation, retention, header/socket fit, antenna/sensor exposure and USB/SD access; close M01–M04 with actual evidence.
- [ ] **Fabrication:** apply chosen manufacturer rules/stackup, independently review the complete design, require clean parity and zero unconnected items with GPS installed, then generate and inspect fresh Gerbers/drills.
- [ ] **Prototype:** assemble and test startup/current/rails, sensor/GPS logging, storage failures, endurance, magnetic/GPS interference and thermal effects.

## Team inputs needed

Exact parts on hand/purchasing; battery and powered runtime; required measurement rates/ranges/accuracy; enclosure and mounting; sensor exposure; start/stop/data-loss requirements; PCB supplier, budget and assembly responsibility. See [TEAM_LEAD_REQUESTS.md](TEAM_LEAD_REQUESTS.md). No message has been sent on the team's behalf.

## Current evidence and collaboration

Use [LAYOUT_REVIEW_CLEANUP.md](LAYOUT_REVIEW_CLEANUP.md) and `validation/2026-10-19/layout-review/` for current PCB checks/views. The board now has 233 tracks and 17 vias; SDA/SCL are 135.163/128.209 mm. Earlier autoroute/Step 5 exports are historical.

Pull the branch after preserving any local work. Agree a single PCB editor at a time and review each handoff. Do not rerun full schematic/PCB generators or the whole-board autorouter. After targeted changes, run the relevant checks (`tools/verify_v4_layout.py` with KiCad Python for the current layout), update the status/session notes and keep the remaining GPS gate explicit.
