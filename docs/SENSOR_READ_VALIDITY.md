# Sensor read validity — October 20, 2026

Branch `saadat-dev`, starting from `5a22f0b`; firmware **4.0.2-draft**.
Addresses review finding 2 in software. No PCB changes or hardware tests.
The preceding [SD/reset checkpoint](FIRMWARE_RELIABILITY.md) remains implemented.

## Resulting logger behavior

An address ACK no longer suffices for a sensor row to say `OK`. BNO055 rows
require successful quaternion, acceleration, gyro, magnetometer and calibration
transfers. MS8607 rows require successful temperature/pressure conversions and
ADC reads, plus a successful humidity transfer and CRC. Initialization also checks
the MS8607 calibration PROM transfers and CRC.

If any required measurement fails, the logger writes **`READ_FAIL` with all of
that row's measurement fields empty**, increments the relevant failure counter,
and marks that sensor's health false. IMU failures also clear the calibration LED.
The other streams continue. A later successful complete sample restores health
and resumes `OK` rows. `INIT_FAIL` and `NO_RESPONSE` retain their existing meanings.
No CSV columns were added by this checkpoint.

The logger distinguishes an initialized device from its last read's health:
a transient transfer/CRC failure retries sampling on the next scheduled tick
without unnecessarily restarting the driver. Five consecutive IMU failures
still trigger hardware reset. Reset success sets readiness, but health remains
false until a measurement succeeds. Failed initialization retains the preceding
five-second IMU cooldown.

## Driver changes

- **BNO055:** the repository-local driver adds checked quaternion/vector/calibration
  getters that leave caller outputs unchanged on failure. The sketch checks every
  result. Initialization and external-crystal setup now propagate configuration
  write failures as well. Existing conversion factors and output units remain.
- **MS8607:** version 1.0.4 is now repository-local with original license notices.
  Reset, PROM/configuration, conversion and ADC/humidity transfer failures propagate
  to the caller. The existing CRC checks now reach the logger. Requested output
  events are cleared before reading and published only after all requested reads
  pass. Individual Unified Sensor wrappers return the actual result.
- MS8607 repeated initialization reuses its wrapper objects, preventing the former
  allocation leak. Event IDs are initialized and humidity's event type is corrected.
- External library installation now requires only GPS, Unified Sensor and BusIO;
  BNO055 and MS8607 are included under the sketch's `src/` directory.

Upstream source identities/hashes and tested source hashes are in
[validation evidence](validation/2026-10-20/sensor-read-validity/).
The BNO conversion checks retain the register-unit conventions in
[Bosch's BNO055 datasheet](https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bno055-ds000.pdf).
The MS8607 compensation and CRC algorithms remain those in the attributed
Adafruit/TE source, rather than newly derived formulas.

## Validation and limits

The host suite executes the **actual sketch and both local drivers** with fake
BusIO/peripherals. Sixteen parameterized groups cover the ten previous storage/reset
groups plus signed BNO conversion values, failed/short transfers at every sampled
register, configuration failures, MS8607 commands/ADC reads, humidity CRC,
all seven PROM transfers, PROM CRC, wrapper results, empty CSV fields, health/LEDs,
recovery and continued operation of the other sensor stream. Fixtures are synthetic.

The Teensy 4.1 build and host-test logs are in the evidence folder. Run:

```text
python tools/test_firmware_reliability.py --cxx clang++
arduino-cli compile --warnings all Firmware_v4/PTERODACTYL_v4
```

`OK` means the required transfers and available CRC checks succeeded. It does not
prove sensor accuracy, plausible flight values, correct mounting, synchronized
register samples, calibration quality or interference immunity. BNO sample transfers
have no added payload CRC. MS8607 compensation, conversion delays and humidity
scaling are unchanged. Legacy unchecked driver APIs outside the logger's path
are not covered by this guarantee.

**Next:** GPS RMC/GGA freshness and timestamp matching, then CSV analysis.
Real partial-bus faults, sensor resets, SD behavior, rates and simultaneous logging
still need bench/endurance tests. No firmware was uploaded to hardware.
