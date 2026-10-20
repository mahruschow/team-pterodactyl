# Repository-local BNO055 driver

Based on the installed **Adafruit BNO055 1.6.4** library, whose `library.properties`
identifies https://github.com/adafruit/Adafruit_BNO055 as its upstream.
Copied on October 19, 2026; integration completed October 20.
`LICENSE` and the original source/utility notices are preserved.

Intentional local changes (updated October 20, firmware 4.0.2-draft):

- `begin(mode, resetTimeoutMs = 1000)` checks the software-reset write result.
- Post-reset CHIP_ID polling checks transfer success and a rollover-safe elapsed
  deadline. Failure returns `false`; it no longer waits forever.
- `read8` explicitly casts its register enum to `uint8_t`, avoiding a narrowing
  diagnostic with the host test compiler.
- Checked quaternion/vector/calibration getters expose transfer failure and leave
  caller outputs unchanged on failure; the logger uses these checked APIs.
- `begin()`, `setMode()` and `setExtCrystalUse()` propagate configuration-transfer
  failures. The latter two now return a boolean, checked by the logger's init path.

The timeout bounds the **post-reset polling phase**, not the whole `begin()` call.
A transaction already in progress may finish beyond the deadline. The selected
Teensy 1.62.0 Wire implementation has its own transaction timeouts; this patch
cannot bound a different platform's indefinitely blocking I2C implementation.
Normal upstream boot/configuration delays remain.

The sketch includes this header by relative path and Arduino compiles `src/`
recursively. Do not also include an installed `<Adafruit_BNO055.h>`. BusIO and
Unified Sensor remain external, pinned dependencies. Updating the global Arduino
library does not replace this patch; future updates must reconcile it explicitly.

Legacy value-returning getters cannot report transfer failure; use the new checked
APIs. Other legacy APIs outside the logger's path are not audited by this patch.
Run `tools/test_firmware_reliability.py` and the Teensy build
after changes. Host tests execute this driver against a fake I2C device; they do
not prove real bus timing or sensor operation.
