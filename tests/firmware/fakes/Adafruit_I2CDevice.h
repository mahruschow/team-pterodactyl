#pragma once
#include "Wire.h"
#include <array>
#include <vector>
#include <map>
struct FakeBnoBus {
  bool present = true, resetWritten = false, resetWriteFails = false;
  bool resetReadFails = false;
  uint32_t readyAfterMs = 700, resetAt = 0, transactionMs = 0;
  unsigned resetWrites = 0, reads = 0;
  int failReadReg = -1, failWriteReg = -1;
  std::map<uint8_t, std::vector<uint8_t>> registers;
};
inline FakeBnoBus bnoBus;
struct FakeMsBus {
  bool badPromCrc = false, badHumidityCrc = false;
  std::string failOperation;
  int failAddress = -1, failCommand = -1, failCall = 1, matches = 0;
  uint8_t conversion = 0;
  unsigned resets = 0;
  // Deterministic synthetic calibration/ADC values, not a physical sensor.
  std::array<uint16_t, 8> prom = {0, 46372, 43981, 29059, 27842, 31553, 28165, 0};
  bool fail(const char *operation, int address, int command) {
    return failOperation == operation &&
           (failAddress < 0 || failAddress == address) &&
           (failCommand < 0 || failCommand == command) && ++matches == failCall;
  }
  // Independent byte-at-a-time CRC reference, polynomial 0x31, initial zero.
  uint8_t humidityCrc(uint16_t value) const {
    uint8_t crc = 0;
    for (uint8_t data : {uint8_t(value >> 8), uint8_t(value)}) {
      crc ^= data;
      for (int bit = 0; bit < 8; ++bit)
        crc = (crc & 0x80) ? uint8_t((crc << 1) ^ 0x31) : uint8_t(crc << 1);
    }
    return crc;
  }
};
inline FakeMsBus msBus;
class Adafruit_I2CDevice {
  uint8_t deviceAddress;
public:
  Adafruit_I2CDevice(uint8_t address, TwoWire *) : deviceAddress(address) {}
  bool begin(bool = true) {
    if (deviceAddress != 0x28) return !msBus.fail("begin", deviceAddress, -1);
    delay(bnoBus.transactionMs); return bnoBus.present;
  }
  bool write(const uint8_t *data, size_t len) {
    if (deviceAddress != 0x28) {
      if (msBus.fail("write", deviceAddress, data[0])) return false;
      if (deviceAddress == 0x76 && (data[0] & 0xe0) == 0x40) msBus.conversion = data[0];
      if (data[0] == 0x1e || data[0] == 0xfe) msBus.resets++;
      return true;
    }
    delay(bnoBus.transactionMs);
    if (bnoBus.failWriteReg == data[0]) return false;
    if (len == 2 && data[0] == 0x3f && data[1] == 0x20) {
      bnoBus.resetWrites++;
      if (bnoBus.resetWriteFails) return false;
      bnoBus.resetWritten = true;
      bnoBus.resetAt = millis();
    }
    return bnoBus.present;
  }
  bool read(uint8_t *out, size_t len) {
    if (msBus.fail("read", deviceAddress, -1)) {
      if (len) out[0] = 0xff; // partial transfer must not leak to a published event
      return false;
    }
    if (deviceAddress == 0x40 && len == 3) {
      out[0] = 0x80; out[1] = 0x00;
      out[2] = msBus.humidityCrc(0x8000) ^ (msBus.badHumidityCrc ? 1 : 0);
      return true;
    }
    return false;
  }
  bool write_then_read(const uint8_t *address, size_t, uint8_t *out, size_t len, bool = false) {
    const uint8_t reg = address[0];  // upstream sometimes aliases address and out
    if (deviceAddress != 0x28) {
      if (msBus.fail("write_then_read", deviceAddress, reg)) {
        if (len) out[0] = 0xff;
        return false;
      }
      if (deviceAddress == 0x76 && reg >= 0xa0 && reg <= 0xac && len == 2) {
        uint16_t value = msBus.prom[(reg - 0xa0) / 2];
        // Fixed fixture CRC, precomputed using TE's algorithm from upstream.
        if (reg == 0xa0) value |= uint16_t(8 ^ (msBus.badPromCrc ? 1 : 0)) << 12;
        out[0] = value >> 8; out[1] = value;
        return true;
      }
      if (deviceAddress == 0x76 && reg == 0 && len == 3) {
        uint32_t value = (msBus.conversion & 0x10) ? 8077636 : 6465444;
        out[0] = value >> 16; out[1] = value >> 8; out[2] = value;
        return true;
      }
      if (deviceAddress == 0x40 && reg == 0xe7 && len == 1) { out[0] = 2; return true; }
      return false;
    }
    delay(bnoBus.transactionMs);
    bnoBus.reads++;
    if (bnoBus.failReadReg == reg) {
      if (len) out[0] = 0xff;
      return false;
    }
    if (!bnoBus.present || (bnoBus.resetWritten && bnoBus.resetReadFails)) return false;
    memset(out, 0, len);
    auto data = bnoBus.registers.find(reg);
    if (data != bnoBus.registers.end()) {
      if (data->second.size() != len) return false; // short read
      memcpy(out, data->second.data(), len);
    }
    if (reg == 0 && (!bnoBus.resetWritten ||
                    uint32_t(millis() - bnoBus.resetAt) >= bnoBus.readyAfterMs))
      out[0] = 0xa0;
    return true;
  }
};
