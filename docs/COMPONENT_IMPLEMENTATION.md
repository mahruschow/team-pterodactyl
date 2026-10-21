# Component implementation and review — October 21, 2026

## Team-name silkscreen update — October 21, 2026

Saadat Muyeen, Mahrus Chowdhury and Ryeed Zaman are now on the back silkscreen, with 2 mm text and 0.30 mm strokes. Fresh DRC, connectivity and schematic-parity checks report zero issues. All original PCB bytes are retained; only three text objects were added. The other eight Gerber layers match the prior geometry exactly, apart from export timestamps. Existing ERC evidence remains applicable to the unchanged schematic.

**Order the updated native PCB or fabrication ZIP. AISLER TCVOYNZG revision 1 is superseded and does not contain the names.** Two revision-upload attempts failed; the alternate upload form says an anonymous project is already in progress and requires login to save it. Sign in and upload the updated board, then inspect the bottom preview before ordering. No new AISLER revision or order has been created. Earlier statements below about revision 1 being the exact current PCB or ready for checkout refer to the previous checkpoint.

## First prototype scope and order checkpoint - October 21, 2026

**Current authority: [FIRST_PROTOTYPE_RELEASE.md](FIRST_PROTOTYPE_RELEASE.md).** PCB checks and AISLER upload/preview passed; project TCVOYNZG revision 1 is ready for checkout. FB1/SW1/SW2/J3 are selected for P1. The user explicitly excludes physical testing, flight qualification, subsequent redesign and casing from this phase; older statements requiring those before PCB fabrication are superseded. Assembly receipt/polarity checks remain part of building the prototype. No order placed. Updated known cost is USD 129.37 (15 price lines missing); entered mass 170.25 g (three missing). The provisional EUR board quote is separate.

**Targeted prototype changes are applied to Native_KiCad_v4. Not released for manufacture or flight.** This document supersedes the research-only boundary in COMPONENT_FINALIZATION_RESEARCH.md. Nothing was purchased, committed or pushed. Firmware was not changed.

## Native changes

| References | Applied selection / change |
| --- | --- |
| J1, J2 | Molex 0022272021 KK254 headers, replacing the -25 C JST-XH candidates. Local footprint uses 2.54 mm pitch, 1.19 mm drill and 1.90 x 2.19 mm pads for AISLER annulus. |
| C1, C3 | Panasonic EEUFR1E101, 100 uF 25 V. C1 was 47 uF; C3 was rated 10 V. Nominal body D6.3 x H11.2 mm, 2.5 mm pitch. Removed inaccurate inherited 7 mm-high 3-D model. Sleeve/body tolerances and fit still require confirmation. |
| C2/C4/C7/C9/C11 | KEMET C322C104K5R5TA, 100 nF 50 V X7R. Local body envelope 5.08 x 3.18 mm, maximum height 6.6 mm. |
| C5/C6/C8/C10 | KEMET C322C106K3R5TA, 10 uF 25 V X7R. Local body envelope 5.08 x 4.07 mm, maximum height 6.6 mm. Effective capacitance at bias/cold is unmeasured. |
| Q1 | AO3401A, G1/S2/D3, source VBAT_PROT and drain VBAT_FUSED retained. Local SOT-23 silk omits the two bottom strokes that conflict with an exposed via. Copper and pin numbering unchanged. |
| R1/R2 | MRS16000C1003FCT00, 100 kohm |
| R3 | MRS16000C2202FCT00, 22 kohm |
| R4–R7 | MRS16000C6800FCT00, 680 ohm |
| D1 / F1 | BZX79-C10,133 / MF-RHT070-0 |
| D2–D5 | WP7113LID / WP7113LYD / WP7113LGD / WP7113LSECK/J4 |
| FB1 | BL01RN1A2A2B marked **candidate rejected: obsolete, replacement required** |
| SW1 | OS102011MS2QN1 entered as a **candidate**, drawing/low-current contact check open |
| SW2 | Y97HT21A1FAFP (PTS645SL50-2 LFS alias) entered as a **candidate**, drawing/order-table ambiguity open |
| J3 | HTSW-102-07-T-S entered as a **candidate**, mating shunt/fit and operational role open |
| J4 / TP1–TP10 | J4 remains DNP. Test points explicitly bare plated pads, no purchased test-pin hardware. |

The resistor choice changed from the research proposal: **MRS25 needs at least 10 mm formed lead pitch**, which does not fit the existing 7.62 mm pattern. MRS16 needs at least 5 mm, so its maximum 3.6 x 1.6 mm body fits. Seven published 0.125 g resistor masses total 0.875 g, already included in the passive-lot allowance. Recheck lifecycle and stock before purchase. [Vishay drawing](https://www.vishay.com/docs/28724/mrs16m25.pdf).

Exact codes, sources and selection-status fields are in `tools/component_selections.py` and the native schematic/PCB. The current **47-reference BOM has zero blank MPN fields**, but includes four explicitly unresolved candidates, ten pad-only entries and DNP J4. Five module identities remain unchanged. A filled MPN column is not a released BOM.

## Preserved layout and necessary local movement

The approximately 98 x 98 mm outline, all module positions, zone boundaries, net assignments and every original footprint/pad/segment/via UUID are retained. There are still **51 footprints, 246 track segments and 25 vias**. Eight segments have endpoint changes; no tracks or vias were added or removed.

| Item | Targeted change |
| --- | --- |
| J1/J2 pad 2 | 2.50 to 2.54 mm pitch, hence -0.04 mm board Y at the retained 90-degree orientation; attached endpoints follow |
| C2 | Y -0.30 mm; carrier ADC pin gap now 4.793 mm, under the 5 mm target |
| C6 | Y +0.20 mm |
| C8 | Y +0.15 mm |
| TP4 | Y +1.00 mm |
| J2 nearby route | Small VBAT_SW corner adjustment to clear larger pad 1 |
| BTN_USER route near C2 | Two nearby junctions moved to Y118.45 mm to clear the actual capacitor body/pads |
| Silkscreen | Stroke/text thickness raised to 0.15 mm where needed; local labels moved and Q1 silk clipped to avoid exposed via opening |

Original pre-edit native files are saved locally in `work/component-finalization-baseline/`. The comparison is against that checkpoint, **not** against HEAD (which predates substantial user work). PCB baseline SHA-256: `dde1328daaae48dd68cea94614225affd30146d519a74f4dc4634c406fde1c2c`.

## Battery, connector and module assembly

Prototype battery selection is **four Energizer L91 AA primary lithium cells in series, nominal 6 V, in MPD BH4AAW**. This is a holder candidate with a suitable published rating, not a finished qualified pack. Do not confuse BH4AAW with BA4AAW, whose -10 C rating was rejected. Do not charge or directly solder bare cells.

The BH4AAW manufacturer drawing specifies nylon 66, nickel-plated 302 stainless springs, **-40 to +140 C**, a **61.72 x 57.15 x 15.88 mm** holder body, approximately **15.05 g**, and 152.4 +/-5 mm, 24 AWG leads. Four L91 cells add 60 g, for **75.05 g cells + wired-holder estimate**. This is not the full installed envelope: allow cell/body variation, connector bends, strain relief, restraint and casing. Lead marking UL1007/TR64 80 C does not independently establish acceptable bending/insulation behavior at -40 C. Check insulation diameter against the crimp, keep leads supported and test the actual assembly. The steel springs also require separation/interference testing relative to the BNO055 magnetometer. [MPD drawing](https://www.batteryholders.com/uploads/parts/BH4AAW/datasheets/BH4AAW-datasheet.pdf), [L91 sheet](https://data.energizer.com/pdfs/L91GL0225.pdf).

J1/J2 mating proposal: two **0022012027** housings and four **0008500113** contacts. Molex specifies 22–30 AWG and a maximum insulation diameter of 1.57 mm for that contact; wire gauge alone is insufficient for acceptance. Its KK specification covers the 6410 header / 2695 housing / 2759 terminal families at -40 to +80 C for brass. Header drawing uses 0.64 mm square pins and 1.19 +/-0.05 mm PCB holes. The local pad minor-axis annulus is 0.355 mm before fabrication tolerances. Harness continuity/polarity, pull test, approved crimp tooling and retention are open. **J2 carries the battery-switch loop; its second pin is not ground.** [Header](https://www.molex.com/en-us/products/part-detail/22272021), [housing](https://www.molex.com/en-us/products/part-detail/22012027), [contact](https://www.molex.com/en-us/products/part-detail/0008500113), [family specification](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/100/1007/PS-10-07-001.pdf).

Sensor soldered-header candidates are Samtec **HTSW-106-15-T-S** and **HTSW-104-15-T-S** for BNO055, **HTSW-105-15-T-S** for MS8607, and **HTSW-109-15-T-S** for GPS. Tin temperature rating is -55 to +105 C. The -15 style has nominal 18.54 mm overall length: 2.79 mm short tail, 2.54 mm insulator and 13.21 mm post. With the insulator on the carrier, a 1.6 mm carrier gives 1.19 mm short-tail protrusion. A hypothetical 12 mm carrier-to-module underside gap plus a 1.6 mm module gives about 2.15 mm upper protrusion. These are **nominal checks**, not an approved spacer stack or measured module thickness. The 0.635 mm square-pin diagonal is 0.898 mm; 1.04 mm nominal holes leave only 0.142 mm nominal diametral clearance before pin/drill tolerances. Check actual parts and finished holes before release. [Samtec drawing](https://suddendocs.samtec.com/catalog_english/tsw_th.pdf).

Teensy/regulator socket proposals remain as previously documented. No sensor sockets are reintroduced. Nonmagnetic spacers, screws, shunt, external power switch, pack restraint and complete harness remain to be selected. The board outline is preserved; the complete casing envelope remains unmeasured.

Storage is **Kingston SDCIT2/8GB**, -40 to +85 C, selected for the prototype budget/off-board BOM. No socket change is required; it is in the Teensy microSD slot. Public data does not supply a guaranteed write/inrush current maximum. The 30/200 mA planning values remain unverified. [Kingston sheet](https://www.kingston.com/datasheets/SDCIT2_en.pdf).

## Power-path findings and revised budget

AO3401A is limited to +/-12 V gate-source voltage. The design is restricted to the intended four-L91 pack, **not** a generic 16 V input merely because the regulator accepts it. The nominal 10 V zener operates at low gate-bias current and must not be treated as a precise high-energy clamp. [AO3401A sheet](https://www.aosmd.com/pdfs/datasheet/AO3401A.pdf).

MF-RHT070-0 hold current is 0.70 A at 23 C, 0.95 A at -40 C and 0.62 A at +40 C. Published R1max is 0.8 ohm after trip at 23 C; it is **not** a characterized cold resistance maximum. PTC hold is not an instantaneous trip threshold. Low-temperature fault current/time-to-trip, hot self-heating, startup and SD transients need testing. F1 is after J1 and does not protect a short in the leads before it; pack-side protection/physical insulation remain unresolved. [Bourns sheet](https://bourns.com/docs/product-datasheets/mf-rht.pdf?sfvrsn=9bedf0c3_50).

The updated live workbook and builder replace 97% path efficiency with a **provisional 90% allowance**, retain 85% conversion efficiency, 70% usable energy and 25% reserve, and use selected LEDs' mean typical Vf 1.8125 V at 2 mA. LED peak allowance is 3 mA per LED, not a guaranteed maximum. Four LEDs continuously on produce about 8.75 mA typical total through 680 ohm resistors.

| Planning result | Updated value |
| --- | --- |
| 5 V average / peak load | 1.23375 / 2.725 W |
| Battery average / peak input | 1.618301 / 3.567647 W |
| Three-hour modeled consumption | 4.854902 Wh |
| Nominal target with 25% reserve / 70% usable | 8.669468 Wh; 1.444911 Ah at 6 V |
| Cold usable energy including proposed reserve | At least 6.068627 Wh under actual load/cutoff, subject to measured load revision |
| Entered mass subtotal | 170.25 g, including allowances; three mass lines missing |
| Known price subtotal | $118.30; 16 cost lines missing; five module prices from October 20 |

Mass includes 75.05 g cells/holder, removes 1 g test-pin hardware and 1 g DNP J4 allowance. Missing mass lines are module interconnects, enclosure and integration. Harness/retention rows still contain allowances; avoid double-counting holder leads in the added-wire row. These are neither measured mass nor complete procurement totals.

An independent resistance screen uses 1 ohm total (0.8 PTC + 0.085 Q1 at -2.5 V gate/25 C + 0.115 wiring/contact allowance), and solves `Vpack*I = Pmodule + I^2*R`. At 6 / 4.8 / 4 V pack terminals the modeled peak currents are 0.594 / 0.803 / 1.112 A; regulator input becomes 5.406 / 3.997 / **2.888 V**. The 4 V case is below the regulator's 3 V startup requirement. This is a warning from an illustrative model, not a selected cutoff or a guarantee for the higher-voltage cases. Minimum terminal voltage stays blank in the budget until tested. Cell internal loss is already reflected by using loaded terminal voltage, not counted again in series path resistance.

## AISLER review

Target remains **4-layer, 1.6 mm, 35 um ENIG**. Project/custom rules now enforce component PTH annulus >=0.30 mm and drill 0.50–5.60 mm; via annulus >=0.10 mm and drill 0.25–0.45 mm; NPTH drill 0.50–5.60 mm; hole-to-hole >=0.30 mm; silk clearance >=0.125 mm; silk/text stroke >=0.15 mm. Existing stricter 0.20/0.25 mm net clearances, >=0.20 mm track width and 0.50 mm copper-edge gap remain. No new DRC exclusions were added. Existing nonphysical/library defaults that were ignored remain unchanged; see project severity map.

Via tenting is disabled to match the documented standard process. No plugging/filling promise is assumed. The official nominal stackup drawing shows 35 um copper layers, 2 x 70 um prepreg each side of a 1200 um core, approximately 1.62 mm before the manufacturer's finished-thickness tolerance convention. The native board remains 1.6 mm/four layers; **no fabricated impedance target or guessed detailed dielectric stack was entered**. Confirm the actual service stackup/finish and mask/ink processing in AISLER's upload preview before any order. KiCad DRC alone does not verify soldermask process, total silk coverage or supplier upload interpretation.

Sources checked October 21: [design rules](https://community.aisler.net/t/4-layer-35-m-enig-design-rules/3733), [stackup](https://community.aisler.net/t/4-layers-1-6mm-35-m-stackup/5457), [via treatment](https://community.aisler.net/t/via-plugging-filling-via-drill-vs-via-size/5522).

## Fresh saved evidence

Directory: `docs/validation/2026-10-21/component-finalization/`. Earlier GPS evidence was preserved.

- `erc.json`, `schematic-check.json`: zero ERC violations; 32 expected nets and 35 intentional no-connects match. Netlist has 51 components including four mounting holes; BOM has 47 reference rows.
- `drc.json`, `layout-check.json`: zero enabled violations, zero unconnected and zero parity issues after native saved zone refill. Both inner ground planes and six ground-via connections pass; I2C paths 135.163/128.209 mm.
- `preservation-check.json`: all original object identities/nets retained, outline/module placements/zone boundaries unchanged; bounded moves above.
- `bom.csv`: per-reference codes, selection status, sources, DNP and notes. `netlist.xml` and schematic PDF accompany it.
- `budget-check.json`: independent budget arithmetic, incomplete totals, and resistance-screen energy balances pass.
- `board-top-review.pdf`: visual copper/silkscreen review. Draft legend remains. This is review evidence, not a fabrication release.

### FB1 lifecycle finding after final source check

The BL01RN1 family is marked **EOL** in a Murata-authored presentation dated February 4, 2020, visually reviewed here. Its original reference specification confirms the proposed part’s 7 A rating, 20 milliohm maximum DCR, -40 to +85 C range and 10 +/-1 mm formed pitch, but that does not solve availability. FB1 is now explicitly rejected for new procurement in the schematic, PCB and BOM; geometry is retained pending a validated replacement. This closes the lifecycle uncertainty by identifying a replacement gate. Sources: [Murata EOL presentation, mirrored copy](https://285624.selcdn.ru/syms1/iblock/035/035d91d2fd3c7fc23f4a844cafed7b71/7c009e77a03a1be4e0c81a69e35476ba.pdf), [Murata reference specification](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/2316/BL01RN1A_Spec.pdf). Do not use an unreviewed SMD alternative or omit the bead silently.

## Remaining gates, in order

1. Resolve SW1 visual drawing/logic-level contact suitability and revision temperature discrepancy; SW2 contact pairs plus conflicting height/force ordering data; J3 shunt/finished-hole fit and role; FB1 replacement for the obsolete part. C&K/Littelfuse PDF downloads returned access errors/timeouts in this environment; searchable tables are not sufficient to close drawing gates. Do not substitute an unrelated switch silently.
2. Complete harness/protection and external power-switch choice, crimp tooling/insulation match, nonmagnetic retention hardware and exact module spacer stack. Check capacitor sleeve/height tolerances and all module overhangs, actual GPS holder, SD/USB access and solder tails by physical fit.
3. Confirm AISLER upload preview and service stackup, latest prices/stock and fabrication review. Do not order from this candidate BOM merely because ERC/DRC pass.
4. Cold loaded startup, three-hour runtime with reserve, brownout/SD transients and fault tests on the complete pack/board; logging endurance, vibration/retention and magnetic/GPS/thermal interference. Whole-module -40 C and altitude suitability remain unproven.
5. Firmware GPS RMC freshness/matching remains open from the earlier checkpoint. Then casing CAD around the measured final assembly.

`tools/apply_component_finalization.py` is the guarded **initial migration only**, not a full reconstruction of the subsequent clearance refinements. Do not rerun it on the current design or regenerate the board. `tools/component_selections.py` keeps schematic generator fields aligned without regeneration. Run read-only verification scripts into a new dated evidence directory after further native changes.
