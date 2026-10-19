# Team planning and handoff

Start here when joining the project or resuming work. This directory contains the shared plan, current status, requirements, session notes and validation evidence. It travels with the repository; no previous chat or access to Saadat's computer is needed to read it.

## Reading order

1. [Current status and resume checklist](CURRENT_STATUS.md) — where we stopped and the next concrete actions.
2. [Version-one requirements](V1_REQUIREMENTS.md) — agreed baseline, proposals and unresolved decisions.
3. [Development plan](DEVELOPMENT_PLAN.md) — the ten steps from imported baseline to tested hardware.
4. [October 18 session notes](sessions/2026-10-18.md) — work completed, decisions and limitations.
5. [Baseline review](BASELINE_REVIEW.md) and [native validation summary](validation/2026-10-18/VALIDATION_SUMMARY.md) — evidence behind the current issue list.
6. [Module connection and mechanical review](SENSOR_CONNECTION_MAP.md) — Step 3 pin map, power/pull-up review, footprint mismatch and remaining verification gates.
7. [Carrier footprint review](FOOTPRINT_REVIEW.md) — three native draft footprints, pad numbering, assembly assumptions and test evidence.

8. [Module assembly proposal and closure gates](MODULE_ASSEMBLY_PLAN.md) — candidate connectors, spacing calculation, symbol validation and M01–M04 evidence checklist.

9. [Teensy drawing comparison](TEENSY_MECHANICAL_REVIEW.md) — supplied PNG, matching nominal geometry, implemented SSW carrier and remaining fit/retention requirements.

10. [Open requests for the team lead](TEAM_LEAD_REQUESTS.md) — plain-language Steps 1–3 summary and the inputs needed to close Step 3 and approve placement.

11. [Placement and interference plan](PLACEMENT_AND_INTERFERENCE.md) — Step 4 draft floor plan, placement/routing rules, estimates and prototype test matrix.

## Directory contents

```text
docs/
  README.md                     Start here
  CURRENT_STATUS.md             Current handoff and next actions
  DEVELOPMENT_PLAN.md            Milestones and completion criteria
  V1_REQUIREMENTS.md             Requirements and decision register
  SENSOR_CONNECTION_MAP.md       Step 3 interfaces and mechanical review
  FOOTPRINT_REVIEW.md            Draft carrier library and approval gates
  MODULE_ASSEMBLY_PLAN.md        Connector/height proposal and closure record
  TEENSY_MECHANICAL_REVIEW.md    Teensy drawing comparison and carrier review
  TEAM_LEAD_REQUESTS.md          Inputs needed from the lead/team
  PLACEMENT_AND_INTERFERENCE.md  Step 4 floor plan, rules and test matrix
  BASELINE_REVIEW.md             Repository/source/tool inventory
  sessions/
    2026-10-18.md                Session record
    2026-10-19.md                Step 4 session record
  reference/
    Budgets_2026-10-18.xlsx       Unchanged supplied parts workbook
    baseline_manifest_2026-10-18.json
    step3-source-manifest.json   Manufacturer CAD commits, URLs and hashes
    step3-cad-geometry.json      Extracted header/outline/hole coordinates
    step3-carrier-pad-map.csv    Carrier-to-manufacturer pad mapping
    step3-gps-cad-history.json   GPS CAD age/revision evidence
  validation/2026-10-18/
    VALIDATION_SUMMARY.md        Findings, triage and commands
    baseline-erc.json            Native schematic check report
    baseline-drc.json            Native PCB and parity check report
    schematic-netlist.xml        Native KiCad-exported netlist
    net-comparison.json         PCB/schematic pad-membership comparison
    step3-footprints/           Native coordinate check, fixture, DRC and SVGs
    step3-symbols/              Sensor pin-contract/GPS logical checks and SVGs
    step3-teensy/               Carrier check, positive/negative DRC fixtures and SVG
  validation/2026-10-19/
    step4-placement/            Draft placement fixture, separation checks, DRC and SVG
```

## Keeping this handoff useful

- Update CURRENT_STATUS.md at the end of a work session: completed work, remaining issues, exact next action and tool limitations.
- Add a dated session note for substantial work. Record files changed, checks performed and decisions with their source. Use a suffix for multiple sessions on the same day if useful.
- Keep DEVELOPMENT_PLAN.md milestone status aligned with CURRENT_STATUS.md.
- Keep requirements and the D01-D10 decision register in V1_REQUIREMENTS.md. Distinguish team decisions from unapproved engineering proposals.
- Save new check reports in a dated validation directory and identify the source commit and KiCad version. Preserve previous reports for comparison.
- Follow the root README's branch and library rules. Do not commit editor lock files, local UI state, scratch copies or authentication data.
- Historical Gerbers and an audit report are not a fabrication approval. Do not infer a passing design from zero unconnected PCB items.

Historical paths and pre-commit statements in the baseline/session evidence describe that point in time. Use CURRENT_STATUS.md and Git history for the current state.
