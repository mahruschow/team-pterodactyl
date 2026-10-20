#pragma once
#include "Wire.h"
struct FakeBnoBus {
  bool present = true, resetWritten = false, resetWriteFails = false;
  bool resetReadFails = false;
  uint32_t readyAfterMs = 700, resetAt = 0, transactionMs = 0;
  unsigned resetWrites = 0, reads = 0;
};
inline FakeBnoBus bnoBus;
class Adafruit_I2CDevice {
public:
  Adafruit_I2CDevice(uint8_t, TwoWire *) {}
  bool begin(bool = true) { delay(bnoBus.transactionMs); return bnoBus.present; }
  bool write(const uint8_t *data, size_t len) {
    delay(bnoBus.transactionMs);
    if (len == 2 && data[0] == 0x3f && data[1] == 0x20) {
      bnoBus.resetWrites++;
      if (bnoBus.resetWriteFails) return false;
      bnoBus.resetWritten = true;
      bnoBus.resetAt = millis();
    }
    return bnoBus.present;
  }
  bool write_then_read(const uint8_t *address, size_t, uint8_t *out, size_t len) {
    const uint8_t reg = address[0];  // upstream sometimes aliases address and out
    delay(bnoBus.transactionMs);
    bnoBus.reads++;
    if (!bnoBus.present || (bnoBus.resetWritten && bnoBus.resetReadFails)) return false;
    memset(out, 0, len);
    if (reg == 0 && (!bnoBus.resetWritten ||
                    uint32_t(millis() - bnoBus.resetAt) >= bnoBus.readyAfterMs))
      out[0] = 0xa0;
    return true;
  }
};
