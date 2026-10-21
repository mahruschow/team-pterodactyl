# Component finalization research — handoff October 21, 2026

## First prototype scope and order checkpoint - October 21, 2026

**Current authority: [FIRST_PROTOTYPE_RELEASE.md](FIRST_PROTOTYPE_RELEASE.md).** PCB checks and AISLER upload/preview passed; project TCVOYNZG revision 1 is ready for checkout. FB1/SW1/SW2/J3 are selected for P1. The user explicitly excludes physical testing, flight qualification, subsequent redesign and casing from this phase; older statements requiring those before PCB fabrication are superseded. Assembly receipt/polarity checks remain part of building the prototype. No order placed. Updated known cost is USD 129.37 (15 price lines missing); entered mass 170.25 g (three missing). The provisional EUR board quote is separate.

**Historical research checkpoint, not a released BOM.** The later targeted implementation and revised choices (including MRS16 and BH4AAW) are in [COMPONENT_IMPLEMENTATION.md](COMPONENT_IMPLEMENTATION.md). Statements below about changes not being applied describe the earlier checkpoint.

**Original research boundary:** These recommendations have not been applied to the schematic, PCB, exported BOM or live budget. The current native design still contains the earlier candidate/generic components. See RESUME_HERE.md for authoritative requirements and next actions. No purchase or new native-design validation occurred during this research.

## Battery and storage recommendations

**Battery: four Energizer L91 AA Li/FeS2 primary cells in series**, nominal 6 V, typical cell-only mass 60 g. This is the leading lightweight candidate for the existing buck-boost architecture, not a guarantee of three-hour operation. Its published operating range includes -40 C. Four cells reduce required current and improve startup voltage margin relative to three; series connection does not multiply Ah. These are non-rechargeable cells. [Energizer current datasheet](https://data.energizer.com/pdfs/L91GL0225.pdf).

The manufacturer's temperature graph was visually inspected: capacity falls strongly at -40 C under higher loads. The 2.5 A continuous headline is single-cell data at room temperature unless otherwise stated; do not apply it unchanged at -40 C. Do not assign a fixed 3.5 Ah cold capacity from the room-temperature curve. Existing model currents for a four-cell pack are approximately 0.249 A average / 0.547 A peak at 6 V, and 0.374 A / 0.821 A at 4 V. Four volts is a screening example, not an implemented cutoff. The regulator needs at least 3 V at its own input to start, after wiring/protection losses. Select a qualified loaded-voltage endpoint and test cold startup and complete logging.

The **holder/finished pack is unresolved**. MPD BA4AAW's manufacturer drawing specifies -10 to +100 C, so it is not an acceptable rated -40 C choice. MPD 6S-AA is rated -40 to +180 C but holds only ONE cell and uses PCB pins; four of them would need additional integration. Do not misidentify it as a four-cell holder. A professionally assembled pack is another option, but no pack-builder SKU has been verified. Cell restraint, wiring and connector mass must be added to the 60 g cells. Sources: [BA4AAW drawing](https://www.batteryholders.com/uploads/parts/BA4AAW/datasheets/BA4AAW-datasheet.pdf), [MPD 6S-AA](https://products.memoryprotectiondevices.com/?page_id=793).

**microSD: Kingston Industrial SDCIT2/8GB**, 8 GB pSLC industrial microSDHC, -40 to +85 C; FAT32 for the initial Teensy logging setup. SDCIT2/8GBSP is the no-adapter variant; the adapter is not flown. Eight GB leaves ample space for this logger. The public summary does not establish an exact current maximum; measure write/startup peaks and retain an explicitly provisional allowance. Card power-failure features do not replace firmware sync/clean-stop handling. [Kingston datasheet](https://www.kingston.com/datasheets/SDCIT2_en.pdf), [exact product](https://www.kingston.com/en/memory/search?partid=SDCIT2%2F8GB).

## On-board component research

The table records the proposed order code and remaining review, not permission to silently substitute other parts. Quantities derive from the current schematic.

| References | Proposed exact part | Findings / remaining work |
| --- | --- | --- |
| U1–U5 | PJRC Teensy 4.1; Pololu 2836; Adafruit 2472, 4716, 5440 | Retain specified modules. Whole-module cold operation is not established merely from individual IC ratings. |
| C1, C3 | Panasonic **EEUFR1E101**, 100 uF 25 V | Proposed C1 increase from 47 to 100 uF and C3 voltage increase from 10 to 25 V. 6.3 mm diameter, 11.2 mm body length, 2.5 mm pitch, -40 to +105 C. Existing radial footprint matches nominal pitch/diameter; height and cold impedance still need review. |
| C2, C4, C7, C9, C11 | KEMET **C322C104K5R5TA**, 100 nF 50 V 10% X7R | Max body 5.08 mm long, 3.18 mm thick, 6.6 mm high. Generic disc body is inaccurate. |
| C5, C6, C8, C10 | KEMET **C322C106K3R5TA**, 10 uF 25 V 10% X7R | Max body 5.08 mm long, 4.07 mm thick, 6.6 mm high. Generic disc body is inaccurate. Review usable capacitance under bias and temperature. |
| Q1 | Alpha & Omega **AO3401A** | Candidate replacement for discontinued IRLML6402. SOT-23 G/S/D, top-view drawing inspected. -30 V Vds, +/-12 V Vgs, max 85 mOhm at -2.5 V gate drive. Check pin mapping against existing G1/S2/D3 and source-to-protected-rail orientation. No replacement applied yet. |
| D1 | Nexperia **BZX79-C10,133** | 10 V zener, DO-35. Existing R1 gives low clamp bias; do not claim precise 10 V clamping at arbitrary input voltage. Four-cell battery contract is narrower than regulator's standalone 16 V input limit. |
| F1 | Bourns **MF-RHT070-0** | 0.7 A hold / 1.4 A trip nominal at 23 C. Hold changes with temperature (about 0.95 A at -40 C, 0.62 A at 40 C). Review time-current curve, path loss, startup and fault behavior; hold is not an instantaneous cutoff. Retain as candidate until reviewed. |
| FB1 | Murata **BL01RN1A2A2B** | Bulk packaging suffix B; source family drawing matches existing axial footprint. Confirm exact current, temperature and ordering status from manufacturer documentation before closing. |
| R1, R2 | Vishay **MRS25000C1003FCT00** | 100 kOhm, 1%. Check active ordering status and maximum body dimensions against DIN0207 footprint. |
| R3 | Vishay **MRS25000C2202FCT00** | 22 kOhm, 1%. Same family review. |
| R4–R7 | Vishay **MRS25000C6800FCT00** | 680 Ohm, 1%. Retain resistance. |
| D2 | Kingbright **WP7113LID** | Low-current red, 5 mm THT. |
| D3 | Kingbright **WP7113LYD** | Low-current yellow, 5 mm THT. |
| D4 | Kingbright **WP7113LGD** | Low-forward-voltage green, 5 mm THT; avoid a generic high-Vf green substitution. |
| D5 | Kingbright **WP7113LSECK/J4** | Low-current orange, 5 mm THT. Check flange/body limits and recalculate actual LED current assumptions. |
| J1, J2 | Molex **22-27-2021** (0022272021) | Proposed -40 C-rated replacement for JST-XH, whose published minimum is only -25 C. Pitch changes 2.50 to 2.54 mm. Must update footprints and affected route endpoints; keep polarity/net mapping. |
| SW1 | C&K **OS102011MS2QN1** | Proposed full order code; validate drawing and non-shorting configuration against existing OS102011MS2Q footprint. |
| SW2 | C&K **PTS645SL50-2 LFS**, Littelfuse order code **Y97HT21A1FAFP** | 5 mm-high, 1.3 N, through-hole version, -40 to +85 C. Latest datasheet identifies available order code. Check 6.5 x 4.5 mm holes, contact-pair mapping and actuator height. SMTR variants are surface mount and must not be substituted. |
| J3 | Samtec **HTSW-102-07-T-S** | Standard two-pin header proposal; verify pad orientation and shunt choice. |
| J4 | DNP | Spare header remains unpopulated unless needed. |
| TP1–TP10 | Exposed PCB pads only (proposal) | No purchased pin hardware needed for probing; adjust mass allowance if adopting this population decision. |

KEMET lead pitch is **5.08 +/-0.78 mm**; current 5.00 mm hole centers are within that range. Keep existing pad centers only after checking the actual specified lead form. Both use approximately 0.51 mm leads. Create accurate local rectangular body/courtyard geometry and preserve nets, UUIDs and routing. A correct lead pitch does not prove surrounding body clearance.

Molex standard KiCad footprint candidate: `Connector_Molex:Molex_KK-254_AE-6410-02A_1x02_P2.54mm_Vertical`. Its 1.74 mm minor pad size around a 1.19 mm drill leaves only 0.275 mm nominal radial annulus; AISLER's component PTH rule calls for 0.30 mm. Proposed local adaptation: 1.90 x 2.19 mm pad with 1.19 mm drill (0.355 mm minimum nominal ring). Verify the official drawing before adopting. Current J1/J2 are rotated 90 degrees; a 0.04 mm pitch shift must be transformed into board coordinates, not applied blindly to X. Possible mating housing **22-01-2027**, contacts **08-50-0113**; verify the complete mated assembly ratings and crimp/wire match. Header rating alone does not qualify the harness.

### Primary references for the table

- [Panasonic exact part](https://industrial.panasonic.com/ww/products/pt/aluminum-cap-lead/models/EEUFR1E101)
- [KEMET 100 nF exact sheet](https://search.kemet.com/component-documentation/download/specsheet/C322C104K5R5TA), [KEMET 10 uF exact sheet](https://search.kemet.com/component-documentation/download/specsheet/C322C106K3R5TA)
- [AO3401A](https://www.aosmd.com/pdfs/datasheet/AO3401A.pdf), [Nexperia BZX79](https://assets.nexperia.com/documents/data-sheet/BZX79.pdf), [Bourns MF-RHT](https://www.bourns.com/docs/product-datasheets/mf-rht.pdf)
- [Vishay MRS family](https://www.vishay.com/docs/28724/mrs16m25.pdf)
- Kingbright: [red](https://www.kingbrightusa.com/images/catalog/SPEC/WP7113LID.pdf), [yellow](https://www.kingbrightusa.com/images/catalog/SPEC/WP7113LYD.pdf), [green](https://www.kingbrightusa.com/images/catalog/SPEC/WP7113LGD.pdf), [orange](https://www.kingbrightusa.com/images/catalog/SPEC/WP7113LSECK-J4.pdf)
- [Molex header](https://www.molex.com/en-us/products/part-detail/22272021), [housing](https://www.molex.com/en-us/products/part-detail/22012027), [KK254 family literature](https://www.content.molex.com/dxdam/literature/987651-0403.pdf), [existing JST-XH](https://www.jst-mfg.com/product/index.php?lang=2&series=277)
- [C&K OS family](https://www.ckswitches.com/media/1428/os.pdf), [current PTS645 datasheet](https://www.littelfuse.com/assetdocs/littelfuse-c-k-tactile-pts645-series-datasheet?assetguid=d58fc8a8-f6e1-4527-ab68-27635e632e39). The latter could be read through web search, but direct PDF download returned access denied; no complete visual drawing review was obtained.

## External assembly components

Proposed soldered sensor headers: Samtec **HTSW-106-15-T-S** and **HTSW-104-15-T-S** for BNO055; **HTSW-105-15-T-S** for MS8607; **HTSW-109-15-T-S** for GPS. Catalog drawing was visually inspected: style -15 has 18.54 mm overall pin length, 2.79 mm short tail and 13.21 mm long post, with 2.54 mm insulator. Tin versions list -55 to +105 C. With the insulator on the carrier, these nominal dimensions could retain a 12 mm carrier-top to module-underside spacing, leaving roughly 2.15 mm above a 1.6 mm module PCB. Confirm actual board thickness, pin tolerances, finished holes, protrusion, trimming and underside clearance. **This is an assembly proposal, not a verified stackup.** [Samtec catalog](https://suddendocs.samtec.com/catalog_english/tsw_th.pdf).

Existing Teensy/regulator socket proposals remain in MODULE_ASSEMBLY_PLAN.md. Exact spacers, screws, battery restraint and casing are unresolved; choose light, cold-compatible materials and evaluate magnetic effects near BNO055.

Panel switch candidate: **APEM 5636AB**, SPDT ON-ON, use common and one throw for power on/off with unused throw insulated. Published -40 to +85 C; solder-lug type. Final DC rating, terminal identification, panel hole and mass review still needed. [Exact manufacturer page](https://www.apem.com/panel-switches/5000/p/5636ab).

## AISLER direction and open checks

Working fabrication choice: retain **four layers, 1.6 mm, 35 um, ENIG**. Do not halve thickness solely to save mass before checking stiffness, mounted-module loading and hole/connector tolerances. No board outer-dimension change has been made. AISLER assembly service versus team hand assembly has not been decided; sensor through-hole soldering does not imply AISLER will assemble these modules. Q1 remains an SMD part.

The [official 4-layer 35 um ENIG rules](https://community.aisler.net/t/4-layer-35-m-enig-design-rules/3733) were reviewed. Key checks to apply: 0.125 mm track clearance; 0.30 mm component PTH annular ring; 0.10 mm via ring; 0.30 mm hole-to-hole edge spacing; silk 0.15 mm stroke, 0.8 mm text height, 0.125 mm pad clearance. Review all other limits directly, including drill classification, masks, edges and via treatment. The current project has some looser settings, notably 0.25 mm hole spacing and zero silkscreen clearance, so the earlier clean DRC does **not** establish AISLER compliance. Confirm current stackup and unsupported via options from AISLER rather than guessing dielectric thicknesses.

Next deliverable: an applied, checked exact BOM and updated native files with preservation evidence. Do not label this research document, old BOM or previous zero-DRC report as a fabrication release.
