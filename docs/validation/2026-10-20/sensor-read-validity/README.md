# Sensor-read validation — October 20, 2026

Base `5a22f0b`; tested firmware 4.0.2-draft is committed alongside this evidence.

| Check | Result |
| --- | --- |
| Host fault suite | PASS — 16 parameterized groups, including the ten previous storage/reset groups |
| Teensy 4.1 build with `--warnings all` | PASS — zero warnings |
| PCB/schematic changes | None |
| Hardware validation | Not performed |

`host-tests.log` is from `tools/test_firmware_reliability.py` with Zig 0.13.0
`c++`, C++17 and `-Wall -Wextra -Werror`. It compiles the actual sketch, storage,
metadata and both local sensor drivers. BusIO, GPS, Arduino and SD peripherals
are faked; the previous fake MS8607 driver has been removed.

The six added groups cover signed BNO values/conversions; failed and short
quaternion/vector/calibration transfers; BNO configuration failure; MS8607
events/wrappers; temperature/pressure/humidity transaction failures and humidity
CRC; and reset/configuration/PROM-transfer/PROM-CRC initialization failures.
They assert blank failed-data fields, schema width, health/LED changes, failure
counters, reset threshold, recovery and continuation of the other sensor stream.

The MS8607 PROM is a fixed synthetic fixture with CRC nibble 8 calculated using
the upstream TE algorithm. Humidity CRC uses a separate bytewise 0x31 reference.
Neither fixture constitutes physical calibration or accuracy evidence.

`build.log` records Arduino CLI and library/platform output. The build used
installed Teensy 1.62.0 and the pinned external dependencies, not an isolated
`--profile` installation. Both sensor drivers are compiled locally under `src/`.
`source-manifest.json` records raw working-file hashes and the installed MS8607
upstream provenance. Git newline conversion may change byte hashes elsewhere.

See [sensor-read checkpoint](../../../SENSOR_READ_VALIDITY.md) for remaining
GPS freshness and hardware-validation work.
