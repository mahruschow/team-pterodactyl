#pragma once
#include "Adafruit_Sensor.h"
#include "Wire.h"
class Adafruit_MS8607 {
public:
  bool begin(TwoWire *) { return true; }
  bool getEvent(sensors_event_t *p, sensors_event_t *t, sensors_event_t *h) {
    p->pressure = 1000; t->temperature = 20; h->relative_humidity = 40;
    return true;
  }
};
