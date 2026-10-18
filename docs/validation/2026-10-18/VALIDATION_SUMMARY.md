# KiCad baseline validation — October 18, 2026

KiCad **10.0.7** ran against a temporary copy of the complete native project from branch `saadat-dev`, starting commit `69450d2df193a769bd69af3dae057a2e1a04c28a`. All 41 original native-project/library/report files were checked by SHA-256 before and after and remained unchanged. This audit establishes the current issues; it does not resolve them or approve fabrication.

## Results

| Check | Errors | Warnings | Other result |
| --- | ---: | ---: | --- |
| Schematic electrical rules (ERC) | 33 | 10 | 43 findings |
| PCB design rules (DRC), with zone refill | 11 | 428 | 0 unconnected items |
| Schematic/PCB parity | 0 | 52 | Listed separately from the 439 DRC findings |

Both check commands returned exit code 1 because violations were found and `--exit-code-violations` was enabled. They completed and produced reports. There were no findings marked as exclusions in the returned reports; ignored check categories remain listed below. Zone refill occurred in memory on the temporary copy; `--save-board` was not used.

## Schematic findings and treatment

| Finding | Count | Interpretation and next action |
| --- | ---: | --- |
| Unconnected pins | 30 errors | Includes Teensy pins 27/33/36/37, MS5611 PS/SDO/CBS, switch contacts, regulator controls and alternative GPS pins. Review exact component requirements and chosen population before adding deliberate no-connect markers or wiring. Do not suppress every unused-pin report indiscriminately. |
| Power inputs without a recognized power-output driver | 3 errors | 3V3, GND and +5V power symbols are affected. This can reflect imported symbol electrical types or missing declarations; it is not by itself proof that the physical board has no supply. Trace the actual sources before correcting symbols or adding power flags. |
| Labels connected to only one pin | 2 warnings | `GND_1` and `5V`. Investigate their intended relationships to other ground/power nets; do not merge them based on their names. |
| Unconnected wire endpoints | 8 warnings | Inspect exact endpoints and remove obsolete stubs or restore intended connections during schematic cleanup. |

The report includes symbols whose pins are modeled as bidirectional. Automated checks can only apply the supplied pin types, so a clean future ERC must still be supported by a datasheet-based pin review.

## PCB findings

The fresh physical DRC reproduces the October 7 report's counts and categories exactly:

| Finding | Count |
| --- | ---: |
| Clearance errors | 11 |
| Text thickness warnings | 134 |
| Text height warnings | 134 |
| Silkscreen overlap warnings | 104 |
| Silkscreen over copper warnings | 37 |
| Library footprint mismatch warnings | 12 |
| Silkscreen edge clearance warnings | 7 |

Clearance findings include 0.1524 mm spacing where the project requires 0.2000 mm. Resolve through layout review and manufacturer requirements, not an arbitrary rule reduction. Review the 12 library mismatches before updating footprints to avoid overwriting intentional board-specific edits.

## Schematic/PCB parity triage

| Finding | Count | Evidence |
| --- | ---: | --- |
| Net conflicts | 34 | 29 pads have no PCB net but receive schematic-generated `unconnected-(...)` names. Four pad findings involve two differently named two-pad power nets. One involves a single-pad switch net. |
| Missing symbol fields in footprints | 8 | Missing `CATEGORY` fields on four LEDs and four resistors. |
| Value mismatches | 4 | The four resistor footprints carry values resembling reference names while their schematic value fields are empty. Clean component references/values and BOM consistently. |
| Extra PCB footprints | 6 | `U$32` AXIS graphic, `U$30` PTERODACTYLV3.1 graphic, and `U$18/U$19/U$20/U$21` HOLE footprints. Review appropriate board-only classification rather than deleting these features. |

To investigate the net warnings, a native KiCad XML netlist was exported and its sets of (component reference, pin number) were compared with each PCB net's (footprint reference, pad number) set. All **50 assigned PCB nets** have matching schematic pad membership, allowing the following three name differences:

| PCB name | Schematic name | Pad members |
| --- | --- | --- |
| `VCC_2` | `Net-(U$7-PadVIN)` | U$7 VIN, U$8 VIN |
| `VCC_3` | `Net-(U$5-PadVIN)` | U$5 VIN, U$7 VOUT |
| `N$14` | `unconnected-(U$26-PadNO)` | U$26 NO only |

The schematic has 79 nets, including generated single-pin unconnected nets. This comparison supports an import/naming explanation for these warnings; it does not make the parity report clean or verify physical pin numbering, internal module circuitry, correct power architecture, or suitability of unused pins. No unexpected multi-pad membership mismatch was detected in this comparison.

## Check coverage limitations

DRC inherited these ignored project checks: missing courtyard; track endpoint not centered on via; tuning profile track geometries; footprint/symbol filter mismatch; footprint type/pad mismatch.

ERC inherited these ignored project checks: single global label; four-way junction; SPICE model issue; footprint-filter mismatch.

`--severity-all` includes error, warning and excluded findings, but does not enable ignored check categories. Project settings were preserved. The audit did not include 3D fit, manufacturer footprint verification, interference measurement, firmware compilation or physical tests.

## Reproduction

Use a disposable copy containing the `.kicad_pro`, schematic, PCB and local libraries. With KiCad 10.0.7 CLI, run from that copied project directory:

```powershell
& 'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe' sch erc --format json --severity-all --exit-code-violations --output baseline-erc.json PTERODACTYL_v3.8_v11.kicad_sch
& 'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe' pcb drc --format json --severity-all --schematic-parity --refill-zones --exit-code-violations --output baseline-drc.json PTERODACTYL_v3.8_v11.kicad_pcb
& 'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe' sch export netlist --format kicadxml --output schematic-netlist.xml PTERODACTYL_v3.8_v11.kicad_sch
```

Raw ERC and DRC reports, the exported netlist and net-comparison evidence are saved alongside this report in the repository. Report timestamps are tool-generated; the review date above follows the user's local date.

## Next work

Step 1's baseline audit is complete. Step 2 is to record the version-one feature decisions and required measurement behavior. Step 3 then verifies the selected modules and builds the pin/power/footprint map. Carry these findings into schematic cleanup and layout work, prioritizing power and pin correctness before cosmetic warnings. The Teensy firmware toolchain remains a later prerequisite; no firmware compilation was performed here.
