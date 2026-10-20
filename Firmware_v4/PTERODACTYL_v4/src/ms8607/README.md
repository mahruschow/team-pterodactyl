# Repository-local MS8607 driver

Based on installed **Adafruit MS8607 1.0.4**, copied October 20, 2026.
Its `library.properties` declares https://github.com/adafruit/Adafruit_MS8607
as upstream. Both source files retain their original MIT license and attribution
to TE Connectivity, SparkFun and Adafruit; the installed package has no separate
LICENSE file. Original hashes are recorded in the sensor-read validation manifest.

Local changes:

- Fail initialization on either reset failure, any failed calibration PROM
  transfer, failed PROM CRC or humidity configuration-register transfer.
- Preserve/reuse the three Unified Sensor wrappers across repeated initialization.
- Track initialization so events cannot be fetched after failed initialization
  or reset until initialization succeeds. Initialize event sensor IDs.
- Check both pressure/temperature conversion commands and ADC reads.
- Check humidity conversion command and response, then propagate the existing
  humidity CRC result.
- Clear requested output events first and publish them only if every requested
  read succeeds. Unified Sensor wrappers return the driver's success/failure.
- Correct the humidity event type to relative humidity. Remove an unused BusIO
  Register include and an unused, unchecked resolution read from sampling.

Compensation formulas, CRC algorithms, conversion delays and humidity scaling
remain upstream behavior. The legacy enum-returning `getHumidityResolution()`
still cannot report a transfer error; it returns the default enum on failure.
The logger does not use that getter; its initialization uses the checked setter.
Callers must check `begin()` and `getEvent()` results.

The sketch includes this local header; Arduino recursively compiles `src/`.
Do not also include the installed `<Adafruit_MS8607.h>`. BusIO and Unified Sensor
remain external pinned dependencies. Run the host suite and Teensy build after
updating either the driver or its dependencies.
