// PTERODACTYL v4 logger - DRAFT for the v4 carrier (Teensy 4.1, BNO055 #2472,
// MS8607 #4716, PA1616D GPS #5440, onboard microSD). No telemetry.
//
// Behaviour (docs/V1_REQUIREMENTS.md LOG-01..07, docs/FIRMWARE_V4.md):
// - Starts logging automatically at power-up; never waits for USB, a button or a GPS fix.
// - Each power-up (or restart after a clean stop) creates a new session folder Snnn; nothing is overwritten.
// - Independent schedules: IMU 10 Hz, environment 1 Hz, health 1 Hz, GPS on each GGA sentence.
// - Every record has session, sequence number, monotonic millis() and a status field;
//   failed sensor transfers/CRC produce empty fields; GPS freshness remains open.
// - Files stay open; sync is scheduled each second. SD faults close the session and retry in a new folder.
// - SW_MODE to GND requests close; failures latch the fault LED. Hardware timing still needs testing.

#include <Wire.h>
#include <SD.h>
#include <Adafruit_Sensor.h>
#include "src/bno055/Adafruit_BNO055.h"
#include "src/ms8607/Adafruit_MS8607.h"
#include <Adafruit_GPS.h>
#include "config.h"
#include "storage.h"

Adafruit_BNO055 bno(55, BNO055_ADDR, &Wire);
Adafruit_MS8607 ms8607;
Adafruit_GPS gps(&GPS_SERIAL);

bool stopRequested = false;
char line[320];

// ---------------------------------------------------------------- device state
bool imuOk = false, envOk = false;
bool imuReady = false, envReady = false; // initialized separately from latest read status
uint8_t imuConsecutiveFails = 0;
uint32_t imuFailTotal = 0, envFailTotal = 0, imuResets = 0, gpsParseFails = 0, overruns = 0;
uint8_t calSys = 0;
uint32_t lastGgaMs = 0;
bool gpsHadFix = false;
uint32_t maxLoopUs = 0;
uint32_t lastImuAttemptMs = 0;
bool imuAttempted = false;

struct Debounced {
  uint8_t pin; bool state; bool raw; uint32_t changedMs;
  bool update(uint32_t now) {            // returns true when the stable state changes
    bool r = digitalRead(pin);
    if (r != raw) { raw = r; changedMs = now; }
    if (raw != state && now - changedMs >= DEBOUNCE_MS) { state = raw; return true; }
    return false;
  }
};
Debounced modeSwitch{PIN_SW_MODE, HIGH, HIGH, 0};
Debounced button{PIN_BUTTON, HIGH, HIGH, 0};
Debounced pbf{PIN_PBF, LOW, LOW, 0};

struct Schedule {
  uint32_t period, next;
  bool due(uint32_t now) {               // counts missed periods as overruns
    if ((int32_t)(now - next) < 0) return false;
    uint32_t late = now - next;
    if (late >= period) { overruns += late / period; next = now + period; }
    else next += period;
    return true;
  }
};
Schedule imuTick{IMU_PERIOD_MS, 0}, envTick{ENV_PERIOD_MS, 0}, healthTick{HEALTH_PERIOD_MS, 0},
         flushTick{FLUSH_PERIOD_MS, 0};

// ---------------------------------------------------------------- helpers
bool i2cPresent(uint8_t address) {
  Wire.beginTransmission(address);
  return Wire.endTransmission() == 0;
}

// Prefix "session,seq,t_ms," then the formatted body.
void record(StreamId id, uint32_t now, const char *fmt, ...) {
  LogStream &s = streams[id];
  int n = snprintf(line, sizeof(line), "%d,%lu,%lu,", session, (unsigned long)s.seq++, (unsigned long)now);
  va_list args;
  va_start(args, fmt);
  vsnprintf(line + n, sizeof(line) - n, fmt, args);
  va_end(args);
  writeLine(id, line);
}

void event(const char *name, const char *detail = "") {
  record(S_EVENTS, millis(), "%s,%s", name, detail);
  if (Serial) Serial.printf("[%lu] %s %s\n", (unsigned long)millis(), name, detail);
}

void startLogging(const char *reason) {
  if (!startStorage(writeMetadata)) return;
  event("SESSION_START", reason);
  char detail[64];
  snprintf(detail, sizeof(detail), "imu=%d env=%d storage_faults=%lu", imuOk, envOk, (unsigned long)storageFaults);
  event("DEVICES", detail);
}

// ---------------------------------------------------------------- devices
bool initImu() {
  calSys = 0;
  bool ok = bno.begin(OPERATION_MODE_NDOF, BNO_RESET_TIMEOUT_MS);
  if (ok) ok = bno.setExtCrystalUse(true);
  imuReady = ok;
  lastImuAttemptMs = millis();  // cooldown starts after the blocking attempt
  imuAttempted = true;
  return ok;
}

void resetImu(uint32_t now) {
  // RST is pulled up on the breakout; drive low briefly, then release.
  pinMode(PIN_IMU_RST, OUTPUT);
  digitalWrite(PIN_IMU_RST, LOW);
  delay(1);
  pinMode(PIN_IMU_RST, INPUT);
  delay(700);  // BNO055 power-on reset time; blocks other streams once per reset (logged)
  imuResets++;
  initImu();
  imuOk = false;  // reset success is not yet a successful measurement
  imuConsecutiveFails = 0;
  char detail[40];
  snprintf(detail, sizeof(detail), "ready=%d blocked_ms=%lu", imuReady, (unsigned long)(millis() - now));
  event("IMU_RESET", detail);
}

void sampleImu(uint32_t now) {
  if (!imuReady && imuAttempted && now - lastImuAttemptMs < IMU_RETRY_MS) {
    record(S_IMU, now, "INIT_WAIT,,,,,,,,,,,,,,,,,");
    return;
  }
  if (!i2cPresent(BNO055_ADDR)) {
    imuReady = imuOk = false; calSys = 0; imuFailTotal++;
    record(S_IMU, now, "NO_RESPONSE,,,,,,,,,,,,,,,,,");
    if (++imuConsecutiveFails >= IMU_FAILS_BEFORE_RESET) resetImu(now);
    return;
  }
  if (!imuReady) {                       // device answered again: re-initialise before trusting data
    imuOk = initImu();
    if (!imuOk) { imuFailTotal++; record(S_IMU, now, "INIT_FAIL,,,,,,,,,,,,,,,,,"); return; }
    event("IMU_REINIT", "ok");
  }
  imu::Quaternion q;
  imu::Vector<3> a, g, m;
  uint8_t cs, cg, ca, cm;
  if (!bno.getQuatChecked(q) ||
      !bno.getVectorChecked(Adafruit_BNO055::VECTOR_ACCELEROMETER, a) ||
      !bno.getVectorChecked(Adafruit_BNO055::VECTOR_GYROSCOPE, g) ||
      !bno.getVectorChecked(Adafruit_BNO055::VECTOR_MAGNETOMETER, m) ||
      !bno.getCalibrationChecked(&cs, &cg, &ca, &cm)) {
    imuOk = false; calSys = 0; imuFailTotal++;
    record(S_IMU, now, "READ_FAIL,,,,,,,,,,,,,,,,,");
    if (++imuConsecutiveFails >= IMU_FAILS_BEFORE_RESET) resetImu(now);
    return;
  }
  imuOk = true;
  imuConsecutiveFails = 0;
  calSys = cs;
  const float d2r = PI / 180.0f;
  record(S_IMU, now, "OK,%.5f,%.5f,%.5f,%.5f,%.3f,%.3f,%.3f,%.5f,%.5f,%.5f,%.2f,%.2f,%.2f,%u,%u,%u,%u",
         q.w(), q.x(), q.y(), q.z(), a.x(), a.y(), a.z(), g.x() * d2r, g.y() * d2r, g.z() * d2r,
         m.x(), m.y(), m.z(), cs, cg, ca, cm);
}

void sampleEnv(uint32_t now) {
  if (!i2cPresent(MS8607_PT_ADDR) || !i2cPresent(MS8607_RH_ADDR)) {
    envReady = envOk = false; envFailTotal++;
    record(S_ENV, now, "NO_RESPONSE,,,,");
    return;
  }
  if (!envReady) {
    envReady = envOk = ms8607.begin(&Wire);
    if (!envOk) { envFailTotal++; record(S_ENV, now, "INIT_FAIL,,,,"); return; }
    event("ENV_REINIT", "ok");
  }
  sensors_event_t pressure, temperature, humidity;
  if (!ms8607.getEvent(&pressure, &temperature, &humidity)) {
    envOk = false; envFailTotal++;
    record(S_ENV, now, "READ_FAIL,,,,");
    return;
  }
  envOk = true;
  float pa = pressure.pressure * 100.0f;  // library reports hPa
  float alt = 44330.0f * (1.0f - powf(pa / ISA_P0_PA, 0.190295f));
  record(S_ENV, now, "OK,%.1f,%.2f,%.2f,%.1f", pa, temperature.temperature, humidity.relative_humidity, alt);
}

void serviceGps(uint32_t now) {
  while (GPS_SERIAL.available()) {
    gps.read();
    if (!gps.newNMEAreceived()) continue;
    char *nmea = gps.lastNMEA();
    if (!gps.parse(nmea)) { gpsParseFails++; continue; }
    // One row per GGA (1 Hz); RMC fields (date, speed, course) are merged from the latest RMC.
    const char *type = strchr(nmea, '$');
    if (!type || strncmp(type + 3, "GGA", 3) != 0) continue;
    lastGgaMs = now;
    if (gps.fix != gpsHadFix) { gpsHadFix = gps.fix; event(gps.fix ? "GPS_FIX" : "GPS_FIX_LOST"); }
    char date[16] = "", time[24] = "";
    if (gps.year) snprintf(date, sizeof(date), "20%02u-%02u-%02u", gps.year, gps.month, gps.day);
    snprintf(time, sizeof(time), "%02u:%02u:%02u.%03u", gps.hour, gps.minute, gps.seconds, gps.milliseconds);
    if (gps.fix) {
      record(S_GPS, now, "OK,1,%u,%u,%s,%s,%.7f,%.7f,%.1f,%.2f,%.2f,%.1f", gps.fixquality, gps.satellites, date, time,
             gps.latitudeDegrees, gps.longitudeDegrees, gps.altitude, gps.HDOP, gps.speed * 0.514444f, gps.angle);
    } else {
      record(S_GPS, now, "NO_FIX,0,%u,%u,%s,%s,,,,,,", gps.fixquality, gps.satellites, date, time);
    }
  }
}

void writeHealth(uint32_t now) {
  float vbat = analogRead(PIN_VBAT) * ADC_REF_V / ((1 << ADC_BITS) - 1) * VBAT_DIVIDER;
  long gpsAge = lastGgaMs ? (long)(now - lastGgaMs) : -1;
  record(S_HEALTH, now, "%.3f,%d,%d,%ld,%lu,%lu,%lu,%lu,%lu,%lu,%lu,%d,%d,%lu", vbat, imuOk, envOk, gpsAge,
         (unsigned long)imuFailTotal, (unsigned long)envFailTotal, (unsigned long)imuResets, (unsigned long)gpsParseFails,
         (unsigned long)overruns, (unsigned long)writeFailTotal(), (unsigned long)maxLoopUs,
         modeSwitch.state == LOW, pbf.state == LOW, (unsigned long)storageFaults);
  if (Serial) Serial.printf("t=%lu session=%d vbat=%.2f imu=%d env=%d gps_age=%ld fix=%d sats=%u cal=%u overruns=%lu wfail=%lu storage_faults=%lu\n",
                            (unsigned long)now, session, vbat, imuOk, envOk, gpsAge, gps.fix, gps.satellites, calSys,
                            (unsigned long)overruns, (unsigned long)writeFailTotal(), (unsigned long)storageFaults);
  maxLoopUs = 0;
}

void updateLeds(uint32_t now) {
  bool gpsFresh = gps.fix && lastGgaMs && now - lastGgaMs < GPS_STALE_MS;
  bool logging = session >= 0;
  bool fault = (!logging && !stopRequested) || !imuOk || !envOk || storageFaults > 0;
  digitalWrite(PIN_LED_FAULT, fault);
  digitalWrite(PIN_LED_GPS, gpsFresh);
  digitalWrite(PIN_LED_LOG, logging && (now / 500) % 2);
  digitalWrite(PIN_LED_CAL, imuOk && calSys == 3);
}

void serviceInputs(uint32_t now) {
  if (modeSwitch.update(now)) {
    if (modeSwitch.state == LOW) {
      stopRequested = true;
      event("STOP_REQUEST", "mode switch");
      const uint32_t faultsBeforeStop = storageFaults;
      const bool wasLogging = session >= 0;
      const bool closed = closeSession();
      // This result cannot be appended to files that are already closed.
      if (Serial) Serial.println(wasLogging && closed && storageFaults == faultsBeforeStop
                                 ? "SD_STOP_OK" : "SD_STOP_FAILED_OR_INACTIVE");
    } else {
      stopRequested = false;
      startLogging("mode switch released");
    }
  }
  if (button.update(now) && button.state == LOW) event("BUTTON", "marker");
  if (pbf.update(now)) event(pbf.state == HIGH ? "PBF_REMOVED" : "PBF_INSERTED");
}

// ---------------------------------------------------------------- Arduino entry points
void setup() {
  Serial.begin(115200);  // never waited on (LOG-01)
  for (uint8_t pin : {PIN_LED_FAULT, PIN_LED_GPS, PIN_LED_LOG, PIN_LED_CAL}) { pinMode(pin, OUTPUT); digitalWrite(pin, HIGH); }
  for (uint8_t pin : {PIN_SW_MODE, PIN_BUTTON, PIN_PBF}) pinMode(pin, INPUT_PULLUP);
  pinMode(PIN_IMU_RST, INPUT);
  analogReadResolution(ADC_BITS);
  analogReadAveraging(16);

  Wire.begin();
  Wire.setClock(I2C_CLOCK_HZ);
  imuOk = initImu();
  envReady = envOk = ms8607.begin(&Wire);

  gps.begin(GPS_BAUD);
  gps.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  gps.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);

  uint32_t now = millis();
  modeSwitch.raw = modeSwitch.state = digitalRead(PIN_SW_MODE);
  button.raw = button.state = digitalRead(PIN_BUTTON);
  pbf.raw = pbf.state = digitalRead(PIN_PBF);
  stopRequested = modeSwitch.state == LOW;   // switch already in stop position: do not start
  if (!stopRequested) startLogging("power-up");
  event("BOOT", FW_VERSION);
  if (stopRequested) event("STOP_AT_BOOT", "mode switch in stop position");
  for (Schedule *s : {&imuTick, &envTick, &healthTick, &flushTick}) s->next = now + s->period;
  for (uint8_t pin : {PIN_LED_FAULT, PIN_LED_GPS, PIN_LED_LOG, PIN_LED_CAL}) digitalWrite(pin, LOW);
}

void loop() {
  uint32_t start = micros();
  uint32_t now = millis();
  serviceInputs(now);
  now = millis();
  serviceGps(now);
  if (imuTick.due(now)) sampleImu(now);
  now = millis();
  if (envTick.due(now)) sampleEnv(now);
  now = millis();
  if (healthTick.due(now)) writeHealth(now);
  if (flushTick.due(now)) flushAll();
  now = millis();  // flush/reset may have updated retry timestamps after loop entry
  if (session < 0 && !stopRequested && now - lastSdAttemptMs >= SD_RETRY_MS) startLogging("sd retry");
  updateLeds(millis());
  uint32_t elapsed = micros() - start;
  if (elapsed > maxLoopUs) maxLoopUs = elapsed;
}
