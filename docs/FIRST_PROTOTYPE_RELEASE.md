# First prototype: fabrication and assembly handoff

October 21, 2026. Active design: Native_KiCad_v4, first-prototype checkpoint developed on saadat-dev. **The PCB is ready for the first prototype order. No order has been placed.** Reviewed fabrication ZIP and budget workbook are stored in `releases/2026-10-21-P1/`; native files and validation evidence remain in their source locations.

The user's scope ends at the first physical prototype. Cold-runtime testing, flight testing, qualification, revisions after testing and custom casing are outside this phase. Those activities are not prerequisites for ordering these boards. Ratings and calculations below are design evidence, not measured performance.

## PCB order

[AISLER project TCVOYNZG, revision 1](https://aisler.net/p/TCVOYNZG) was created from the saved native board. AISLER reports successful processing. Its top/bottom previews, outline, holes and four-layer interpretation were inspected. Checkout is prepared for **Beautiful Boards (bare PCB), quantity 3, four layers, 1.6 mm, 35 um copper, ENIG, green mask, white silkscreen**, with no stencil or expedited-service add-ons. Hand assembly is intended, including the small SOT-23 Q1.

AISLER recognizes **97.79 x 97.79 mm**, the unchanged outline centerline dimensions. Earlier approximately 98 mm dimensions include rounding or edge stroke width. Do not resize the board to reconcile those numbers.

The anonymous checkout showed EUR 51.37 net, EUR 9.76 default 19% VAT, EUR 61.13 total, and estimated dispatch November 3, 2026. This is a provisional quote, not the delivered US price: sign in, enter the actual shipping/tax details and review the recalculated total. Account access and payment remain with the user. The project was uploaded, but nothing purchased or publicly published.

Use the saved AISLER project or the native board in the handoff ZIP. A separate Gerber ZIP is supplied as an alternative. It contains four copper layers, two mask layers, two legend layers, one outline, separate PTH/NPTH Excellon files and IPC-D-356 netlist. No paste stencil is needed for the planned hand assembly. The automatically generated `.gbrjob` is deliberately excluded because its default dielectric thicknesses/finish are not the selected AISLER service stackup. The order specification governs: [AISLER stackup](https://community.aisler.net/t/4-layers-1-6mm-35-m-stackup/5457), [design rules](https://community.aisler.net/t/4-layer-35-m-enig-design-rules/3733), [KiCad upload guidance](https://community.aisler.net/t/kicad/88).

## Last four board selections closed

| Ref | First-build selection | Drawing/electrical check |
| --- | --- | --- |
| FB1 | Laird 28L0138-10R-10 | Replaces obsolete Murata. 75 ohm nominal at 100 MHz, 5 A, 0.01 ohm maximum DCR, -40 to +125 C. Maximum body 4.70 x 3.76 mm; maximum lead diameter 0.69 mm. Local footprint retains 10 mm pitch, 0.85 mm drills and 1.60 mm pads. Form leads with support at the body; do not pull against the ferrite. |
| SW1 | C&K OS102011MS2QN1 | Manufacturer drawing matches 2 mm signal pitch and 8.2 mm anchor span. Common pin 2; unused throw 3. Grounded position requests clean logging stop. Older sheet specifies -30 to +70 C; a newer temperature claim is not used to qualify the assembly. Minimum reliable long-term wetting current is unspecified. |
| SW2 | C&K PTS645SL50-2 LFS | Exact legacy ordering code: straight leads, 5 mm actuator, 130 gf. Drawing matches 6.5 x 4.5 mm pattern; top pair is common, bottom pair is common. KiCad's repeated pad numbers match those pairs. Avoid an alias-only substitution without checking configuration. |
| J3 | Samtec HTSW-102-07-T-S with SNT-100-BK-T | Matching tin 2.54 mm shunt, 0.635 mm square posts and 5.84 mm mating length. Header recommended hole 1.02 +/-0.03 mm includes the 1.00 mm nominal footprint. Firmware removal event is a launch marker, not a power disconnect. |

Sources: [Laird current product](https://www.laird.com/products/inductive-components-emc-components-and-ferrite-cores/ferrite-beads-on-wire/28l0138-series/28l0138-10r-10), [Laird drawing](https://www.farnell.com/datasheets/1685873.pdf), [C&K OS catalog, PDF page 36](https://www.farnell.com/datasheets/1851186.pdf), [C&K PTS645 drawing, pages 1-2](https://datasheet.datasheetarchive.com/originals/dk/DKDS42/DSANUWW0042856.pdf), [Samtec header](https://suddendocs.samtec.com/catalog_english/tsw_th.pdf), [shunt drawing](https://suddendocs.samtec.com/prints/snt-100-xx-x-x-mkt.pdf). Manufacturer-authored mirrored drawings were used where current vendor downloads were inaccessible.

FB1 body graphics and four part fields changed in this phase. Pads, nets, copper routing and module placements did not. The board legend now reads PTERODACTYL v4 P1 - FIRST PROTOTYPE. Earlier targeted connector/capacitor changes remain; see COMPONENT_IMPLEMENTATION.md for their history. The 47-reference BOM now has zero blank MPNs and zero held candidate references. Ten test pads need no purchased hardware; J4 remains DNP.

## Battery and power assembly

Use **four Energizer L91 primary AA cells in series in MPD BH4AAW**, with Kingston SDCIT2/8GB in the Teensy slot. The battery and holder specifications support the requested -40 C minimum on paper. The completed harness and runtime are unmeasured. Do not recharge or solder directly to the cells.

Build the positive harness as `holder red -> insulated pack fuse -> J1 pin 1`. Connect holder black to J1 pin 2 (GND). Add **Littelfuse 025101.5MXL**, 1.5 A fast axial fuse, near the holder lead exit. It supplements board F1 and protects the downstream harness. Support both leads and enclose the fuse and splices in insulation; leave the shortest practical protected section before it. Do all soldering with cells removed. This fuse is rated 125 VDC, 300 A DC interrupt, -55 to +125 C; its 0.0823 ohm cold resistance is nominal at room temperature, not a -40 C maximum. [Littelfuse manufacturer sheet](https://www.mouser.com/datasheet/2/240/media-3323600.pdf).

Retain board **MF-RHT070-0** for P1. With a 6 V terminal voltage and an illustrative 1.15 ohm path, modeled peak current is 0.605 A and regulator VIN 5.304 V, versus 0.70 A PTC hold at 23 C. This supports the first nominal-voltage build; it does not establish a discharge endpoint or cold startup. At 4 V the same model falls below the regulator's startup threshold. Use fresh matched cells for the first build; no three-hour measured-runtime claim is made.

J1 and J2 each use Molex **0022012027** housing with two **0008500113** contacts. For additional harness wire use stranded **Alpha Wire 3050**, 24 AWG, in red and black; use red or clearly labeled wire for both J2 switch conductors. Its specified 1.422 +/-0.051 mm insulation diameter fits the contact's 1.02-1.57 mm tool range. Use Molex **0640160201** ServiceGrade tool or an appropriately qualified assembler; its sheet explicitly lists this terminal. Strip 2.54-3.17 mm, crimp conductor and insulation separately as instructed, inspect retention and continuity before inserting cells. Do not assume the supplied holder lead's insulation diameter is correct for a direct crimp; splice to the selected wire when necessary. Tooling is bench equipment, not installed mass. [Alpha specification](https://www.farnell.com/datasheets/428386.pdf), [Molex tool specification, page 2](https://www.tme.eu/Document/d946c5a6efd66b5855487ea546568486/ATS-640160201.pdf).

For the first room-temperature build, external power switch **C&K 7101SYZQE** connects J2's two conductors through common terminal 2 and one outer terminal; insulate the unused throw. Label the connected position ON. J2 is a switch loop: **neither conductor is ground**. This 5 A/28 VDC switch is rated -30 to +85 C and is not a -40 C flight selection. It can be supported on a small insulating bench bracket; final casing placement is deferred. [C&K 7000 drawing and ratings](https://www.littelfuse.com/assetdocs/littelfuse-ck-toggle-7000-series-datasheet?assetguid=fed01bc6-88d0-4bda-b896-13c98cf9e90e).

Hold the four cells in the holder with two nonconductive straps and support the holder separately from the board. Secure the cable so pulling it does not load contacts or solder joints. Keep the holder and switch away from the BNO055. Casing and flight retention are not part of this first-build release.

## Assembly sequence

1. Buy the quantities for **one populated prototype** in the grouped board BOM plus off-board BOM. Three fabricated PCBs does not mean three sets of modules. Order modules without preinstalled headers where available; do not duplicate included hardware. Commodity spacers/fasteners are specified by dimensions in the off-board list.
2. Populate Q1, low-profile resistors/diode/ferrite, switches, connectors and capacitors before modules. Check Q1 G1/S2/D3, diode cathode band, LED A/K and electrolytic polarity against the schematic and assembly drawing. C1/C3 are 100 uF 25 V, nominal 11.2 mm high; allow sleeve/height tolerances.
3. Install sensor HTSW -15 pins with the insulator on the carrier and long posts toward the modules. Populate both BNO055 rows, including unused signals. Use 12 mm insulating spacers and M2 fasteners through the existing module holes: four BNO055, four MS8607 and two GPS. Nominal 1.6 mm module thickness leaves about 2.15 mm upper pin protrusion. Check orientation, free seating and underside clearance during assembly before soldering both ends. This receipt/assembly check does not delay PCB ordering or add a test-and-redesign phase. Do not pull a module flat with screws if something contacts underneath.
4. Teensy uses two SSW-124-01-L-S sockets and two HTSW-124-07-L-S headers. Regulator uses SSW-103-01-L-S / HTSW-103-07-L-S. Fully seated nominal board separation is 11.05 mm. Keep USB, program button and microSD access open. Leave J4 unpopulated.
5. Before USB and external power can be used together, **cut the Teensy's VUSB-to-VIN link as specified by PJRC and check isolation with power disconnected**. Then programming requires external power and USB data. This is an assembly instruction, not a carrier PCB trace cut. See POWER_ARCHITECTURE.md and [PJRC Teensy 4.1](https://www.pjrc.com/store/teensy41.html).
6. Fit the selected SD card, assemble the harness, check for solder bridges and verify J1 polarity with the harness disconnected from the carrier. Install the J3 shunt. Load the existing Firmware_v4 build. Firmware is still 4.0.2-draft; GPS RMC freshness work is deferred and has not been claimed fixed.

## Checks and budget

Evidence is in `validation/2026-10-21/first-prototype-release/`: zero ERC violations, zero enabled DRC violations, zero unrouted connections and zero schematic parity errors. The independent net contract checks 32 nets and 35 intentional no-connects. There are 51 footprints, 246 track segments, 25 vias, 183 plated drill hits and 14 nonplated holes.

The preservation audit retains original footprint/pad/track/via identities, all pad nets, outline, module positions and zone boundaries. Earlier four small footprint moves and eight endpoint changes remain documented. Five pre-existing ignored DRC categories are unchanged: footprint filter/type mismatch, missing courtyard, track centering on via and tuning-profile geometry. No new exclusions were added. AISLER processing is a manufacturing interpretation check, not an electrical performance test.

Power planning remains 1.618301 W average / 3.567647 W peak, 4.854902 Wh over three powered hours and an 8.669468 Wh provisional nominal energy target. Path screening now includes an allowance for the added pack fuse. Entered mass remains 170.25 g with three missing mass lines. The known USD cost subtotal is 129.37 with 15 unpriced lines; tool cost and the separate EUR board quote are not silently folded into that subtotal. Complete cost/mass totals remain incomplete. Missing quotes and casing mass do not block this uncapped first PCB order.

**Remaining execution:** sign in to AISLER and finalize the delivered PCB order; procure the BOM and workshop consumables; solder and assemble one prototype. No physical testing, flight qualification or later revision is included in this phase.
