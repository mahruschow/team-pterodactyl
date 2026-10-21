# Resume here — October 21, 2026, component implementation

This handoff supersedes the earlier research-only checkpoint. **Targeted KiCad edits, AISLER dimensional checks and the budget update are applied; physical fit and flight qualification are not complete.**

## Workspace and preservation

- Repository: `C:\Users\saada\OneDrive\Documents\team-pterodactyl`, branch `saadat-dev`, HEAD observed `e2664ad219d1493cc166856ba750f05f734da859`.
- Substantial uncommitted work, including pre-existing GPS, firmware/docs and budget changes. Inspect status and diffs first. Do not reset, overwrite or assume the remote contains it.
- Active files: `Native_KiCad_v4/PTERODACTYL_v4.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, `.kicad_dru`. Shared library: `Native_KiCad_v11/Pterodactyl_Modules.pretty/`; v11 is the library location, not the active design.
- Firmware: `Firmware_v4/PTERODACTYL_v4/`. KiCad 10.0.7 CLI/Python: `C:\Program Files\KiCad\10.0\bin`.
- **Do not regenerate the routed board or full schematic, run the autorouter, or rerun the migration script on current files.** Make targeted changes preserving UUIDs/nets. Reload a stale KiCad editor before saving.
- Pre-edit native checkpoint is locally backed up in `work/component-finalization-baseline/`. Scratch downloads/scripts in `work/` are not release inputs. Old GPS validation evidence is preserved.

## Confirmed requirements — do not ask again

Three hours TOTAL powered runtime including preparation/recovery wait; battery minimum -40 C; approximately 30,000 ft; no telemetry; onboard logging; through-hole soldered BNO055/MS8607/GPS modules. Teensy/regulator socket proposals remain. Teensy 4.1, Adafruit 2472/4716/5440 and Pololu 2836 remain specified. AISLER manufacture; no spending cap; minimize practical mass without a hard ceiling. Preserve current dimensions when compatible. Custom casing CAD follows the board and measured assembly. Whole-breakout cold ratings cannot be inferred from individual IC ratings.

## Read in this order

1. `COMPONENT_IMPLEMENTATION.md` — applied changes, reviewed sources, preserved geometry, battery/harness candidates, power limits, AISLER and remaining gates.
2. `COMPONENT_FINALIZATION_RESEARCH.md` — historical research; MRS25 and unresolved-holder statements are superseded by the MRS16/BH4AAW review.
3. `CURRENT_STATUS.md`, `REMAINING_WORK.md` — newest sections override older entries.
4. `POWER_COST_MASS_BUDGET.md`, `../tools/create_budget_workbook.js` — current model and historical comparison.
5. `MODULE_ASSEMBLY_PLAN.md`, `GPS_CARRIER_INTEGRATION.md`, `TEENSY_MECHANICAL_REVIEW.md`.
6. `POWER_ARCHITECTURE.md`, `SENSOR_CONNECTION_MAP.md`, `PLACEMENT_AND_INTERFERENCE.md`.
7. `SENSOR_READ_VALIDITY.md`, `FIRMWARE_RELIABILITY.md` if doing firmware; then dated session notes.
8. Inspect native files, `validation/2026-10-21/component-finalization/`, git status and diffs before further edits.

## Current implementation

51 footprints, 246 segments, 25 vias. All original footprint/pad/track/via UUIDs and pad nets remain; outline/module placements/zone boundaries unchanged. Eight segment endpoints changed locally; C2/C6/C8/TP4 moved slightly. J1/J2 now Molex KK254, capacitor bodies corrected, C1/C3 100 uF 25 V, Q1 AO3401A, MRS16 resistors and exact component fields applied. J4 DNP; test pads have no purchased hardware.

Fresh saved checks: **0 ERC / 0 enabled DRC / 0 unconnected / 0 parity**; 32 expected nets, 35 no-connects verified. BOM has 47 individual reference rows, zero blank MPNs and **four held references: SW1, SW2, J3 candidates; FB1 rejected as obsolete**. Detailed rules, ignored pre-existing categories and scope are documented; clean DRC is not an AISLER order approval.

Prototype pack candidate: **4 series Energizer L91 in MPD BH4AAW**. Holder drawing is -40 to +140 C; BA4AAW is not the selected part. Full harness/protection/retention remains unresolved and untested. Storage: **Kingston SDCIT2/8GB**; current allowance is not a published maximum. Nothing ordered or flight-qualified.

Updated budget: 1.618301 W average / 3.567647 W peak; 4.854902 Wh over 3 h; provisional 8.669468 Wh nominal target (70% usable, 25% reserve). Nominal pack 6 V; minimum loaded voltage remains blank. A 1-ohm path screen at 4 V predicts regulator input below startup threshold. Entered mass **170.25 g**, three mass lines missing; known price **$118.30**, 16 price lines missing. Complete totals stay incomplete.

Live budget session: `document_21d90808-743d-456b-8775-87ca5a43cfea`. Prior artifact `artifact_FUIBR-EQUnXhhV3JS2j9rrmri3HwRDLQ` was unavailable in this continuation. The builder reproduces a NEW workbook; never rerun it into a populated one. Follow the spreadsheet skill. Excel export and review copies are in this Codex chat's outputs folder; authoritative data/source/evidence are in this repository.

Firmware remains 4.0.2-draft: previous 16 host fault-test groups and Teensy compile passed. **GPS RMC freshness/matching is not fixed**. No new hardware tests or firmware edits in this continuation.

## Next actions

1. Close SW1 visual drawing/low-current contacts, SW2 contact pairs/height-force ambiguity, J3 shunt/fit/role and replacement for obsolete FB1. Do not promote candidate codes on the strength of populated fields. Manufacturer switch downloads were blocked/timed out; source limitation is documented.
2. Finish crimp tooling/insulation/polarity, pack-side short protection/insulation and strain relief, external power switch, nonmagnetic module and cell restraint. Dry-fit actual headers, capacitor sleeves/heights, GPS holder, USB/SD access and spacer stack.
3. Review AISLER upload, actual service stackup/mask/ink interpretation and stock/quotes before release. No controlled-impedance stackup was invented. Current native target is four layers/1.6 mm; component/via drill, annulus, clearances and silk rules pass locally.
4. Cold loaded startup, three-hour runtime/reserve, supply transients, SD endurance, brownout/fault and mechanical/interference testing. Do not assume cold cell current/energy from room-temperature headlines. Whole-assembly altitude/temperature suitability is unproven.
5. GPS freshness firmware task and then casing around measured final assembly.

## Validation/tool notes

Use one pcbnew LoadBoard per Python process; retain the GetTracks container while accessing wrappers. For vias use GetWidth(pcbnew.F_Cu), not the no-argument call. Save a native zone refill before validation. Verification scripts accept CLI path as argument 1 and a new output directory as argument 2. Preservation checker takes baseline PCB and output JSON. Migration script is only the initial hash-guarded edit; subsequent clearance fixes are already saved in the native board. Generator field source was synchronized without regenerating.

No commit, push, purchase, external message, or fabrication order was made. Current native SHA-256 values follow (also `native-hashes.json`):

- `PTERODACTYL_v4.kicad_dru`: `e14084119c2cc54b0cac4186f663c33994e14025c7ea552a4c21899a039d987c`
- `PTERODACTYL_v4.kicad_pcb`: `bfa61f10db5c565da103afd3172880e875aae43eb892818baa89bac8df7184cf`
- `PTERODACTYL_v4.kicad_pro`: `6b6741a208c3b716519252bb4229848cdc5922948a758c8d4f4668998329ca82`
- `PTERODACTYL_v4.kicad_sch`: `430b6bb52dab2902e64b517d1a0f8c81940add06692e45550b44755db550aafd`
