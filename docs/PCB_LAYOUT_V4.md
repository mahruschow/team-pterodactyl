# Step 7 — draft v4 PCB layout

Prepared October 19, 2026. Working branch: `saadat-dev`. Status: **placed and first-pass autorouted; 6 supply connections and clean-up left for hand routing.** Not for fabrication.

Open `Native_KiCad_v4/PTERODACTYL_v4.kicad_pro` in KiCad 10 and switch to the PCB editor. A top-view render is in [v4-top.png](validation/2026-10-19/step7-pcb/v4-top.png). Both copper layers are in [v4-copper.pdf](validation/2026-10-19/step7-pcb/v4-copper.pdf), and an assembly drawing in [v4-assembly.pdf](validation/2026-10-19/step7-pcb/v4-assembly.pdf).

![Draft v4 board, top view](validation/2026-10-19/step7-pcb/v4-top.png)

## What the board contains

- **Outline:** the legacy 97.79 × 97.79 mm outline with rounded corners (copied from the v3.8 board, A1), and four M3 mounting holes at the legacy positions.
- **Layers:** 4 copper layers. In1.Cu and In2.Cu are solid GND planes, so every GND through-hole pad connects without tracks and all signals get a continuous return path (PC6, PC14). They are marked as power planes, with a rule area forbidding tracks, so routing cannot cut them; vias may pass through. F.Cu and B.Cu are for routing.
- **Parts:** all 49 footprints from the v4 schematic, with nets assigned from the KiCad-exported netlist. Every footprint carries the schematic's fields, and J4 is marked DNP. The board stays linked to the schematic, so *Update PCB from Schematic* works normally.
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
  - U5 (GPS) and U2 (regulator) have no verified footprints yet. Each is drawn as a labelled box on F.Fab/F.CrtYd with a rule area that keeps footprints, and on the outer layers tracks and vias, out (PC10). The inner GND planes continue underneath.
  - Their pads are missing, so their nets end short of them.

## Checks

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

1. Route the 6 open supply connections:
   - SENSOR_3V3 to C6, C8, C9, C10, C11, U4 VIN and TP4;
   - +5V to TP2 and C4.

   Consider moving the test-point row out of the Teensy fan-out area first.
2. Move TP1 (VBAT_PROT) and TP2 (+5V) next to the power section. Their autorouted stubs run across the board. They carry no load current, but they are unnecessary long traces.
3. Review every supply track against PC6 (return directly beneath, which the inner planes give) and PC7 (nothing near the BNO055). Also check the I2C daisy-chain order (PC11).
4. Tidy autorouter artefacts: odd angles, detours and unnecessary vias.
5. Then place silkscreen labels, add outer-layer GND pours and stitching vias, and rerun `tools/check_v4_pcb.py`.

Do not rerun `tools/build_v4_pcb.py` or `tools/autoroute_v4_pcb.py` once hand routing starts; both replace board content.

## What is not done yet

1. **Routing:** first pass done; finish and clean up per the list above.
2. **U2 and U5 footprints:** the regulator pinout check and M01 (GPS geometry).
3. **Track widths:** net classes are set (Power 0.5 mm). Confirm them against the manufacturer's rules and the measured currents.
4. **Silkscreen references:** currently on the assembly layer only (F.Fab). Place them on silkscreen during routing.
5. **Manufacturer rules (D08):** minimum track/space, drill sizes and stackup must be set once a fabricator is chosen.
6. **Outer-layer GND pours, stitching vias:** after routing.
7. **3D models for the module footprints:** cosmetic.
8. **Mechanical approval:** M01–M04 and the enclosure (R3, R6).
