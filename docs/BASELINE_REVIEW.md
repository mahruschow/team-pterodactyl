# Baseline review — October 18, 2026

## Repository

- Location: `C:\Users\saada\OneDrive\Documents\team-pterodactyl`.
- Branch: `saadat-dev`.
- Starting commit: `69450d2df193a769bd69af3dae057a2e1a04c28a` — Add PTERODACTYL KiCad design baseline and references.
- Working tree was clean before this task's documentation/reference additions.
- Origin: `https://github.com/mahruschow/team-pterodactyl.git`.
- HEAD and the locally cached `origin/saadat-dev` matched (0 ahead, 0 behind). No fetch was performed, so this does not establish current remote freshness or authentication.
- Current README, design brief and ignore rules read. No AGENTS.md found in the checked ancestor locations or repository search.
- README requires branch work, portable project libraries, exclusion of editor locks/UI settings, and explanations of connector/sensor/pin/power changes.

## Source workbook

Read `C:\Users\saada\Downloads\Budgets.xlsx` directly with the bundled Python runtime and openpyxl, including formulas, cached values, links and cell notes. One sheet: Sheet1. Original remained unchanged.

A byte-identical project reference is saved as `reference/Budgets_2026-10-18.xlsx`.

SHA-256: `a1b6621eb42996d12243888c779e335cfa9c791b8e812494c6bf3cf8ef243fd8`.

Selected products and budget caveats are recorded in DEVELOPMENT_PLAN.md. The part list and totals agree with the supplied handoff. Independent arithmetic verifies the totals; no supplier specifications were newly validated in this step.

## Design and firmware inventory

- Native project, schematic, PCB, symbol library and footprint library tables present.
- Both library tables use `${KIPRJMOD}` relative locations.
- 33 imported footprint files present. Every namespaced footprint referenced by the PCB resolved to a local footprint file.
- Text inspection counted 39 PCB footprints, 417 track segments, zero vias and two zones, matching the README.
- Both firmware ZIPs passed ZIP CRC integrity checks. v19.1 contains the main `PTERODACTYL_v3_8_19_1.ino` sketch and GPS/XBee companion files.
- These are structural/integrity checks. They do not establish symbol correctness, electrical connectivity, physical fit, firmware behavior or schematic/PCB parity.
- Project/schematic/PCB hashes and machine-readable inventory are in `reference/baseline_manifest_2026-10-18.json`.

## Saved design-rule report

The existing report is dated October 7, 2026; it was parsed, not rerun.

| Finding | Count |
| --- | ---: |
| Clearance errors | 11 |
| Text thickness warnings | 134 |
| Text height warnings | 134 |
| Silkscreen overlap warnings | 104 |
| Silkscreen over copper warnings | 37 |
| Library footprint mismatch warnings | 12 |
| Silkscreen edge clearance warnings | 7 |
| Total warnings | 428 |

The report records 0 unconnected pads. It also lists ignored checks, including missing courtyards and footprint-related checks. Several reported clearances are 0.1524 mm against a 0.2000 mm requirement. Do not change rules merely to clear errors; review actual layout and manufacturer limits.

## Tools and native validation

- KiCad was unavailable during the initial inventory. After the user installed it, `C:\Program Files\KiCad\10.0\bin\kicad-cli.exe` reported version 10.0.7.
- Fresh ERC, DRC with in-memory zone refill, and schematic/PCB parity checks were completed on a temporary project copy. Results: 33 ERC errors and 10 warnings; 11 physical DRC errors and 428 warnings; 0 unconnected items; 52 additional parity warnings.
- Parity triage and a native-netlist-to-PCB pad-membership comparison found matching memberships for all 50 assigned PCB nets, allowing three naming differences. The parity warnings still require cleanup; this does not establish correct module pinouts or design intent.
- Original native project/library files were unchanged, verified by hashes for all 41 files. No KiCad rendering or physical test was performed.
- Arduino IDE 2.3.2 is installed. Its bundled Arduino CLI reports version 0.35.3.
- The CLI's default installed-core list contains `arduino:avr` 1.8.6 only. No Teensy core appears there. Other custom toolchain configurations have not been ruled out.
- Firmware has not been compiled. A reproducible Teensy toolchain and the needed libraries remain to be configured before firmware work is validated.

Full findings, inherited ignored checks, command details and raw evidence are in `validation/2026-10-18/VALIDATION_SUMMARY.md` and its adjacent files. Re-run affected checks after schematic and PCB changes.

## Changes made in this step

Added the development plan, this review, an unmodified workbook snapshot, the baseline manifest and native validation evidence under docs/. Updated README and design-brief validation status. No schematic, PCB, firmware or library was modified. No commits, pushes, merges, purchases or fabrication exports were performed.

Status: Step 1 baseline audit complete, including native checks and issue triage. The reported errors and warnings remain unresolved; the design is not approved for manufacture.
