#pragma once
#include "Arduino.h"
#define PMTK_SET_NMEA_OUTPUT_RMCGGA ""
#define PMTK_SET_NMEA_UPDATE_1HZ ""
class Adafruit_GPS {
public:
  bool fix = false;
  unsigned year = 0, month = 0, day = 0, hour = 0, minute = 0, seconds = 0;
  unsigned milliseconds = 0, fixquality = 0, satellites = 0;
  float latitudeDegrees = 0, longitudeDegrees = 0, altitude = 0, HDOP = 0, speed = 0, angle = 0;
  explicit Adafruit_GPS(FakeSerial *) {}
  void begin(uint32_t) {}
  void sendCommand(const char *) {}
  void read() {}
  bool newNMEAreceived() { return false; }
  char *lastNMEA() { return nullptr; }
  bool parse(char *) { return false; }
};
