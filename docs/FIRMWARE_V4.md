# Step 6 — v4 logger firmware

Updated October 20, 2026. Firmware **4.0.1-draft**; [SD/BNO reliability checkpoint](FIRMWARE_RELIABILITY.md). Originally prepared October 19, 2026. Working branch: `saadat-dev`. Status: **draft written and compiled for Teensy 4.1; not yet run on hardware.**

Source: [Firmware_v4/PTERODACTYL_v4/](../Firmware_v4/PTERODACTYL_v4/). Pins and rates live in `config.h`; the logger is `PTERODACTYL_v4.ino`.

## Why a new sketch instead of porting v19.1

The v3.8 v19.1 firmware is written for hardware v4 drops: u-blox M8N/M9N (binary UBX), XBee, OLED, LSM9DS1, MS5611, thermistors and the heater. It also waits for user input during startup, and its GPS setup changes the shared data delay (Step 2 finding). Porting it would mean removing most of it. The new sketch keeps the useful ideas: a CSV log on the built-in SD card, a numbered file per power-up, voltage reading, button and switch inputs, and status LEDs. It is written for the v4 schematic and the logging requirements LOG-01 to LOG-07 in V1_REQUIREMENTS.md. The legacy archives are unchanged.

## What it does

| Area | Behaviour | Requirement |
| --- | --- | --- |
| Startup | Starts logging automatically. Never waits for USB, a button or a GPS fix. Retries after missing card or detected storage faults, with a 5 s pause. | LOG-01 |
| Sessions | Each power-up creates a new folder `S000`–`S999`. Requires all headers and metadata to write/sync before activating; recovery gets a new folder. Exclusive file creation prevents deliberate overwrite; if all 1000 exist it refuses and shows a fault. | LOG-01, LOG-07 |
| Streams | `imu.csv` 10 Hz; `env.csv` 1 Hz; `gps.csv` one row per GGA (1 Hz); `health.csv` 1 Hz; `events.csv`; `meta.txt` | LOG-04 |
| Every record | Session number, per-file sequence number, `t_ms` (Teensy millis, monotonic), status (`OK`, `NO_RESPONSE`, `INIT_FAIL`, `INIT_WAIT`, `READ_FAIL`, `NO_FIX`) | LOG-02 |
| Bad data | Known absent/init-failed readings are empty. **Transfer/CRC failure propagation and GPS RMC freshness remain unresolved**; some failures can still be logged as OK. | LOG-03 |
| Timing | Independent schedules. Late or missed periods are counted as `overruns` in health. | LOG-05 |
| Writes | Files stay open; sync is scheduled every 1 s. Checked write/sync faults close the session, latch red and trigger a fresh-folder retry. Blocking operations can delay sync. | LOG-06, LOG-07 |
| Clean stop | Mode switch (SW1, pin 30) to GND requests checked close of all files. Close errors latch a fault; USB reports the result. Switching back starts a new session. If the switch is in the stop position at power-up, logging does not start. | LOG-06, D10 proposal |
| Markers | Button (pin 31) writes a `BUTTON` event. Removing the pull-before-flight jumper (pin 32) writes `PBF_REMOVED`, a launch marker. Neither changes logging. | D10 proposal |
| BNO055 recovery | Each sample checks that the IMU answers on I2C. After 5 consecutive failures it pulses IMU_RST (pin 9) and re-initialises. The reset pulse/boot delay alone is 701 ms; initialization adds time. Post-software-reset polling is bounded at 1000 ms plus in-flight I2C latency. Failed initialization has a 5 s cooldown (`INIT_WAIT`). Total reset blocking time is logged in `IMU_RESET`. | LOG-03 |
| Units | Quaternion; acceleration m/s² including gravity; gyro **rad/s** (converted from the library's deg/s); magnetometer µT; pressure **Pa** (from the library's hPa); temperature °C at the sensor; humidity %RH; GPS altitude m above mean sea level; speed m/s (from knots). | LOG-04 |
| Pressure altitude | ISA model, 44330 × (1 − (p/101325)^0.190295). Model and reference pressure are written to `meta.txt`. | Step 2 |
| GPS | PA1616D at 9600 baud, RMC+GGA at 1 Hz (PMTK commands sent once, without waiting). Accepts combined-constellation `$GN` sentences. Checksum failures are counted. | Step 3 |
| Battery | `vbat_v` = ADC (12-bit, 16-sample average) × 3.3 / 4095 × 122/22. | Step 5 |
| I2C | 100 kHz (Step 4 rise-time estimate). | PC11 |

### Status LEDs

| LED | Pin | Meaning |
| --- | --- | --- |
| Red (STATUS1) | 2 | Fault: not logging (unless cleanly stopped), IMU or environment sensor not OK, or any detected storage fault since boot |
| Yellow (STATUS2) | 3 | GPS fix with a GGA received in the last 3 s |
| Green (STATUS3) | 4 | Blinks at 1 Hz while logging |
| Orange (STATUS4) | 5 | BNO055 system calibration = 3 |

All four LEDs light briefly during startup as a lamp test.

### USB serial

At 115200 baud the sketch prints one status line per second and each event, but only when a USB serial connection is open. Remember the Teensy's VUSB/VIN pads must be cut on the v4 board (POWER_ARCHITECTURE.md).

## Build

Toolchain used (October 19, 2026): Arduino CLI 0.35.3 (bundled with Arduino IDE 2.3.2), Teensy platform `teensy:avr` 1.62.0 from `https://www.pjrc.com/teensy/package_teensy_index.json`, repository-local patched Adafruit BNO055 1.6.4, Adafruit MS8607 1.0.4, Adafruit GPS Library 1.9.0, Adafruit Unified Sensor 1.1.15 and Adafruit BusIO 1.17.4. External dependencies are pinned in [sketch.yaml](../Firmware_v4/PTERODACTYL_v4/sketch.yaml).

- **Arduino IDE:** add the PJRC URL under Preferences → Additional boards manager URLs, install "Teensy" and the four external libraries (MS8607, GPS, Unified Sensor and BusIO) at the versions above; the patched BNO055 source is included in the sketch, select Teensy 4.1, then open `PTERODACTYL_v4.ino`.
- **Command line:** with the same platform and libraries installed, run from the repository root:

```bash
arduino-cli compile --warnings all Firmware_v4/PTERODACTYL_v4
```

The sketch's `default_fqbn` selects Teensy 4.1. `arduino-cli compile --profile teensy41` would build in an isolated environment with exactly the pinned versions. It downloads its own copies, and was not run here.

**Original October 19 result (before reliability changes):** compiled with **0 warnings** at `--warnings all`. Teensy 4.1 memory: 113 KB code of 8 MB flash; 373 KB RAM1 and 512 KB RAM2 free. Log: [build.log](validation/2026-10-19/step6-firmware/build.log). The .hex embeds the build date and time, so its hash changes on every build and is not recorded.

The October 20 reliability build also passes for Teensy 4.1 with **0 warnings**. Ten host fault-injection groups pass against production code using fake peripherals. See [current evidence](validation/2026-10-20/firmware-reliability/); these tests do not replace hardware validation.

## What has not been verified

Compiling proves only that the code builds. None of the following has been tested yet:

- Running on a Teensy with the BNO055, MS8607 and PA1616D connected (Step 6 bench test, needs R1).
- I2C reliability at 100 kHz with both breakouts, BNO055 clock stretching, and the reset/recovery path.
- GPS sentence mix and rate on the real PA1616D, and whether the PMTK commands are accepted.
- SD write latency, flush timing and power-loss behaviour with the chosen card (LOG-06).
- Achieved rates over a long run: target within 1 % of schedule, with overruns counted (LOG-05, RUN-01).

These are the Step 6 bench checks, and later the T5–T7 checks. An independent log-parsing script (LOG-04 verification) is still to be written once real session files exist.

## Open decisions this firmware assumes

- D03 rates and accuracy: 10 Hz/1 Hz are proposals in `config.h`.
- D10 controls: the clean-stop switch, button marker and PBF marker are proposals; change them if the lead specifies a launch workflow.
- D09 acceptable data loss: the 1 s flush is a starting point, not a power-loss guarantee.
- BNO055 axis mapping: uses the default sensor axes. Record the mounting orientation (PC8) and add an axis remap if needed.
