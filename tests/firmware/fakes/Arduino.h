// Host-only fake hardware. Never included in an Arduino build.
#pragma once
#include <cstdint>
#include <cstdio>
#include <cstdarg>
#include <cstring>
#include <cmath>
#include <string>
#include <initializer_list>
using byte = uint8_t;
using boolean = bool;
constexpr int LOW = 0, HIGH = 1, INPUT = 0, OUTPUT = 1, INPUT_PULLUP = 2;
constexpr float PI = 3.14159265358979323846f;
inline uint32_t clockMs = 0;
inline uint32_t millis() { return clockMs; }
inline uint32_t micros() { return clockMs * 1000; }
inline void delay(uint32_t ms) { clockMs += ms; }
inline int pins[64] = {};
inline void pinMode(int, int) {}
inline void digitalWrite(int p, int v) { pins[p] = v; }
inline int digitalRead(int p) { return pins[p]; }
inline void analogReadResolution(int) {}
inline void analogReadAveraging(int) {}
inline int analogRead(int) { return 1000; }
class FakeSerial {
public:
  std::string output;
  operator bool() const { return true; }
  void begin(unsigned long) {}
  int available() { return 0; }
  void println(const char *s) { output += std::string(s) + "\n"; }
  void printf(const char *fmt, ...) {
    char text[1024];
    va_list args;
    va_start(args, fmt);
    vsnprintf(text, sizeof(text), fmt, args);
    va_end(args);
    output += text;
  }
};
inline FakeSerial Serial, Serial2;
