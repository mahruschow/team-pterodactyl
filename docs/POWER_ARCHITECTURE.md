# Step 5 — power architecture and schematic change plan

Prepared October 19, 2026. Working branch: `saadat-dev`. Status: **draft v4 schematic implemented and checked; ready for team review.** The imported v3.8 schematic and PCB are unchanged. No v4 PCB exists yet (Step 7).

## Legacy power design (read-only review)

Traced from the exported v3.8 netlist (`validation/2026-10-18/schematic-netlist.xml`):

- **Path A:** 9 V plug (U$8) → slide switch (U$7) → 3-pin 5 V regulator module (U$5) → `VCC` → Teensy VIN.
- **Path B:** 8-position block (U$4) `3V7` → PowerBoost module (U$28) → `+5V` → slide switch (U$6) → `VCC` → Teensy VIN.
- **Monitor:** 4.7 kΩ/1 kΩ divider from `VCC` to Teensy pin 26 (A12).
- **Status LEDs:** D1–D4 on pins 2–5.
- **Inputs:** switch on pin 30, button on pin 31, pull-before-flight jumper on pin 32 (each to GND).
- **Thermistor:** on A16 with a 10 kΩ resistor.

| ID | Finding | Consequence | Proposed fix |
| --- | --- | --- | --- |
| F1 | Both regulator outputs connect straight to `VCC` through switches, with no OR-ing. | Turning both switches on joins two regulator outputs. | One input path only. |
| F2 | Nothing separates Teensy VIN from USB power. PJRC: "power should not be applied to VIN while a USB cable is used." | Plugging in USB while the battery is on can back-feed the PC or the regulator. | Cut the VUSB/VIN pads on the Teensy (PJRC-documented); see below. |
| F3 | D1–D4 connect pin → LED → GND with **no series resistor** in the schematic. | Pin current is limited only by the pin driver, above PJRC's 4 mA recommended maximum. Unless resistor-type LEDs were used, this stresses the pins. | Add a series resistor per LED. |
| F4 | The voltage divider measures regulated `VCC` (≈5 V), not the battery. | It cannot report battery state of charge until the regulator drops out. | Measure the protected battery input instead. |
| F5 | No fuse, reverse-polarity protection or input bulk capacitance is visible. | A reversed or shorted battery has no protection. | Add a PTC fuse, reverse protection and bulk capacitors. |
| F6 | The pin 41/A17 net goes to the U$4 block with a 10 kΩ resistor to AGND; its purpose is undocumented. | Unknown function. | Not carried forward unless someone identifies it. |

## Requirements this design must meet

- **Teensy 4.1:** 5 V on VIN when USB is not used. Pins and analog inputs are **not 5 V tolerant**. Recommended maximum is 4 mA per pin and 250 mA of external 3.3 V draw. Source: [PJRC Teensy 4.1](https://www.pjrc.com/store/teensy41.html).
- **Sensor breakouts (BNO055, MS8607, GPS):** powered at 3.3 V on VIN (SENSOR_CONNECTION_MAP.md). Their host-side pull-ups and logic levels follow VIN, so a 5 V VIN would put 5 V on Teensy pins.
- **Battery:** unknown (D02). The design should accept any likely choice without a redesign.

## Planning load budget

These are estimates for sizing, not measurements. Confirm them with T5 on the prototype.

| Load | Rail | Typical | Peak (assumed) | Source / note |
| --- | --- | ---: | ---: | --- |
| Teensy 4.1 core at 600 MHz | 5 V | 100 mA | 100 mA | Workbook |
| microSD writes | Teensy 3.3 V | 20 mA average | 100 mA | Assumed; card-dependent |
| BNO055 breakout | SENSOR_3V3 | 15 mA | 15 mA | Workbook |
| MS8607 breakout | SENSOR_3V3 | 5 mA | 5 mA | Workbook |
| PA1616D breakout | SENSOR_3V3 | 29 mA | 34 mA | Product page (acquisition) |
| 4 status LEDs | 3.3 V pins | 4 mA | 6 mA | 680 Ω series resistors; about 1.9 mA each when on |
| **3.3 V external total** | via Teensy regulator | **≈73 mA** | **≈160 mA** | Under the 250 mA recommendation |
| **5 V total** | | **≈175 mA (0.9 W)** | **≈260 mA (1.3 W)** | The Teensy regulator is linear, so 3.3 V current also flows at 5 V |

At an assumed 85 % converter efficiency, battery draw is about 1.0 W typical. That is about 3 Wh for the workbook's 3 hours, or 4 Wh for the 4-hour bench scenario, before cold derating and reserve. The workbook's 0.678 W excluded SD and conversion losses.

## Proposed architecture

```text
Battery ─ J1 ─ PTC fuse ─ reverse-protection P-MOSFET ─ J2 off-board panel switch ─┬─ battery-sense divider ─ RC ─ Teensy A12 (pin 26)
                                                                             └─ 5 V buck-boost (2–16 V in) ─ 5V ─ bulk caps ─ Teensy VIN
Teensy 3.3 V out ─ ferrite bead + 10 µF ─ SENSOR_3V3 ─ BNO055 / MS8607 / GPS VIN (10 µF + 100 nF each)
Teensy VUSB/VIN pads cut on the module; USB is for data/programming only
```

| Block | Proposal | Why |
| --- | --- | --- |
| 5 V regulator | Pololu S9V11F5 module (5 V step-up/step-down, 2–16 V input, 1.5 A when input ≥ output, < 0.2 mA quiescent, 2.54 mm pins, no reverse protection). [Product page](https://www.pololu.com/product/2836) | One part covers a 1S LiPo (3.0–4.2 V), 4 × lithium AA (about 4–7.2 V), 2S packs and 9 V. The battery choice (D02) then does not change the board. Like the legacy design, it is a through-hole module, so it is hand-assemblable. Pinout and footprint must be verified before the footprint is drawn (same rule as M01). |
| Sensor 3.3 V | Teensy 3.3 V output through a ferrite bead | One 3.3 V source, so the sensors cannot back-power Teensy pins through I2C/UART during power-up. Load is well under 250 mA. A dedicated LDO is only needed if T5 or T3 shows noise problems; a DNP footprint can be added. |
| Reverse protection | P-MOSFET in the high side (low drop) | A Schottky diode would waste about 0.3–0.4 V, which matters for a 1S cell. |
| Fuse | PTC resettable, about 0.75–1 A hold | Above the 260 mA peak and regulator startup current; protects wiring. |
| Main switch | Off-board panel switch on a 2-pin connector (J2), rated ≥ 1 A DC, after protection | Replaces the two legacy switches (F1). The small THT slide switches in KiCad's library are rated around 100 mA, below the regulator's ~0.7 A startup current. Switch position then follows the enclosure (D06). |
| Battery sense | 100 kΩ / 22 kΩ divider + 100 nF at the ADC, after the switch | 16 V → 2.89 V and 4.2 V → 0.76 V, inside the 3.3 V ADC range. About 0.13 mA at 16 V, and zero when switched off. |
| USB | Cut the VUSB/VIN pads (PJRC-documented) | Prevents back-feeding (F2). For programming, power the board from battery or a bench supply as usual, with USB connected for data. |
| Decoupling | 47 µF at regulator input, 47–100 µF + 100 nF at Teensy VIN, 10 µF + 100 nF per breakout | SD write and GPS acquisition surges; check with T5. |
| Status LEDs | Keep pins 2–5. Use red, yellow, low-Vf green and orange LEDs, each with a 680 Ω series resistor | Fixes F3: about 1.9 mA at Vf ≈ 2 V. The legacy white and blue LEDs (Vf ≈ 3 V) would get only about 0.3 V of headroom from a 3.3 V pin and barely light. |
| Test points | VBAT_PROT, 5V, 3V3, SENSOR_3V3, GND, SDA, SCL, GPS_TX, GPS_RX | Bring-up and T5/T6 measurements. |

Low-voltage cutoff: the S9V11F5 EN pin (100 kΩ pull-up, about 0.7 V threshold) can implement a hard cutoff with a divider. Leave this DNP until the battery is chosen; firmware can log low battery from A12 regardless.

## Schematic change list

| Legacy part | Action |
| --- | --- |
| U$17 BNO055 (QT footprint) | Replace with `Pterodactyl_Modules:Adafruit_BNO055_2472` |
| U$11 MS5611 | Replace with `Adafruit_MS8607_4716` |
| U$12, U$13, U$15, U$22 u-blox, U$29 MIKROE click | Replace with `Adafruit_PA1616D_5440_Logical` (footprint pending M01) |
| U$14 XBee | Remove (D05: no telemetry) |
| U$9 OLED, U$10 LSM9DS1, U$16 thermistor + R1, U$23/U$27 servos | Remove (D01 exclusions) |
| U$3 Teensy (TEENSY41_SIMPLE) | Replace with `Pterodactyl_v4:Teensy41_Carrier` (same pins, corrected power pin types); assign `Teensy41_SSW_Carrier` |
| U$5, U$7, U$8, U$6, U$28, U$4 legacy power | Replace with the architecture above |
| VR 4.7 kΩ/1 kΩ divider | Replace with battery-sense divider |
| D1–D4 LEDs | Keep; add series resistors |
| U$24 PBF, U$25 button, U$26 switch | Keep as optional inputs on pins 32/31/30 until D10 is decided |
| U$1 female headers, U$2 terminal block (Teensy pin expansion) | **Decision needed** — not in the Step 4 floor plan; they occupy about 82 mm of board edge each |
| Legacy net names | Rename to the Step 3 map: SENSOR_3V3, I2C0_SDA/SCL (pins 18/19), GPS_TX/RX (pins 7/8); resolve the A3V3/AGND/GND_1 labels as single 3V3/GND |

## Decisions (Saadat, October 19)

1. **Battery-agnostic 5 V buck-boost module:** accepted. Step 5 proceeds before the lead picks a battery; the battery choice only sets J1's connector and the fuse/capacitor ratings.
2. **Teensy expansion headers U$1/U$2:** dropped for v1. They are replaced by J4, an 8-pin spare-I/O header (3.3 V, GND, pins 0/1/14/15/16/17), DNP by default.
3. **Schematic approach:** a new clean v4 schematic. The imported v3.8 project is kept unchanged as reference.

## v4 schematic implementation

Open `Native_KiCad_v4/PTERODACTYL_v4.kicad_pro` in KiCad 10. It is a separate project; its library tables point at the shared `Native_KiCad_v11/Pterodactyl_Modules` libraries and at KiCad 10's standard libraries through `${KICAD10_SYMBOL_DIR}`/`${KICAD10_FOOTPRINT_DIR}`. This means it opens even where KiCad's global library table has not been set up.

- **Generated, not hand-drawn.** `tools/generate_v4_schematic.py` holds the part-by-part connection table and writes the schematic. Connections are made by net labels, power symbols and explicit no-connect flags at every pin, so each connection is visible and reviewable. Wires can be drawn in the editor later for presentation. If the schematic is edited by hand, stop regenerating it, or the hand edits are overwritten.
- **New symbols** in `Native_KiCad_v4/Pterodactyl_v4.kicad_sym`:
  - `Pololu_S9V11F5_Logical`: named pins VIN/VOUT/GND/EN, no footprint until the module's pinout is verified (same rule as the GPS).
  - `Teensy41_Carrier`: the imported Teensy graphics and pin positions with corrected electrical types. VIN and GND are power inputs and 3.3V_1 is a power output. 3.3V_2 is passive, because it is the same onboard regulator output and two outputs on one net is an ERC conflict.
- **Pin assignments added in Step 5:**
  - Status LEDs on pins 2–5 (STATUS1–4).
  - IMU_RST on pin 9 to the BNO055 RST pin, for I2C lock-up recovery. This was the open Step 3 item.
  - VBAT_SENSE on pin 26.
  - Mode switch, user button and pull-before-flight on pins 30/31/32, kept as optional inputs while D10 is open.
  - Spare pins 0/1/14–17 on J4.
- **Test points TP1–TP10:** VBAT_PROT, +5V, +3V3, SENSOR_3V3, GND, I2C_SDA, I2C_SCL, GPS_TXD, GPS_RXD, VBAT_SENSE.
- **Mounting holes H1–H4:** M3, matching the legacy outline. Positions come in Step 7.

### Verification

`tools/verify_v4_schematic.py` (ordinary Python 3, uses kicad-cli) does the following:
- Runs native ERC at all severities. Result: **0 violations**.
- Exports the KiCad netlist and compares it with a separately written, net-by-net expected list taken from this document and SENSOR_CONNECTION_MAP.md. Result: **all 32 nets and all 36 intentional no-connects match**, each no-connect with a stated reason.
- Checks that every part except U2 and U5 has a footprint.
- Exports the BOM and a PDF.

Evidence: [schematic-check.json](validation/2026-10-19/step5-schematic/schematic-check.json), [erc.json](validation/2026-10-19/step5-schematic/erc.json), [netlist.xml](validation/2026-10-19/step5-schematic/netlist.xml), [bom.csv](validation/2026-10-19/step5-schematic/bom.csv), [PDF](validation/2026-10-19/step5-schematic/PTERODACTYL_v4.pdf).

This proves the file wires what the documents say. It does not prove that the documents are right, that candidate parts meet their ratings, or that the circuit works.

### BOM status

Part numbers marked "(candidate)" need datasheet confirmation before ordering. In particular, check:
- The PTC voltage rating against the maximum battery voltage.
- Q1's Vds and Vgs ratings against the 10 V zener clamp.
- The ferrite bead's current rating.
- The J1/J2 connector type against the chosen battery and switch.

The module sockets and headers (Samtec SSW/HTSW, listed in MODULE_ASSEMBLY_PLAN.md) and the spacers/fasteners are not yet BOM lines. Add them once M03 is approved.

## Remaining before Step 5 sign-off

- [ ] Team review of the architecture and schematic (this document plus the PDF).
- [ ] Verify the S9V11F5 pinout and dimensions, then create its footprint (it has none yet).
- [ ] Confirm candidate part ratings (BOM status above).
- [ ] D02 battery: confirm J1 connector, fuse rating and C1 voltage rating.
- [ ] D10 controls: confirm or remove SW1/SW2/J3.
- [ ] GPS footprint after M01.

Step 6 (firmware) can start using the net names and pins above. Step 7 (PCB layout) needs the two missing footprints and the Step 4 review.

For the lead, independent of the above: lithium AA primaries (for example 4 × AA) tolerate cold much better than LiPo or alkaline 9 V cells. Alkaline 9 V capacity falls sharply at this design's ~200 mA draw. This is context for D02, not a decision.
