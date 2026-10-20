# Firmware reliability checkpoint — October 20, 2026

Branch `saadat-dev`; based on `e1663f7`. Firmware version **4.0.1-draft**.
This addresses software paths in review findings **3 (BNO reset)** and
**4 (SD sessions)**. Hardware validation remains open. PCB files are unchanged.

## SD recovery

`storage.cpp` owns the five required CSV files and the session lifecycle.
Logging becomes active only after all headers and `meta.txt` are written and
synced successfully. Open/header/metadata failures close partial handles and leave
logging inactive. Partial folders are retained for diagnosis.

Short writes, missing handles, sticky write errors and failed `sync()` calls
invalidate the session. The logger retries mounting/creating a session after five
seconds, unless the stop switch is active. Recovery uses a new unused `S000`–`S999`
folder with exclusive file creation; old files are never deliberately overwritten
or deleted. Exhausting all 1000 numbers leaves logging inactive.

The sketch now uses Teensy's `FsFile` API because its `sync()` and `close()` return
success/failure; the previous `File::flush()` wrapper returned no status.
File-failure counters persist across sessions. `storage_fault_total` is appended
to `health.csv` and USB diagnostics and includes mount/session failures. It counts
detected fault operations, not unique incidents. The red fault LED stays latched
until reboot even after logging resumes; green blinks only for an active session.

The mode switch records `STOP_REQUEST` before closing. USB reports `SD_STOP_OK`
only if the session was active and close succeeded, otherwise
`SD_STOP_FAILED_OR_INACTIVE`. A stop event is not proof that data reached the card.

**Limits:** there is no outage buffer or replay. A failed record may be partial;
inspect the tail of interrupted CSVs. Sync success is the library's result, not
a guarantee against card failure or sudden power loss. SD operations and IMU
initialization are still blocking; the one-second sync schedule is a target,
not a maximum data-loss interval.

## BNO055 reset recovery

The repository includes Adafruit BNO055 1.6.4 source and license under
`Firmware_v4/PTERODACTYL_v4/src/bno055/`. Its patched `begin()` checks the reset
write and polls CHIP_ID for up to **1000 ms**, counting elapsed time with unsigned
rollover-safe arithmetic. A failed read cannot satisfy the ready check.

The budget applies to post-reset polling, with possible overshoot for a bus
transaction already in progress. Detection/configuration delays and the hardware
reset's 701 ms pulse/boot delay are additional. Teensy Wire's bounded transactions
are required; this is not a nonblocking driver.

After an initialization attempt, a failed IMU gets a **five-second cooldown**.
Rows during that wait contain `INIT_WAIT` and empty measurements. Other streams
can run between attempts. Actual failures still increment the failure counter;
waiting itself is not counted as another failed transfer.

## Validation and next work

Evidence: [firmware validation](validation/2026-10-20/firmware-reliability/).
The host suite compiles the actual sketch, storage, metadata and patched BNO
source with fake peripherals. It tests required-file failure/cleanup, metadata
failure, partial writes, sync/close failures, missing card and handles, exclusive
creation, folder exhaustion, retry timing/rollover, clean-stop suppression,
post-reset timeout/read/write faults, cooldown and startup continuation.

Run from the repository:

```text
python tools/test_firmware_reliability.py --cxx clang++
arduino-cli compile --warnings all Firmware_v4/PTERODACTYL_v4
```

The host runner also accepts `g++` or a Zig executable (`zig c++`); C++17 is required.
No hardware is accessed by these tests. The Teensy build uses the installed
1.62.0 platform and dependencies; an isolated `--profile` installation is not tested.

**Still open:** propagate BNO055/MS8607 transfer and CRC failures (review finding
2), reject stale/mismatched GPS RMC fields (finding 6), and add a CSV analysis tool.
Then run real missing/full-card, removal/reinsertion, power-loss, reset, simultaneous
logging and endurance tests. No complete-system hardware testing has occurred.
