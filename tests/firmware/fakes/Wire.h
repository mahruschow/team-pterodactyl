#pragma once
#include "Arduino.h"
struct TwoWire {
  bool present = true;
  void begin() {}
  void setClock(uint32_t) {}
  void beginTransmission(uint8_t) {}
  int endTransmission() { return present ? 0 : 2; }
};
inline TwoWire Wire;
