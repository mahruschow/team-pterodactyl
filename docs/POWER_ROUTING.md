# Power routing checkpoint — October 19, 2026

All connections among the **50 currently placed footprints** are routed. Native KiCad 10.0.7 reports **0 enabled physical DRC violations and 0 unconnected items** after refill. Schematic parity still reports **missing U5/GPS**. This is a partial-board routing milestone, not fabrication approval or completion of GPS wiring.

The preceding regulator/GPS footprint work was committed and pushed as `d40fba3` on `saadat-dev`. This follow-up edits the active `Native_KiCad_v4/PTERODACTYL_v4.kicad_pcb` through targeted changes. The full generators and autorouter were not rerun.

## Changes

- Connected U2 VIN to `/VBAT_SW` and VOUT to `+5V`; completed the +5V connections through C3/C4 to Teensy VIN and TP2.
- Connected the sensor supply from FB1/C5 to the BNO055 and MS8607 supply/decoupling pads, C10/C11 and TP4. The future GPS still needs its physical supply connection.
- Moved TP1 and TP2 beside the power section, and TP4 beside the sensor rail. Removed the old unloaded TP1 branch across the board: five segments, 68.667 mm. Actual battery-current paths were retained.
- Added 37 power-track segments on the outer layers: 0.5 mm for battery/5 V and 0.3 mm for the sensor rail. No new vias were needed. Both inner GND planes were refilled.

Test-point pad centres in KiCad's absolute coordinates (millimetres):

| Reference | Net | X | Y |
| --- | --- | ---: | ---: |
| TP1 | VBAT_PROT | 177.000 | 119.202 |
| TP2 | +5V | 174.000 | 137.000 |
| TP4 | SENSOR_3V3 | 152.500 | 89.500 |

## Verification

Evidence: [routing comparison and metrics](validation/2026-10-19/power-routing/routing-check.json), [native DRC/parity](validation/2026-10-19/power-routing/drc.json), [changed-object identifiers](validation/2026-10-19/power-routing/targeted-edits.json).

| Check | Result |
| --- | --- |
| Enabled physical DRC / unconnected items | 0 / 0 |
| Schematic parity | Only missing U5 |
| Existing track/via objects preserved exactly | 197; only the five documented TP1 spur segments removed |
| Footprints | 47 unchanged; three test points moved with pad/net identities preserved |
| Schematic, symbols and project rules | Unchanged from `d40fba3` |
| Current tracks / vias | 224 segments, 1344.6 mm total / 10 vias |
| Longest I2C route | 110.5 mm, unchanged; below the proposed 150 mm limit |
| Existing power-class track widths | Pass |
| Seven module separation targets | Pass |
| Inner-plane tracks / GPS-envelope track endpoints | None; native rule-area DRC also passes |

The enabled checks and the project's unchanged ignored-check list are recorded in the DRC report. Zero violations does not establish manufacturer acceptance. Copper and In2 GND-plane plots were visually inspected: the new routes stay outside the GPS envelope and do not introduce a plane split. No additional supply route crosses beneath the BNO055 body; its existing VIN entry remains. This is layout evidence, not measured EMI or thermal performance.

Views: [outer copper with assembly references](validation/2026-10-19/power-routing/copper.svg), [In2 GND return plane](validation/2026-10-19/power-routing/return-plane.svg). Assembly references still need cleanup; these are review plots, not manufacturing outputs.

To repeat native DRC from the repository root, writing a fresh report in scratch storage:

```powershell
New-Item -ItemType Directory -Force work | Out-Null
& 'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe' pcb drc --format json --severity-all --schematic-parity --refill-zones --output work/power-routing-drc.json Native_KiCad_v4/PTERODACTYL_v4.kicad_pcb
```

Inspect all three report sections: `violations`, `unconnected_items` and `schematic_parity`. Keep the GPS warning visible. The current project's source hashes and comparison baseline are in the saved evidence.

**Later checkpoint:** [LAYOUT_REVIEW_CLEANUP.md](LAYOUT_REVIEW_CLEANUP.md) corrects ADC placement and I2C order and adds readable labels/local stitching. The metrics above preserve this earlier routing checkpoint.

## Remaining work

1. Close GPS M01 using revision-matched #5440 evidence or actual measurements, then assign and connect U5. The legacy comparison footprint remains unverified.
2. Review the entire layout, including existing I2C topology, ADC filter placement, return paths, remaining detours, silkscreen and any outer GND pours/stitching. This pass covers the open power connections, not every earlier routing decision.
3. Agree battery/startup margins, component ratings, module retention/fit, enclosure and manufacturer rules/stackup before fabrication review. Run the documented load, interference and thermal tests on a prototype.
4. Fix the four outstanding firmware reliability findings and test on hardware. No firmware or hardware testing occurred in this routing pass.

Do not regenerate the schematic/PCB or rerun the whole-board autorouter over the current design. Preserve the hand edits and use targeted changes.
