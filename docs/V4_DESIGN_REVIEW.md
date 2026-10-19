# PTERODACTYL v4 design review

Reviewed October 19, 2026. Branch `saadat-dev`, commit `8933189` (`feat(pcb): first-pass autoroute of the draft v4 board`). Paths below are relative to that repository unless stated otherwise.

**Conclusion: the v4 schematic, placement, initial routing and firmware are substantial draft deliverables, but Steps 1–7 are not all complete. The board is not ready for fabrication.** The repository's `docs/REMAINING_WORK.md` already describes this accurately. The review below distinguishes those acknowledged gaps from additional defects.

## Findings in priority order

### 1. P1 — Missing module footprints and open supply connections prevent a complete board

Location: `Native_KiCad_v4/PTERODACTYL_v4.kicad_pcb`; `docs/PCB_LAYOUT_V4.md`, “Envelopes” and “Clean-up list for hand routing.”

Fresh KiCad DRC with zone refill and schematic parity finds **10 unconnected items** on `+5V` and `/SENSOR_3V3`, plus **missing U2 and U5 footprints**. U2 is the regulator; U5 is the GPS. Their drawn envelopes have no electrical pads. The existing routing therefore cannot provide the complete intended power/GPS circuit. The missing module connections also cannot appear as normal unrouted pad pairs until those pads exist.

The open items include U4 VIN, C6/C8/C9/C10/C11, TP4, and the +5V connections involving TP2 and C4. The routing notes call these six remaining supply connections; the native checker reports ten item pairs. Use the native report and ratsnest when completing them.

**Action:** verify and assign both real module footprints, update the board from the schematic, complete every connection, then refill and require zero unconnected items and zero unexplained parity differences. This is an acknowledged unfinished item, not a newly introduced surprise.

### 2. P1 — Sensor read failures can be logged as valid measurements

Location: `Firmware_v4/PTERODACTYL_v4/PTERODACTYL_v4.ino:218–250`.

The I2C address probe only proves that a device acknowledged at that moment. It does not verify the subsequent register transfers. The installed Adafruit BNO055 1.6.4 implementation discards the read result in `getQuat()` and `getVector()` (library lines 401–410 and 466–474). The sketch then writes `OK` unconditionally. A failed transfer can produce zero or otherwise invalid values without entering the failure/recovery path.

The MS8607 check is also ineffective: installed Adafruit MS8607 1.0.4 `getEvent()` (lines 272–286) ignores `_read()` and `_read_humidity()` results and always returns true. Failed conversions or humidity CRC errors can leave previous measurements in place, which the sketch records as new `OK` data.

**Action:** use a driver interface that propagates individual transfer/conversion/CRC failures; invalidate affected fields, count failures and recover with bounded retries. Inject failures after a successful address ACK to test this. Compilation does not test it.

### 3. P1 — BNO055 reset can stall every logging stream indefinitely

Location: sketch `initImu()` at line 185, called by `setup()`, `resetImu()` and `sampleImu()`.

Installed BNO055 1.6.4 `begin()` checks the chip ID before reset, but its subsequent reset-completion loop at library lines 115–117 has no timeout. If the device responds initially and then fails to return the expected ID after reset, `begin()` never returns. At boot this happens before SD session creation; during recovery it stops GPS service, all sampling, SD flushes and input processing. A completely absent sensor follows a different, bounded path, so an unplugged-at-boot test alone would miss this.

**Action:** bound the driver's post-reset polling and return a failure so the other streams continue. A timeout checked only after `begin()` returns cannot solve an infinite wait inside it. Test loss of the sensor specifically during reset.

### 4. P1 — A failed SD stream opening leaves logging permanently incomplete

Location: sketch lines 148–158; retry condition at line 353; `writeLine()` at lines 90–95.

`openSession()` sets `session`, skips any failed `SD.open()`, and still returns true. For example, if `imu.csv` fails to open, the remaining files may open and `SESSION_START` is recorded, but every IMU write then silently returns because its handle is invalid. The retry logic requires `session < 0`, so it never reopens the missing file. The fault counter/LED does indicate a problem, but the logging LED still uses the nonnegative session number. Likewise, subsequent write failures only increment a counter; they do not transition storage into recovery.

**Action:** make session creation transactional for the required files, close partial handles on failure and restore a retryable state. Define recovery for write/flush failures without overwriting existing data. Test failed opens, full media and card removal/reinsertion; verify file contents and status indications.

### 5. P2 — The advertised battery input range omits the regulator's startup limit

Location: `docs/POWER_ARCHITECTURE.md:52–59`; Step 5 status in `docs/DEVELOPMENT_PLAN.md`.

The architecture describes 2–16 V input and includes a 1S LiPo down to 3.0 V. Pololu specifies **at least 3 V at regulator VIN to start**, with operation down to 2 V only after startup. A battery at 3.0 V leaves no allowance for the fuse, MOSFET, switch, cable or battery sag. A low-battery restart therefore is not guaranteed by the stated range.

**Action:** distinguish running and startup voltage limits, specify the minimum battery voltage under startup load with margin, and confirm battery protection/cutoff and current capability for the selected pack. The available output current also depends on input voltage and temperature; a fixed 1.5 A assumption across the entire range is inappropriate.

Source: [Pololu S9V11F5 product specifications and connection guidance](https://www.pololu.com/product/2836), inspected October 19, 2026.

### 6. P2 — GPS rows can label stale RMC fields as current data

Location: sketch lines 259–269.

Each GGA row merges date, speed and course from the most recently parsed RMC without checking RMC age or matching its measurement epoch. If RMC sentences become missing or invalid while GGA continues, the sketch can keep logging old speed/course/date with fresh GGA timestamps and status `OK`. The installed GPS parser updates speed/course on RMC, not GGA. This contradicts the stated rule that failed or missing values must not be reused as fresh data.

**Action:** track sentence-specific validity and timestamps; associate GGA and RMC by UTC epoch, or expose field age and leave unavailable fields blank. Test valid GGA continuing after RMC loss and a midnight rollover.

### 7. P2 — The placement checker does not remeasure moved footprints

Location: `tools/check_v4_pcb.py:71–75`.

The separation checks read the generated `placement.json`, rather than the current footprints in the PCB. After a manual move, a passing check can still describe the old positions, despite the documentation saying it checks actual placement. This matters now that hand editing is the intended workflow.

**Action:** derive courtyard extents and envelope positions from the loaded board, and test that moving the IMU toward the power region makes the check fail. For this review I independently read the current board geometry: it agrees with the saved placement within 0.005 mm, and all seven separation targets currently pass. This is a checker defect, not evidence that the present placement violates those targets.

## Fresh checks and their limits

| Check | Result |
| --- | --- |
| KiCad 10.0.7 schematic ERC, all severities | 0 violations |
| PCB physical DRC, all enabled checks, zones refilled in memory | 0 violations |
| Schematic/PCB parity | Missing U2 and U5 footprints |
| Unconnected items | 10 |
| Actual board inventory | 49 footprints, 192 track segments, 10 vias; 1249.6 mm track length |
| Actual courtyard separation targets | All seven pass; tightest relevant GPS-to-power gap is 20.70 mm against a 20 mm planning target |
| Routing inspection | No inner-layer tracks; reported I2C maximum net length 110.5 mm against a 150 mm planning target |
| Fresh Teensy 4.1 firmware compilation | Successful using Teensy platform 1.62.0 and the installed documented library versions |
| Hardware tests | Not performed; no assembled-system evidence supplied |

The DRC configuration ignores missing courtyards, off-center track-to-via endpoints, tuning-profile geometry, footprint-filter mismatches and footprint-type mismatches. “Zero physical DRC violations” means zero under those configured checks, not a manufacturing release. The draft checker intentionally tolerates U2/U5 absence and open connections.

The new compile used the installed libraries, not an isolated `--profile` dependency installation. Code-path findings above are source-inspection results, not claims that hardware fault-injection tests were run.

Interference spacing is a planning constraint, not measured performance. The magnetic, GPS, rail-transient, thermal and bus tests in the existing T1–T11 matrix remain relevant. Manufacturer stackup/rules, final battery/cabling, enclosure, sensor exposure and mounting materials must still be settled. No new nominal spacing violation was found in this review.

## Completion assessment

| Step | Review assessment |
| --- | --- |
| 1 — Baseline | Completed and documented |
| 2 — Requirements | Core scope agreed; quantitative mission, power, accuracy and mechanical inputs remain open |
| 3 — Modules/connections | Draft mapping and several verified footprints exist; GPS/regulator footprint work and physical fit/retention remain |
| 4 — Interference/placement | Planning and test matrix drafted; current separations pass; assumptions and team acceptance remain open |
| 5 — Power/schematic | ERC-clean draft; startup specification, candidate ratings, selected battery and design review remain |
| 6 — Firmware | Compiles; fault-handling defects above and hardware/log validation remain |
| 7 — PCB layout | Placement and first autoroute exist; missing footprints, open supplies, routing cleanup, silkscreen, manufacturer and mechanical checks remain |

Suggested next order: close regulator/GPS footprint geometry; settle the power input contract; complete and review routing; correct firmware failure handling in parallel; then run clean native checks and hardware tests before declaring the relevant steps complete. Some team decisions can remain tracked while independent work continues, but cannot be replaced by DRC or compilation.

Hardware and firmware source were left unchanged during the review. Fresh review evidence is preserved in [validation/2026-10-19/v4-design-review](validation/2026-10-19/v4-design-review/). This report and its evidence are published in a subsequent documentation-only commit at Saadat's request; findings describe reviewed commit `8933189`.
