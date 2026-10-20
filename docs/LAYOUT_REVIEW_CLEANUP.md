# Layout review and cleanup — October 19, 2026

Reviewed the v4 carrier after `46f926a`. Fixed the remote ADC filter placement, corrected the I2C routing order, and replaced overlapping assembly labels with readable silkscreen references and a test-point key. **Fresh enabled physical DRC: 0 violations; unconnected items: 0 for the 50 placed footprints. U5/GPS remains missing.** This is a reviewed draft, not fabrication approval.

## Findings and changes

| Finding | Change / result |
| --- | --- |
| C2 was about 65 mm from Teensy pin 26, despite PC13 calling for the ADC capacitor at the input. | Moved C2 beside the carrier pin: 4.493 mm pad-centre separation, with a short connection. This does not measure the Teensy's internal route to the MCU. |
| I2C followed Teensy → BNO055 → MS8607 rather than the PC11 plan. A total-length-only check missed this. | Rerouted the host leg to MS8607, retaining the existing MS8607–BNO055 connections. Graph checks now verify the intended order for both nets. |
| Crowded test points and traces obstructed the ADC capacitor location. | Moved TP3 slightly upward and TP5 into a clear probe area. Locally adjusted +3V3 and BTN_USER routes to maintain clearances. Removed the old C2 branch beside the power section. |
| I2C's revised host route changes between outer layers. | Added four signal vias and three nearby GND stitching vias. Each new GND via is connected to both inner GND fills. |
| Component values and test-point names overlapped in the assembly view; references were not on silkscreen. | Moved component references to F.Silkscreen, hid redundant value fields, and added module/control names, battery polarity marks and a separate TP6–TP10 key. Values remain stored in the board/schematic/BOM. |

The ADC change follows the existing PC13 intent and general [NXP analog-input layout guidance](https://www.nxp.com/docs/en/application-note/AN2105.pdf): terminate an analog input route with capacitance near the input. Component values and circuit topology are unchanged; ADC settling, accuracy and noise still require bench measurements.

C2's new placement is intentionally excluded from the *power-section* spacing group in `check_v4_pcb.py`. It is a high-impedance ADC shunt capacitor, not a switching converter or load-current source. A separate ≤5 mm carrier-pin proximity check now covers it. This clarifies the implementation of PC13; it does not reduce the 40 mm BNO-to-power target or move the converter closer to the sensors. Existing power-source separations remain unchanged.

## Validation

Run with KiCad Python from the repository root:

```powershell
& 'C:\Program Files\KiCad\10.0\bin\python.exe' -B tools/verify_v4_layout.py
```

This reads the board without regenerating or saving it. It runs native refilled DRC/parity, checks present-footprint connectivity, traces the I2C copper graph, checks capacitor proximity, measures the actual module separation geometry, checks track widths/inner-plane routing and verifies the new GND vias connect to both fills.

| Check | Result |
| --- | --- |
| Enabled physical DRC / present-footprint unconnected items | 0 / 0 |
| Schematic parity | Only missing U5 |
| I2C copper lengths | SDA 135.163 mm; SCL 128.209 mm; both below proposed 150 mm maximum |
| I2C topology | Both host-to-IMU paths pass through the MS8607 pad |
| Negative regression against `46f926a` | Both old paths are connected but fail the intended device-order check |
| C2 signal pad → U1 pin 26 centre distance | 4.493 mm; ≤5 mm carrier-layout target |
| Placement | 47 footprints unchanged; only C2, TP3 and TP5 moved |
| Existing tracks/vias | 220 objects preserved exactly; 14 removed and 30 added on documented nets |
| Current routing | 233 segments / 17 vias; 1389.2 mm total track length |
| New return stitching | 3 GND vias, connected to both inner planes |
| Power widths / seven separation checks | Pass |
| Tracks on inner GND layers / GPS envelope intrusion | None |
| Schematic, symbols, project design rules, outline, stackup and zone boundaries | Unchanged |

Evidence: [layout checks](validation/2026-10-19/layout-review/layout-check.json), [DRC including ignored-check list](validation/2026-10-19/layout-review/drc.json), [preservation audit](validation/2026-10-19/layout-review/preservation-check.json), [changed object IDs](validation/2026-10-19/layout-review/changed-objects.json).

Review views: [outer copper and silkscreen](validation/2026-10-19/layout-review/copper.svg), [silkscreen only](validation/2026-10-19/layout-review/silkscreen.svg), [inner GND fills](validation/2026-10-19/layout-review/ground-planes.svg). The combined copper view was visually inspected. Native clearance checks cover the final silkscreen geometry. Module-body overlays remain on F.Fab/F.Courtyard for mechanical review.

## Ground and remaining review decisions

- Retain the two solid inner GND planes and the no-inner-tracks rule. Add local ground connections at the new layer transitions; defer optional outer GND pours until GPS geometry/routing is settled. Final stackup and measured return/noise performance remain unverified.
- Preserve unrelated signal/power routes. The I2C order correction adds length and vias but meets the existing 150 mm draft target. Pair spacing is not uniform through every connector escape; start at the documented 100 kHz and measure rise time/error rate before considering 400 kHz.
- The carrier's C1 and C4 remain roughly 20 mm from regulator VIN and 13 mm from Teensy VIN respectively. They supplement module-local capacitance, but proximity and transient behavior still need review against the installed modules and the T5 startup/load test. This pass does not certify the entire power-integrity design.
- Labels use the existing project constraints; final silkscreen stroke/height, drill rules and stackup must meet the selected manufacturer's capabilities. Module sockets, retention and access require a physical fit check.
- GPS M01 still blocks U5 assignment and routing. The absence of U5 means zero unconnected items is not complete schematic implementation.
- Firmware reliability findings, battery/enclosure decisions, final independent team review and prototype EMI/thermal/load tests remain open. No firmware changes or hardware measurements were made in this pass.

Do not rerun the full PCB/schematic generators or whole-board autorouter over these edits. Use targeted changes and fresh checks.
