#pragma once
#include "Arduino.h"
constexpr float SENSORS_DPS_TO_RADS = PI / 180;
enum { SENSOR_TYPE_ORIENTATION, SENSOR_TYPE_LINEAR_ACCELERATION,
       SENSOR_TYPE_ACCELEROMETER, SENSOR_TYPE_GRAVITY,
       SENSOR_TYPE_GYROSCOPE, SENSOR_TYPE_MAGNETIC_FIELD,
       SENSOR_TYPE_AMBIENT_TEMPERATURE, SENSOR_TYPE_PRESSURE,
       SENSOR_TYPE_RELATIVE_HUMIDITY };
struct FakeVector { float x, y, z; };
struct sensors_event_t {
  int version, sensor_id, type;
  uint32_t timestamp;
  FakeVector orientation, acceleration, gyro, magnetic;
  float pressure, temperature, relative_humidity;
};
struct sensor_t {
  char name[12];
  int version, sensor_id, type, min_delay;
  float max_value, min_value, resolution;
};
class Adafruit_Sensor {
public:
  virtual ~Adafruit_Sensor() = default;
  virtual bool getEvent(sensors_event_t *) = 0;
  virtual void getSensor(sensor_t *) = 0;
};
