# Power, cost and mass budget — October 20, 2026

## Team-name silkscreen update — October 21, 2026

Saadat Muyeen, Mahrus Chowdhury and Ryeed Zaman are now on the back silkscreen, with 2 mm text and 0.30 mm strokes. Fresh DRC, connectivity and schematic-parity checks report zero issues. All original PCB bytes are retained; only three text objects were added. The other eight Gerber layers match the prior geometry exactly, apart from export timestamps. Existing ERC evidence remains applicable to the unchanged schematic.

**Order the updated native PCB or fabrication ZIP. AISLER TCVOYNZG revision 1 is superseded and does not contain the names.** Two revision-upload attempts failed; the alternate upload form says an anonymous project is already in progress and requires login to save it. Sign in and upload the updated board, then inspect the bottom preview before ordering. No new AISLER revision or order has been created. Earlier statements below about revision 1 being the exact current PCB or ready for checkout refer to the previous checkpoint.

## First prototype scope and order checkpoint - October 21, 2026

**Current authority: [FIRST_PROTOTYPE_RELEASE.md](FIRST_PROTOTYPE_RELEASE.md).** PCB checks and AISLER upload/preview passed; project TCVOYNZG revision 1 is ready for checkout. FB1/SW1/SW2/J3 are selected for P1. The user explicitly excludes physical testing, flight qualification, subsequent redesign and casing from this phase; older statements requiring those before PCB fabrication are superseded. Assembly receipt/polarity checks remain part of building the prototype. No order placed. Updated known cost is USD 129.37 (15 price lines missing); entered mass 170.25 g (three missing). The provisional EUR board quote is separate.

**Current implementation — October 21:** Targeted component/connector/capacitor edits and the budget update are now applied. Fresh ERC/DRC/connectivity/parity and preservation checks pass. Read [RESUME_HERE.md](RESUME_HERE.md), then [COMPONENT_IMPLEMENTATION.md](COMPONENT_IMPLEMENTATION.md) for the authoritative boundary. Four BOM references remain explicit candidates; holder/harness fit, cold runtime and flight qualification remain open. Earlier dated figures and research-only statements below are historical where superseded.

## Current budget revision — component implementation

The live budget was rebuilt in session `document_21d90808-743d-456b-8775-87ca5a43cfea` because the previous chat artifact was unavailable. `tools/create_budget_workbook.js` reproduces it into a NEW workbook. Do not rerun creation into a populated workbook. A checked Excel export accompanies the review package.

Current modeled battery input is **1.618301 W average / 3.567647 W peak**, using 85% conversion and a provisional 90% path efficiency (replacing the earlier optimistic 97%). Three hours consumes 4.854902 Wh; the 25% reserve and 70% usable allowance produce **8.669468 Wh / 1.444911 Ah at nominal 6 V**. Actual cold usable energy should cover at least 6.068627 Wh including that reserve at the tested load/cutoff. All current, efficiency and cold-capacity assumptions remain unmeasured.

Battery: four L91 cells + BH4AAW holder, 75.05 g combined estimate. SD: Kingston SDCIT2/8GB, still 30/200 mA provisional load. Selected LEDs use mean typical Vf 1.8125 V, 680 ohm and a separate 3 mA/LED peak allowance. Minimum loaded pack voltage remains blank pending testing. The added 1-ohm path screen produces 2.888 V at the regulator from a 4 V pack during modeled peak demand, below its 3 V startup requirement.

**Entered mass: 170.25 g**, including allowances; three missing mass lines (module interconnects, enclosure, integration). **Known price: $118.30**, 16 unpriced lines; TP hardware intentionally zero, J4 DNP. Complete totals remain `Incomplete`. No newly invented procurement prices were entered. `validation/2026-10-21/component-finalization/budget-check.json` records reconciliation and energy-balance checks. See COMPONENT_IMPLEMENTATION.md for sources, assumptions and limits.

The prior budget below is retained as the October 20 historical model; it is not the current workbook state.

The budget uses **three hours of total powered runtime**, confirmed by Saadat on October 20, 2026. Estimated consumption is **4.48 Wh**, giving an **8.01 Wh nameplate battery-energy target** with the proposed 25% reserve and 70% usable-energy allowance. The battery assembly, cold-performance verification, complete purchasing cost and complete installed mass remain open; the minimum battery temperature is confirmed as -40 C. No hardware was ordered or tested, and this budget work does not change the PCB or firmware.

## Lead's updated direction

**Latest update, October 20:** the lead specifies **-40 C minimum** for battery selection, superseding the -45 C screening assumption. Runtime remains three hours. Saadat confirms sensors will be through-hole soldered and the casing will be CAD-designed around the completed PCB layout. Sensor sockets are superseded by soldered headers; exact header lengths and clearances remain unverified. The earlier 10.5 g interconnect allowance has been withdrawn, leaving **97.2 g of entered mass and four missing mass lines** (interconnects, battery/protection, enclosure and integration). This is an incomplete subtotal, not a measured reduction in assembly mass. The five-module price subtotal remains $118.30; 17 price lines remain open.

Power!B35 records -40 C with the lead reply as its source. The 70% usable-energy assumption has not been validated at this temperature; the 8.01 Wh nameplate target is unchanged and provisional. With the proposed 25% reserve, the selected pack should demonstrate at least 5.61 Wh usable at the relevant cold load/cutoff conditions, plus adequate startup and peak-current capability. Battery research now recommends four series Energizer L91 cells; the complete pack/holder is not finalized, and nothing has been ordered. See COMPONENT_FINALIZATION_RESEARCH.md. These recommendations have not been entered into the live workbook.

Saadat supplied the lead's reply: create power, cost and mass budgets, then choose a battery from the power requirement. Nothing has been ordered. Dimensions should be as small as possible while retaining functionality. Battery selection is therefore a design-team task; the lead is not required to nominate a pack. Saadat subsequently confirmed three hours of total powered runtime. The minimum battery temperature is -40 C. AISLER is selected, no spending cap applies, and mass should be minimized without a supplied hard ceiling. Mounting and whole-assembly thermal performance still need engineering closure.

The supplied `New Budgets.xlsx` is a reference for a different payload with particle sensors, pumps, heaters and a Teensy 4.0. Its two-hour calculation and 37 Wh battery are not requirements for this logger. Its `Have` entries are not free parts available to this project. The original file was read without modification:

- Source: `C:\Users\saada\Downloads\New Budgets.xlsx`
- SHA-256: `C2B65D32B46A4DA5645E785A789C996A97B67B21F26677223E3174541B781F4D`
- Reference totals: 15.336475 W / 30.67295 Wh at two hours; estimated 903.3 g / actual 902 g for that other payload. PMS5003 quantity differs between its power and cost/mass sheets; do not inherit those totals.

## Workbook and reproducibility

The live workbook in this Codex chat contains **Budget summary**, **Power**, and **Cost and mass**. Artifact reference: `artifact_FUIBR-EQUnXhhV3JS2j9rrmri3HwRDLQ`. It is not an exported Excel file committed to Git. Teammates can use the complete assumptions/results below without access to the chat. The creation source is [tools/create_budget_workbook.js](../tools/create_budget_workbook.js); run it in a new Artifact Session spreadsheet, not an existing populated workbook. It creates new sheets. Future workbook changes must also update this source and the dated record.

Amber cells are editable assumptions; missing cost/mass cells are highlighted. Sources and the distinction between published values and allowances are beside the inputs. Missing values keep complete totals marked `Incomplete`. The summary's team-review statuses are a dated manual record, not automatic approvals.

## Power inputs and method

The baseline assumes Teensy 4.1 at 600 MHz with continuous logging, the three specified breakouts, internal GPS antenna and four status LEDs. No telemetry, heater or actuator is included. **All load-current values below are planning allowances, not measured or guaranteed maxima.**

| Load | Rail | Quantity | Average mA per unit | Peak allowance mA per unit |
| --- | --- | --- | --- | --- |
| Teensy base, excluding card and external loads | 5 V | 1 | 150 | 250 |
| microSD, exact card unselected | 3.3 V | 1 | 30 | 200 |
| BNO055 #2472 breakout | 3.3 V | 1 | 20 | 25 |
| GPS #5440 breakout | 3.3 V | 1 | 35 | 50 |
| MS8607 #4716 breakout | 3.3 V | 1 | 2 | 5 |
| Status LEDs, 680 ohm and assumed 2 V Vf | 3.3 V | 4 | 1.912 | 1.912 |
| I2C/control pull-ups | 3.3 V | 1 | 1 | 3 |

The Teensy supplies these 3.3 V loads through a linear regulator, so their current also appears approximately unchanged at its 5 V input. Simply summing sensor output watts would omit that regulator's heat. The table's device-power subtotal is 1.065635 W; the correct modeled **5 V supply load is 1.228235 W average and 2.703235 W peak**. Added 5-to-3.3 V regulator heat is 0.1626 W average / 0.4941 W peak, already included in those figures.

Editable conversion assumptions: 85% buck-boost efficiency, 97% upstream protection/wiring efficiency, 5 mW battery-side bias/leakage allowance, 70% usable battery energy and 25% additional energy reserve. These are proposed allowances; the usable fraction is not a validated cold-temperature derating. Converter quiescent consumption is included in the efficiency assumption, not separately added again.

```
Battery input W = (5 V load W / 0.85 + 0.005 W) / 0.97
Required nameplate Wh = battery average W × powered hours × 1.25 / 0.70
Required nominal Ah = required nameplate Wh / selected pack nominal V
Peak battery A = peak battery W / minimum pack terminal V
```

Calculated battery input: **1.494828 W average / 3.283791 W peak allowance**. The required nominal energy is 2.669335 Wh per powered hour under these assumptions.

| Example powered duration | Energy consumed | Nameplate energy target with allowances |
| --- | --- | --- |
| 2 h | 2.99 Wh | 5.34 Wh |
| 3 h | 4.48 Wh | 8.01 Wh |
| 4 h | 5.98 Wh | 10.68 Wh |
| 6 h | 8.97 Wh | 16.02 Wh |

Saadat subsequently confirmed three hours of runtime. Power!B31 is now 3, and Power!D39 plus the summary's required target recalculate to 8.008004597 Wh. The other durations remain comparison cases. Treat the three hours as total powered operation, including preparation and recovery wait; energy reserve is applied separately. Pack voltages remain blank because no battery has been selected.

## Power findings to close

**Altitude update from Saadat, October 20:** expected altitude is about 30,000 ft; battery/PCB mounting is not yet known. The [NWS standard-atmosphere table](https://www.weather.gov/index.php/ama/conversions) gives approximately -44.5 C at 30,000 ft. This is an ambient reference, not a mission weather bound or a measured battery/board temperature. Enclosure insulation, solar exposure and internal dissipation affect component temperature; see [NASA's balloon payload thermal explanation](https://lambda.gsfc.nasa.gov/product/websites/TOPHAT/topweb.gsfc.nasa.gov/balloon/inside.html). Keep the usable-energy fraction provisional. BOM research and power review can continue before mounting is settled; final board outline/holes, battery retention, connector access and thermal verification must be resolved before fabrication release. No heater or battery change is authorized by this altitude estimate alone.

1. The current 0.7 A PTC hold rating needs a time-current and temperature review. At example pack terminal voltages of 3.0 / 3.7 / 5.0 / 7.4 V, modeled peaks are 1.095 / 0.888 / 0.657 / 0.444 A. Hold current is not an instantaneous trip threshold; these comparisons neither prove a trip nor approve a fuse.
2. The S9V11F5 needs at least 3 V at its input for startup, after upstream drops and sag. A pack at 3 V leaves no margin. Its startup/current-limit behavior, continuous output versus input voltage, protection, cutoff, connector and capacitor ratings must be checked together.
3. External 3.3 V loads total 65.65 mA average / 90.65 mA peak, below PJRC's 250 mA external-use guidance on paper. Including the onboard SD card gives 95.65 / 290.65 mA of added regulator load. That combined value is not an external-pin measurement; total onboard regulator heating and processor load still need validation.
4. Select an exact microSD card and verify its write/startup current. The 200 mA placeholder is not a guaranteed card limit. Measure complete firmware startup, GPS acquisition, SD writes and steady logging at relevant voltage/temperature.
5. Choose a pack only after duration/environment are established and startup/current/cutoff/cold-capacity behavior has been checked. Include pack protection and a compatible charging method. No battery purchase is implied.

## Cost and mass

Prices below are the manufacturer-store snapshot checked October 20, 2026, before shipping/tax or quantity discounts. Verify price and stock when ordering.

| Module | Unit price USD | Mass g | Mass basis |
| --- | --- | --- | --- |
| Teensy 4.1 DEV-16771 | 31.50 | 7 | Engineering allowance |
| BNO055 #2472 | 34.95 | 3 | Published product mass |
| MS8607 #4716 | 14.95 | 2 | Engineering allowance |
| GPS #5440 | 29.95 | 9 | Published product mass |
| S9V11F5 #2836 | 6.95 | 0.5 | Published, without pins |
| **Five priced modules** | **118.30** | **21.5** | Mixed published/allowance |

The workbook contains 22 purchasing lines. **17 cost lines remain unpriced**: PCB, sockets/headers, passive/protection lot, LEDs, carrier connectors, onboard controls, test points, SD card, external switch, wiring, retention hardware, battery/protection, enclosure, insulation/vent/mounting, shipping/minimum-order extras, tax/duties and spares/rework. The full procurement total remains `Incomplete`.

The **107.7 g subtotal is provisional**, with 12.5 g from published module masses and the rest from engineering allowances. Additional allowances are: PCB 35 g; seven mating header/socket rows 10.5 g; passive/protection lot 8 g; four LEDs 1.2 g; four carrier connectors 4 g; two onboard controls 2 g; ten test points 1 g; SD 0.5 g; panel switch 4 g; wiring 10 g; retention hardware 10 g. Battery/protection, enclosure and insulation/vent/payload mounting have **no mass input yet**. Shipping, taxes and uninstalled spares have zero flown mass, intentionally. Weigh installed assemblies and avoid counting included headers twice before calling this a measured mass budget.

## Source evidence

- [PJRC Teensy 4.1](https://www.pjrc.com/store/teensy41.html): 5 V input, onboard 3.3 V regulator and external-current guidance. Its power prose mentions Teensy 4.0; no 4.1 guaranteed maximum was inferred from that statement.
- [SparkFun Teensy 4.1](https://www.sparkfun.com/teensy-4-1.html): DEV-16771 price.
- [Adafruit BNO055 #2472](https://www.adafruit.com/product/2472): price and board mass. [Bosch product selector](https://www.bosch-sensortec.com/media/boschsensortec/downloads/promotion_material/product-selector-en.pdf): BNO055 12.3 mA chip-level 9DOF current; whole-breakout allowances are higher.
- [Adafruit MS8607 #4716](https://www.adafruit.com/product/4716): exact breakout and price; its sensor low-power figure is not treated as whole-board consumption.
- [Adafruit GPS #5440](https://www.adafruit.com/product/5440): price, mass, 29 mA tracking / 34 mA acquisition reference figures. Budget includes additional allowance.
- [Pololu S9V11F5 #2836](https://www.pololu.com/product/2836) and [specifications](https://www.pololu.com/product/2836/specs): price, startup, voltage/load-dependent conversion, mass without pins and no built-in low-voltage cutoff. The typical efficiency range is not a guaranteed worst-case floor; availability may require backorder.

## Validation and next actions

The live workbook recalculated and passed **22 checks**: independent baseline arithmetic; controller-average and SD-peak perturbations; runtime/voltage capacity propagation; PTC review output; missing-price and missing-mass counts; incomplete totals; newly entered quotes; completion only after every mass input; missing-load and zero-efficiency guards; restoration of all original inputs. The final scan found no spreadsheet formula errors. All three sheets and source notes were rendered and visually reviewed. At the initial validation checkpoint, test values were removed and runtime/pack fields were blank. After Saadat confirmed three hours, the runtime input and required target were recalculated and checked; pack fields remain blank. Evidence: [budget-check.json](validation/2026-10-20/budget-check.json).

Next work, in order:

1. Team: powered duration is confirmed at three hours. Establish minimum/maximum operating temperatures and any cost/mass or mounting limits. Select required sample rates and start/stop workflow if these affect power.
2. Design team: select the SD card and compare candidate packs against the energy, minimum-voltage/startup, peak-current, temperature, protection and mass requirements. Review the PTC and complete power-path component ratings alongside the battery.
3. Complete exact MPNs, assembly hardware and supplier/fabrication quotes. Replace provisional masses with supplier evidence or measured installed values.
4. With pack and hardware dimensions known, review a smaller enclosure/board arrangement without sacrificing antenna exposure, magnetic spacing, ventilation, retention or USB/SD access.
5. Finish independent schematic/layout and manufacturer checks, inspect fabrication outputs, then prototype and measure. The existing clean KiCad checks do not replace these steps.
