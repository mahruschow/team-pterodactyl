# Resume here: first prototype order ready

October 21, 2026. User scope: get to the first physical prototype. Physical testing, flight qualification, subsequent redesign and custom casing are outside this phase and are not PCB-order gates.

Repository `C:\Users\saada\OneDrive\Documents\team-pterodactyl`; development branch `saadat-dev`. The user authorized committing this checkpoint, pushing it to `saadat-dev`, then updating `main`. Check Git history and remote refs for publication status. Inspect git status/diff before editing. Active design is Native_KiCad_v4; shared local library remains in Native_KiCad_v11. Do not regenerate the routed board/full schematic or run the autorouter. Use targeted changes retaining UUIDs and pad nets. Local scratch and backups remain preserved under ignored `work/`.

## Read in order

1. FIRST_PROTOTYPE_RELEASE.md: current order, assembly instructions, power decisions and scope.
2. COMPONENT_IMPLEMENTATION.md, then COMPONENT_FINALIZATION_RESEARCH.md: applied changes and historical evidence; older held-part and testing gates are superseded by the first-prototype release.
3. CURRENT_STATUS.md, REMAINING_WORK.md, POWER_COST_MASS_BUDGET.md, MODULE_ASSEMBLY_PLAN.md.
4. GPS_CARRIER_INTEGRATION.md, TEENSY_MECHANICAL_REVIEW.md, POWER_ARCHITECTURE.md, SENSOR_CONNECTION_MAP.md, PLACEMENT_AND_INTERFERENCE.md.
5. validation/2026-10-21/first-prototype-release/ and native files before further editing. Firmware docs only if resuming firmware work.

## Current state

AISLER project https://aisler.net/p/TCVOYNZG revision 1 successfully processed the exact native PCB. Preview checked top/bottom, four layers, 97.79 x 97.79 mm. Checkout prepared: Beautiful Boards, 3 bare PCBs, 1.6 mm, 35 um, ENIG, green/white, no addons. Anonymous quote EUR 51.37 net / EUR 61.13 with default 19% VAT, estimated dispatch Nov 3. Actual destination/tax/account pricing must be entered before payment. No order placed. The visible AISLER tab is retained for handoff.

FB1 now Laird 28L0138-10R-10 with local P10 footprint; SW1 OS102011MS2QN1 and SW2 PTS645SL50-2 LFS drawings checked; J3 HTSW-102-07-T-S mates SNT-100-BK-T. Four previous held board references closed for P1. All 47 BOM references have MPNs; 36 purchased board components/modules after excluding J4 DNP and ten bare test pads. Grouped purchase and off-board BOMs are included.

Fresh validation: 0 ERC, 0 enabled DRC, 0 unrouted, 0 parity; 32 expected nets, 35 intentional no-connects; 51 footprints, 246 segments, 25 vias. Exported drills match native positions within Excellon 0.001 mm coordinate rounding: 183 PTH, 14 NPTH. Original identities/nets/outline/module positions retained. Four earlier small footprint movements and eight endpoint adjustments remain, not new changes this phase. Existing five ignored DRC categories unchanged. No new exclusions.

Confirmed requirements remain: 3 h total powered runtime, battery minimum -40 C, about 30,000 ft, no telemetry, through-hole soldered sensor modules, AISLER, no spending cap, practical low mass without hard limit, preserve compatible dimensions. Four L91 in BH4AAW and Kingston SDCIT2/8GB selected for first build. Add 025101.5MXL pack-side fuse. Harness, sensor spacing, socket headers, bench switch and assembly sequence are in FIRST_PROTOTYPE_RELEASE.md. The assembled system is not flight/cold/runtime qualified; those tests are outside the current phase.

Budget: 1.618301 W average / 3.567647 W peak, 8.669468 Wh provisional target for 3 h. Separate 1.15-ohm resistance screen includes pack fuse. Entered mass 170.25 g with three missing lines; known USD price 129.37 with 15 unpriced lines. EUR PCB quote remains separate. No complete procurement or mass total is claimed. Live budget session document_21d90808-743d-456b-8775-87ca5a43cfea; builder creates a NEW workbook only.

Firmware unchanged at 4.0.2-draft; previous host/compile evidence retained. GPS RMC freshness is deferred. J3 removal already logs PBF_REMOVED, not a power cut. Teensy VUSB/VIN isolation is a required assembly step before simultaneous USB/external power.

## Remaining execution

An optional open PCB bench holder is available in `mechanical/pcb-holder/` (STEP, STL, editable source, preview and mounting instructions). It uses the existing four corner holes, with 10 mm clearance above its frame. CAD solid/mesh checks passed; printed fit and full component/hardware clearance remain unverified. No PCB changes were made for it. The user separately requested this quick holder and authorized publication to main; the flight enclosure remains deferred.

Sign in to AISLER, enter shipping/tax details and finalize order. Procure parts for one populated prototype, then assemble. No requirement to fly, cold-test or iterate a prototype before placing the PCB order. Commodity assembly hardware is dimensionally specified; receipt checks occur while assembling, not as a fabrication prerequisite.

## Preservation and evidence

Initial native checkpoint: work/component-finalization-baseline/. Additional pre-P1 checkpoint: work/first-prototype-baseline/. Source PDFs in local scratch are referenced by URLs/hashes in release evidence. Manufacturing ZIP excludes the default .gbrjob stackup; selected AISLER service controls the stackup. The Git working tree is authoritative for further edits; exported ZIP is a snapshot.

Use one pcbnew LoadBoard per process; keep GetTracks owner alive. Verification scripts accept CLI path and new evidence directory. verify_component_preservation.py takes original baseline and output JSON. verify_fabrication_package.py compares exported drills/layer metadata with current native. Do not rerun the old guarded migration scripts.

Current native hashes:
- `PTERODACTYL_v4.kicad_pcb`: `3939c94d0d2279776b6aff804f6814c09e275b59fea913cd9d96c8ba36f766a6`
- `PTERODACTYL_v4.kicad_sch`: `39d6b0c75259f510b298a408b1ae700c84622dc93b88eb56d1e584edec9e7154`
- `PTERODACTYL_v4.kicad_pro`: `6b6741a208c3b716519252bb4229848cdc5922948a758c8d4f4668998329ca82`
- `PTERODACTYL_v4.kicad_dru`: `e14084119c2cc54b0cac4186f663c33994e14025c7ea552a4c21899a039d987c`
