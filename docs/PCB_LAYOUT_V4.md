# Step 7 — draft v4 PCB layout

Prepared October 19, 2026. Working branch: `saadat-dev`. Status: **all currently placed footprints routed; GPS footprint/wiring and final layout review remain.** Not for fabrication.

Open `Native_KiCad_v4/PTERODACTYL_v4.kicad_pro` in KiCad 10 and switch to the PCB editor. A top-view render is in [v4-top.png](validation/2026-10-19/step7-pcb/v4-top.png). Both copper layers are in [v4-copper.pdf](validation/2026-10-19/step7-pcb/v4-copper.pdf), and an assembly drawing in [v4-assembly.pdf](validation/2026-10-19/step7-pcb/v4-assembly.pdf).

![Draft v4 board, top view](validation/2026-10-19/step7-pcb/v4-top.png)

## Current routing update

**Latest routing checkpoint:** [POWER_ROUTING.md](POWER_ROUTING.md). All connections among the 50 placed footprints are now routed: 0 enabled physical DRC violations, 0 unconnected items, and only U5/GPS missing in schematic parity. U5 is still absent, so this does not mean all schematic connections are implemented. TP1/TP2/TP4 were moved near their rails; a 68.667 mm unloaded TP1 spur was removed. No new vias; original signal routes and design rules are preserved. GPS geometry, layout/assembly review and fabrication gates remain open.

## Previous footprint checkpoint

U2 now has a three-pin regulator footprint, increasing the main board to 50 footprints. U5 remains an unassigned GPS envelope; its separate legacy comparison footprint is explicitly unverified. Fresh checks: 0 enabled physical DRC violations, only U5 missing in parity, 12 unconnected items including the newly exposed regulator VIN/VOUT. Existing 192 track segments, 10 vias and all 49 prior footprint positions/pads/nets are preserved. See [REGULATOR_GPS_FOOTPRINTS.md](REGULATOR_GPS_FOOTPRINTS.md). Earlier autoroute metrics below describe the pre-integration checkpoint.

## What the board contains

- **Outline:** the legacy 97.79 × 97.79 mm outline with rounded corners (copied from the v3.8 board, A1), and four M3 mounting holes at the legacy positions.
- **Layers:** 4 copper layers. In1.Cu and In2.Cu are solid GND planes, so every GND through-hole pad connects without tracks and all signals get a continuous return path (PC6, PC14). They are marked as power planes, with a rule area forbidding tracks, so routing cannot cut them; vias may pass through. F.Cu and B.Cu are for routing.
- **Parts:** 50 assigned footprints from the v4 schematic, with nets assigned from the KiCad-exported netlist. Every footprint carries the schematic's fields, and J4 is marked DNP. The board stays linked to the schematic, so *Update PCB from Schematic* works normally.
- **Placement** follows the Step 4 floor plan:
  - BNO055 top-left, MS8607 top-centre, GPS envelope top-right.
  - Teensy along the bottom-left (microSD at the left edge, USB/VIN end toward the power section).
  - Power section in the bottom-right corner, with the battery and switch connectors on the right edge.
  - Middle band: status LEDs, user controls, the spare header and test points.
  - Sensor decoupling capacitors sit next to each module's VIN pin.
- **Net classes** (set in the project file by `tools/generate_v4_schematic.py`):
  - Default: 0.25 mm tracks, 0.2 mm clearance.
  - Power: 0.5 mm / 0.25 mm, for VBAT_IN, VBAT_FUSED, VBAT_PROT, VBAT_SW and +5V (about 0.7 A regulator startup).
  - Supply3V3: 0.3 mm / 0.2 mm, for +3V3 and SENSOR_3V3 (about 160 mA peak). This is narrow enough to pass between 2.54 mm pads.
- **Envelopes:**
  - U5 (GPS) has no revision-verified footprint yet. It is drawn as a labelled box on F.Fab/F.CrtYd with a rule area that keeps footprints, and on the outer layers tracks and vias, out (PC10). The inner GND planes continue underneath.
  - GPS pads are missing; U2 now has actual VIN/GND/VOUT pads, with VIN/VOUT still needing routing.

## Historical pre-routing checks

`tools/check_v4_pcb.py` runs native DRC with schematic parity and re-measures the Step 4 separations on the actual placement:

| Check | Result |
| --- | --- |
| DRC violations (all severities) | **0** |
| Schematic parity | Only the 2 expected missing footprints (U2, U5) |
| Unconnected items | 57, expected because nothing is routed yet |
| PC1 BNO055 ↔ power section ≥ 40 mm | 44.4 mm |
| PC2 BNO055 ↔ Teensy ≥ 25 mm | 35.1 mm |
| PC3 BNO055 ↔ GPS ≥ 20 mm | 30.7 mm |
| PC4 GPS ↔ Teensy / power ≥ 20 mm | 30.2 mm / 20.7 mm |
| PC5 MS8607 ↔ Teensy / power ≥ 25 mm | 42.6 mm / 33.8 mm |

Evidence: [pcb-check.json](validation/2026-10-19/step7-pcb/pcb-check.json), [drc.json](validation/2026-10-19/step7-pcb/drc.json).

## How the board is made

`tools/build_v4_pcb.py` (KiCad Python) creates the board from the schematic netlist and a placement table. **It overwrites the board**, so it is only for the pre-routing stage. Once routing or hand edits start, edit the board in KiCad, and use *Update PCB from Schematic* for schematic changes.

## Autorouting (October 19)

`tools/autoroute_v4_pcb.py` exports a router-only copy of the board to Specctra DSN, runs Freerouting, imports the session and refills the planes. Freerouting's analytics are disabled. Attempts:

1. **Freerouting 2.5.0 Windows CLI build:** it crashed on start-up (`UnsupportedFeatureError ... ComponentOutline`, a packaging bug in that native build). The board was unchanged.
2. **Portable `freerouting-2.5.0.jar` on an Eclipse Temurin JRE 25.0.4.1 zip** (both SHA-256 verified; neither is installed or committed): everything routed, but it ran tracks on the inner GND planes. Fixed by marking In1/In2 as power planes with a no-tracks rule area.
3. With that rule area, Freerouting refused vias, and the Teensy's "no parts underneath" rule area was exported as a full keep-out over its own pins. Fixed in the router-only copy:
   - the inner no-tracks area and the Teensy's parts-only area are shrunk to nothing;
   - board-edge keep-out strips are added, because Freerouting ignores KiCad's 0.5 mm edge clearance;
   - automatic neck-down is turned off, because it had produced 0.187 mm tracks.

   The saved board keeps all its rules, and `check_v4_pcb.py` rejects any track on the inner layers.
4. Added the Supply3V3 class so the 3.3 V rails fit between pads.

**Result of the current first pass:**

| Item | Result |
| --- | --- |
| Tracks / vias | 192 segments (1250 mm) on F.Cu and B.Cu only; 10 vias |
| DRC | **0 violations** |
| Schematic parity | Only U2/U5 missing (expected) |
| Unrouted | **10 unconnected items: 6 connections on SENSOR_3V3 and +5V** |
| I2C longest (PC11 ≤ 150 mm) | 110.5 mm |
| Power / 3.3 V track widths | All at class width |
| Tracks in GPS/regulator envelopes, or on the inner planes | None |

Freerouting oscillated between 6 and 10 unrouted on every pass. The bottleneck is the test-point row directly above the Teensy, which nearly every Teensy signal has to cross, so more passes will not help. Log: [freerouting.log](validation/2026-10-19/step7-pcb/freerouting.log).

### Clean-up list for hand routing

1. **Done for present footprints:** regulator VIN/VOUT, +5V, SENSOR_3V3 and their test-point/decoupling connections. TP1/TP2 are now in the power area and TP4 beside the sensor rail; the long TP1 spur was removed. See POWER_ROUTING.md.
2. Confirm current GPS #5440 geometry, assign U5, then route and check its connections. Do not interpret today's zero-unconnected result as GPS completion.
3. Review the full layout against PC6/PC7/PC11, including the existing I2C topology, return paths and ADC filter placement. Targeted new power routes passed DRC and the In2 GND plot was visually reviewed; prototype interference/load testing remains necessary.
4. Tidy remaining autorouter detours and place readable silkscreen labels. Evaluate outer GND pours/stitching after GPS integration and final route review.
5. Apply the selected manufacturer's rules/stackup, refill zones and rerun DRC/parity before review sign-off.

Do not rerun `tools/build_v4_pcb.py` or `tools/autoroute_v4_pcb.py`; both replace board content.

## What is not done yet

1. **Routing:** all present footprints connected; GPS connections and final review/cleanup remain.
2. **U5 footprint:** close M01 (current GPS geometry) before assignment; U2 is now integrated, with physical fit/retention still pending.
3. **Track widths:** net classes are set (Power 0.5 mm). Confirm them against the manufacturer's rules and the measured currents.
4. **Silkscreen references:** currently on the assembly layer only (F.Fab). Place them on silkscreen during routing.
5. **Manufacturer rules (D08):** minimum track/space, drill sizes and stackup must be set once a fabricator is chosen.
6. **Outer-layer GND pours, stitching vias:** after routing.
7. **3D models for the module footprints:** cosmetic.
8. **Mechanical approval:** M01–M04 and the enclosure (R3, R6).
