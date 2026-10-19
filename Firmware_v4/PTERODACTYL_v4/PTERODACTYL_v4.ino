// PTERODACTYL v4 logger - DRAFT for the v4 carrier (Teensy 4.1, BNO055 #2472,
// MS8607 #4716, PA1616D GPS #5440, onboard microSD). No telemetry.
//
// Behaviour (docs/V1_REQUIREMENTS.md LOG-01..07, docs/FIRMWARE_V4.md):
// - Starts logging automatically at power-up; never waits for USB, a button or a GPS fix.
// - Each power-up (or restart after a clean stop) creates a new session folder Snnn; nothing is overwritten.
// - Independent schedules: IMU 10 Hz, environment 1 Hz, health 1 Hz, GPS on each GGA sentence.
// - Every record has session, sequence number, monotonic millis() and a status field;
//   missing or failed readings are written as empty fields, never as stale values.
// - Files stay open; data is flushed at most every second. Write failures are counted.
// - SW_MODE switched to GND closes all files cleanly (safe to remove the card).

#include <Wire.h>
#include <SD.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <Adafruit_MS8607.h>
#include <Adafruit_GPS.h>
#include "config.h"

Adafruit_BNO055 bno(55, BNO055_ADDR, &Wire);
Adafruit_MS8607 ms8607;
Adafruit_GPS gps(&GPS_SERIAL);

// ---------------------------------------------------------------- log streams
enum StreamId { S_IMU, S_ENV, S_GPS, S_HEALTH, S_EVENTS, S_COUNT };

struct LogStream {
  const char *file;
  const char *header;
  File handle;
  uint32_t seq;
  uint32_t writeFails;
};

LogStream streams[S_COUNT] = {
  {"imu.csv", "session,seq,t_ms,status,qw,qx,qy,qz,ax_mps2,ay_mps2,az_mps2,gx_rps,gy_rps,gz_rps,mx_uT,my_uT,mz_uT,cal_sys,cal_gyro,cal_accel,cal_mag", File(), 0, 0},
  {"env.csv", "session,seq,t_ms,status,pressure_pa,temperature_c,humidity_rh,pressure_alt_isa_m", File(), 0, 0},
  {"gps.csv", "session,seq,t_ms,status,fix,fix_quality,satellites,utc_date,utc_time,lat_deg,lon_deg,alt_msl_m,hdop,speed_mps,course_deg", File(), 0, 0},
  {"health.csv", "session,seq,t_ms,vbat_v,imu_ok,env_ok,gps_age_ms,imu_fail_total,env_fail_total,imu_resets,gps_parse_fails,overruns,write_fail_total,max_loop_us,mode_stop,pbf_present", File(), 0, 0},
  {"events.csv", "session,seq,t_ms,event,detail", File(), 0, 0},
};

int session = -1;          // folder number, -1 = not logging
bool sdOk = false;
bool stopRequested = false;
char line[320];

// ---------------------------------------------------------------- device state
bool imuOk = false, envOk = false;
uint8_t imuConsecutiveFails = 0;
uint32_t imuFailTotal = 0, envFailTotal = 0, imuResets = 0, gpsParseFails = 0, overruns = 0;
uint8_t calSys = 0;
uint32_t lastGgaMs = 0;
bool gpsHadFix = false;
uint32_t maxLoopUs = 0;

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
uint32_t lastSdAttemptMs = 0;          // SD retry is not a sampling schedule, so it never counts overruns

// ---------------------------------------------------------------- helpers
bool i2cPresent(uint8_t address) {
  Wire.beginTransmission(address);
  return Wire.endTransmission() == 0;
}

void writeLine(StreamId id, const char *text) {
  LogStream &s = streams[id];
  if (session < 0 || !s.handle) return;
  size_t n = strlen(text);
  if (s.handle.write(text, n) != n || s.handle.write('\n') != 1) s.writeFails++;
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

uint32_t writeFailTotal() {
  uint32_t total = 0;
  for (auto &s : streams) total += s.writeFails;
  return total;
}

// ---------------------------------------------------------------- storage
void writeMetadata(const char *dir) {
  char path[24];
  snprintf(path, sizeof(path), "%s/meta.txt", dir);
  File m = SD.open(path, FILE_WRITE);
  if (!m) { streams[S_EVENTS].writeFails++; return; }
  m.printf("firmware=%s\nbuilt=%s %s\nsession=%d\n", FW_VERSION, __DATE__, __TIME__, session);
  m.printf("board=PTERODACTYL v4 carrier (Native_KiCad_v4)\n");
  m.printf("imu_period_ms=%lu\nenv_period_ms=%lu\nhealth_period_ms=%lu\nflush_period_ms=%lu\n",
           (unsigned long)IMU_PERIOD_MS, (unsigned long)ENV_PERIOD_MS, (unsigned long)HEALTH_PERIOD_MS, (unsigned long)FLUSH_PERIOD_MS);
  m.printf("i2c_hz=%lu\ngps_baud=%lu\ngps_rate=1 Hz, RMC+GGA\n", (unsigned long)I2C_CLOCK_HZ, (unsigned long)GPS_BAUD);
  m.printf("imu_mode=BNO055 NDOF fusion, external crystal\n");
  m.printf("imu_frame=BNO055 sensor axes, default remap (record board mounting per PLACEMENT_AND_INTERFERENCE.md PC8)\n");
  m.printf("imu_units=quaternion unitless; accel m/s^2 including gravity; gyro rad/s; mag uT\n");
  m.printf("env_units=pressure Pa; temperature C at sensor location (not ambient); humidity %%RH\n");
  m.printf("pressure_alt_model=ISA 44330*(1-(p/p0)^0.190295), p0=%.0f Pa\n", ISA_P0_PA);
  m.printf("gps_alt=metres above mean sea level as reported in GGA; time=UTC from RMC/GGA when valid\n");
  m.printf("t_ms=Teensy millis() since boot, monotonic within a session\n");
  m.printf("vbat_divider=%.4f\nadc_bits=%u\n", VBAT_DIVIDER, ADC_BITS);
  m.close();
}

bool openSession() {
  char dir[8];
  for (int n = 0; n < 1000; n++) {
    snprintf(dir, sizeof(dir), "S%03d", n);
    if (SD.exists(dir)) continue;
    if (!SD.mkdir(dir)) return false;
    session = n;
    for (auto &s : streams) {
      char path[24];
      snprintf(path, sizeof(path), "%s/%s", dir, s.file);
      s.handle = SD.open(path, FILE_WRITE);
      s.seq = 0;
      if (!s.handle) { s.writeFails++; continue; }
      s.handle.println(s.header);
    }
    writeMetadata(dir);
    return true;
  }
  return false;  // 1000 sessions present: refuse to overwrite (LOG-07)
}

void closeSession() {
  for (auto &s : streams) if (s.handle) { s.handle.flush(); s.handle.close(); }
  session = -1;
}

void startLogging(const char *reason) {
  lastSdAttemptMs = millis();
  if (!sdOk) sdOk = SD.begin(BUILTIN_SDCARD);
  if (!sdOk) return;
  if (!openSession()) { sdOk = false; return; }
  event("SESSION_START", reason);
  char detail[64];
  snprintf(detail, sizeof(detail), "imu=%d env=%d", imuOk, envOk);
  event("DEVICES", detail);
}

void flushAll() {
  for (auto &s : streams) if (s.handle) s.handle.flush();
}

// ---------------------------------------------------------------- devices
bool initImu() {
  if (!bno.begin(OPERATION_MODE_NDOF)) return false;
  bno.setExtCrystalUse(true);
  return true;
}

void resetImu(uint32_t now) {
  // RST is pulled up on the breakout; drive low briefly, then release.
  pinMode(PIN_IMU_RST, OUTPUT);
  digitalWrite(PIN_IMU_RST, LOW);
  delay(1);
  pinMode(PIN_IMU_RST, INPUT);
  delay(700);  // BNO055 power-on reset time; blocks other streams once per reset (logged)
  imuResets++;
  imuOk = initImu();
  imuConsecutiveFails = 0;
  char detail[40];
  snprintf(detail, sizeof(detail), "ok=%d blocked_ms=%lu", imuOk, (unsigned long)(millis() - now));
  event("IMU_RESET", detail);
}

void sampleImu(uint32_t now) {
  if (!i2cPresent(BNO055_ADDR)) {
    imuOk = false; imuFailTotal++;
    record(S_IMU, now, "NO_RESPONSE,,,,,,,,,,,,,,,,,");
    if (++imuConsecutiveFails >= IMU_FAILS_BEFORE_RESET) resetImu(now);
    return;
  }
  if (!imuOk) {                          // device answered again: re-initialise before trusting data
    imuOk = initImu();
    if (!imuOk) { imuFailTotal++; record(S_IMU, now, "INIT_FAIL,,,,,,,,,,,,,,,,,"); return; }
    event("IMU_REINIT", "ok");
  }
  imuConsecutiveFails = 0;
  imu::Quaternion q = bno.getQuat();
  imu::Vector<3> a = bno.getVector(Adafruit_BNO055::VECTOR_ACCELEROMETER);
  imu::Vector<3> g = bno.getVector(Adafruit_BNO055::VECTOR_GYROSCOPE);   // deg/s from library
  imu::Vector<3> m = bno.getVector(Adafruit_BNO055::VECTOR_MAGNETOMETER);
  uint8_t cs, cg, ca, cm;
  bno.getCalibration(&cs, &cg, &ca, &cm);
  calSys = cs;
  const float d2r = PI / 180.0f;
  record(S_IMU, now, "OK,%.5f,%.5f,%.5f,%.5f,%.3f,%.3f,%.3f,%.5f,%.5f,%.5f,%.2f,%.2f,%.2f,%u,%u,%u,%u",
         q.w(), q.x(), q.y(), q.z(), a.x(), a.y(), a.z(), g.x() * d2r, g.y() * d2r, g.z() * d2r,
         m.x(), m.y(), m.z(), cs, cg, ca, cm);
}

void sampleEnv(uint32_t now) {
  if (!i2cPresent(MS8607_PT_ADDR) || !i2cPresent(MS8607_RH_ADDR)) {
    envOk = false; envFailTotal++;
    record(S_ENV, now, "NO_RESPONSE,,,,");
    return;
  }
  if (!envOk) {
    envOk = ms8607.begin(&Wire);
    if (!envOk) { envFailTotal++; record(S_ENV, now, "INIT_FAIL,,,,"); return; }
    event("ENV_REINIT", "ok");
  }
  sensors_event_t pressure, temperature, humidity;
  if (!ms8607.getEvent(&pressure, &temperature, &humidity)) {
    envFailTotal++;
    record(S_ENV, now, "READ_FAIL,,,,");
    return;
  }
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
  record(S_HEALTH, now, "%.3f,%d,%d,%ld,%lu,%lu,%lu,%lu,%lu,%lu,%lu,%d,%d", vbat, imuOk, envOk, gpsAge,
         (unsigned long)imuFailTotal, (unsigned long)envFailTotal, (unsigned long)imuResets, (unsigned long)gpsParseFails,
         (unsigned long)overruns, (unsigned long)writeFailTotal(), (unsigned long)maxLoopUs,
         modeSwitch.state == LOW, pbf.state == LOW);
  if (Serial) Serial.printf("t=%lu session=%d vbat=%.2f imu=%d env=%d gps_age=%ld fix=%d sats=%u cal=%u overruns=%lu wfail=%lu\n",
                            (unsigned long)now, session, vbat, imuOk, envOk, gpsAge, gps.fix, gps.satellites, calSys,
                            (unsigned long)overruns, (unsigned long)writeFailTotal());
  maxLoopUs = 0;
}

void updateLeds(uint32_t now) {
  bool gpsFresh = gps.fix && lastGgaMs && now - lastGgaMs < GPS_STALE_MS;
  bool logging = session >= 0;
  bool fault = (!logging && !stopRequested) || !imuOk || !envOk || writeFailTotal() > 0;
  digitalWrite(PIN_LED_FAULT, fault);
  digitalWrite(PIN_LED_GPS, gpsFresh);
  digitalWrite(PIN_LED_LOG, logging && (now / 500) % 2);
  digitalWrite(PIN_LED_CAL, imuOk && calSys == 3);
}

void serviceInputs(uint32_t now) {
  if (modeSwitch.update(now)) {
    if (modeSwitch.state == LOW) {
      stopRequested = true;
      event("CLEAN_STOP", "mode switch");
      closeSession();
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
  envOk = ms8607.begin(&Wire);

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
  serviceGps(now);
  if (imuTick.due(now)) sampleImu(now);
  if (envTick.due(now)) sampleEnv(now);
  if (healthTick.due(now)) writeHealth(now);
  if (flushTick.due(now)) flushAll();
  if (session < 0 && !stopRequested && now - lastSdAttemptMs >= SD_RETRY_MS) startLogging("sd retry");
  updateLeds(now);
  uint32_t elapsed = micros() - start;
  if (elapsed > maxLoopUs) maxLoopUs = elapsed;
}
