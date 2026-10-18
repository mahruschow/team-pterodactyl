# Team planning and handoff

Start here when joining the project or resuming work. This directory contains the shared plan, current status, requirements, session notes and validation evidence. It travels with the repository; no previous chat or access to Saadat's computer is needed to read it.

## Reading order

1. [Current status and resume checklist](CURRENT_STATUS.md) — where we stopped and the next concrete actions.
2. [Version-one requirements](V1_REQUIREMENTS.md) — agreed baseline, proposals and unresolved decisions.
3. [Development plan](DEVELOPMENT_PLAN.md) — the ten steps from imported baseline to tested hardware.
4. [October 18 session notes](sessions/2026-10-18.md) — work completed, decisions and limitations.
5. [Baseline review](BASELINE_REVIEW.md) and [native validation summary](validation/2026-10-18/VALIDATION_SUMMARY.md) — evidence behind the current issue list.

## Directory contents

```text
docs/
  README.md                     Start here
  CURRENT_STATUS.md             Current handoff and next actions
  DEVELOPMENT_PLAN.md            Milestones and completion criteria
  V1_REQUIREMENTS.md             Requirements and decision register
  BASELINE_REVIEW.md             Repository/source/tool inventory
  sessions/
    2026-10-18.md                Session record
  reference/
    Budgets_2026-10-18.xlsx       Unchanged supplied parts workbook
    baseline_manifest_2026-10-18.json
  validation/2026-10-18/
    VALIDATION_SUMMARY.md        Findings, triage and commands
    baseline-erc.json            Native schematic check report
    baseline-drc.json            Native PCB and parity check report
    schematic-netlist.xml        Native KiCad-exported netlist
    net-comparison.json         PCB/schematic pad-membership comparison
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
