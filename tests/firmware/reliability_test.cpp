// Compile the actual sketch, storage, metadata, and patched BNO driver against
// fake hardware. This does not emulate a real SD card or Teensy I2C controller.
#include <iostream>
#include <stdexcept>
#include <algorithm>
#include "../../Firmware_v4/PTERODACTYL_v4/PTERODACTYL_v4.ino"

#define CHECK(x) do { if (!(x)) throw std::runtime_error( \
  std::string(__func__) + ":" + std::to_string(__LINE__) + " " #x); } while (0)

static void reset() {
  disk.failOperation.clear();
  closeSession();
  disk = FakeDisk();
  bnoBus = FakeBnoBus();
  msBus = FakeMsBus();
  Wire.present = true;
  clockMs = 100;
  storageFaults = 0;
  lastSdAttemptMs = 0;
  for (auto &s : streams) { s.seq = 0; s.writeFails = 0; }
  stopRequested = false;
  imuReady = imuOk = true;
  envReady = envOk = ms8607.begin(&Wire);
  CHECK(envReady);
  imuAttempted = false;
  imuConsecutiveFails = 0;
  imuFailTotal = envFailTotal = imuResets = overruns = 0;
  lastImuAttemptMs = 0;
  Serial.output.clear();
  std::fill(std::begin(pins), std::end(pins), HIGH);
  modeSwitch = {PIN_SW_MODE, HIGH, HIGH, 0};
  button = {PIN_BUTTON, HIGH, HIGH, 0};
  pbf = {PIN_PBF, HIGH, HIGH, 0};
  // Most tests isolate storage from the sampling schedules.
  for (Schedule *s : {&imuTick, &envTick, &healthTick, &flushTick})
    s->next = millis() + 100000;
}

static void failAt(const char *operation, const std::string &path, int call = 1) {
  disk.failOperation = operation;
  disk.failPath = path;
  disk.failOnCall = call;
  disk.matchedCalls = 0;
}
static std::map<std::string, std::string> snapshot() {
  std::map<std::string, std::string> result;
  for (auto &f : disk.files) result[f.first] = f.second->bytes;
  return result;
}
static void unchanged(const std::map<std::string, std::string> &before) {
  for (const auto &f : before) CHECK(disk.files.at(f.first)->bytes == f.second);
}
static void assertInactive() {
  CHECK(session == -1);
  CHECK(disk.allClosed());
  for (auto &s : streams) CHECK(!s.handle);
  updateLeds(500);
  CHECK(pins[PIN_LED_LOG] == LOW);
  CHECK(pins[PIN_LED_FAULT] == HIGH);
}

static void successfulSessions() {
  reset();
  CHECK(startStorage(writeMetadata));
  CHECK(session == 0 && disk.files.size() == 6);
  for (auto &s : streams) {
    CHECK(s.handle && s.seq == 0);
    CHECK(disk.files.at(std::string("S000/") + s.file)->bytes == std::string(s.header) + "\n");
  }
  CHECK(disk.files.at("S000/meta.txt")->bytes.find("session=0\n") != std::string::npos);
  writeLine(S_IMU, "first");
  CHECK(flushAll());
  CHECK(closeSession());
  const auto before = snapshot();
  CHECK(startStorage(writeMetadata) && session == 1);
  unchanged(before);
  CHECK(storageFaults == 0 && writeFailTotal() == 0);
}

static void incompleteSessions() {
  // Every CSV: open, short header, missing newline, sync. Metadata: open,
  // short first write, late write, sync, close. Partial files must survive retry.
  for (const auto &s : streams) {
    const std::string path = std::string("S000/") + s.file;
    for (const char *op : {"open", "write", "sync"}) {
      reset();
      failAt(op, path);
      CHECK(!startStorage(writeMetadata));
      assertInactive();
      CHECK(storageFaults > 0 && writeFailTotal() > 0);
      const auto before = snapshot();
      disk.failOperation.clear();
      CHECK(startStorage(writeMetadata) && session == 1);
      unchanged(before);
    }
    reset();
    failAt("write", path, 2);  // header was complete; newline fails
    CHECK(!startStorage(writeMetadata));
    assertInactive();
  }
  for (const char *op : {"open", "write", "sync", "close"}) {
    reset();
    failAt(op, "S000/meta.txt");
    CHECK(!startStorage(writeMetadata));
    assertInactive();
    CHECK(startStorage(writeMetadata) && session == 1);
  }
  reset();
  failAt("write", "S000/meta.txt", 5);
  CHECK(!startStorage(writeMetadata));
  assertInactive();
}

static void mountDirectoryAndExhaustion() {
  reset();
  disk.missing = true;
  startLogging("missing");
  assertInactive();
  const uint32_t retryAt = lastSdAttemptMs;
  disk.missing = false;
  clockMs = retryAt + SD_RETRY_MS - 1;
  loop();
  CHECK(session == -1 && disk.mounts == 1);
  clockMs++;
  loop();
  CHECK(session == 0 && disk.mounts == 2);
  reset();
  failAt("mkdir", "S000");
  CHECK(!startStorage(writeMetadata));
  assertInactive();
  CHECK(startStorage(writeMetadata) && session == 0);
  reset();
  for (int n = 0; n < 1000; n++) {
    char name[8]; snprintf(name, sizeof(name), "S%03d", n);
    disk.dirs.insert(name);
  }
  CHECK(!startStorage(writeMetadata));
  assertInactive();
  CHECK(disk.files.empty() && disk.dirs.size() == 1000);
}

static void exclusiveFiles() {
  reset();
  CHECK(startStorage(writeMetadata));
  CHECK(closeSession());
  const auto before = snapshot();
  disk.lieAboutExists = true;
  CHECK(!startStorage(writeMetadata));  // O_EXCL protects previous CSV content
  unchanged(before);
  assertInactive();
}

static void writeAndSyncRecovery() {
  for (const auto &stream : streams) {
    const std::string path = std::string("S000/") + stream.file;
    for (const char *op : {"write", "sync"}) {
      reset();
      CHECK(startStorage(writeMetadata));
      failAt(op, path);
      if (std::string(op) == "write")
        writeLine(static_cast<StreamId>(&stream - streams), "partial record");
      else CHECK(!flushAll());
      assertInactive();
      const auto before = snapshot();
      CHECK(startStorage(writeMetadata) && session == 1);
      unchanged(before);
      updateLeds(500);
      CHECK(pins[PIN_LED_LOG] == HIGH && pins[PIN_LED_FAULT] == HIGH);
      CHECK(writeFailTotal() > 0);  // fault history survives successful recovery
    }
  }
  reset();
  CHECK(startStorage(writeMetadata));
  failAt("write", "S000/imu.csv", 2);
  writeLine(S_IMU, "newline failure");
  assertInactive();
  reset();
  CHECK(startStorage(writeMetadata));
  streams[S_ENV].handle.close();  // unexpected invalid required handle
  writeLine(S_ENV, "must not silently skip");
  assertInactive();
}

static void cleanStopAndFailedClose() {
  for (bool failClose : {false, true}) {
    reset();
    startLogging("test");
    if (failClose) failAt("close", "S000/env.csv");
    pins[PIN_SW_MODE] = LOW;
    serviceInputs(millis());
    delay(DEBOUNCE_MS);
    serviceInputs(millis());
    CHECK(stopRequested && session == -1 && disk.allClosed());
    CHECK(Serial.output.find(failClose ? "SD_STOP_FAILED" : "SD_STOP_OK") != std::string::npos);
    delay(SD_RETRY_MS * 2);
    loop();
    CHECK(session == -1 && disk.mounts == 1);  // never restart while stopped
    pins[PIN_SW_MODE] = HIGH;
    serviceInputs(millis());
    delay(DEBOUNCE_MS);
    serviceInputs(millis());
    CHECK(!stopRequested && session == 1);
  }
  reset();
  CHECK(startStorage(writeMetadata));
  streams[S_ENV].handle.close();
  CHECK(!closeSession());
  assertInactive();
  reset();
  CHECK(startStorage(writeMetadata));
  disk.files.at("S000/env.csv")->writeError = true;
  CHECK(!closeSession());
  assertInactive();
}

static void retryTimingAndRollover() {
  reset();
  clockMs = UINT32_MAX - 2500;
  CHECK(startStorage(writeMetadata));
  disk.operationMs = 10;
  failAt("sync", "S000/imu.csv");
  flushTick.next = millis();
  loop();  // failure timestamp is later than the loop's original timestamp
  CHECK(session == -1 && disk.mounts == 1);
  clockMs = lastSdAttemptMs + SD_RETRY_MS - 1;
  loop();
  CHECK(session == -1);
  clockMs++;
  loop();
  CHECK(session == 1 && disk.mounts == 2);
}

static void bnoResetTimeouts() {
  for (bool readFailure : {false, true}) {
    for (uint32_t start : {uint32_t(100), UINT32_MAX - 500}) {
      reset();
      clockMs = start;
      bnoBus.readyAfterMs = 100000;
      bnoBus.resetReadFails = readFailure;
      CHECK(!bno.begin(OPERATION_MODE_NDOF, 1000));
      CHECK(uint32_t(millis() - start) <= 1050);
      CHECK(bnoBus.resetWrites == 1);
    }
  }
  reset();
  bnoBus.transactionMs = 50;  // bus time counts toward poll deadline
  bnoBus.readyAfterMs = 100000;
  CHECK(!bno.begin(OPERATION_MODE_NDOF, 1000));
  CHECK(uint32_t(millis() - bnoBus.resetAt) < 1070);
  reset();
  bnoBus.resetWriteFails = true;
  CHECK(!bno.begin(OPERATION_MODE_NDOF, 1000));
  CHECK(!bnoBus.resetWritten);
  reset();
  bnoBus.present = false;
  CHECK(!bno.begin(OPERATION_MODE_NDOF, 1000));
  CHECK(millis() < 1000 && bnoBus.resetWrites == 0);
  reset();
  CHECK(bno.begin(OPERATION_MODE_NDOF, 1000));
  CHECK(bnoBus.resetWrites == 1);
}

static void initCooldownAndOtherStreams() {
  reset();
  CHECK(startStorage(writeMetadata));
  imuReady = imuOk = false;
  bnoBus.readyAfterMs = 100000;
  sampleImu(millis());
  CHECK(!imuOk && bnoBus.resetWrites == 1);
  const uint32_t failedAt = lastImuAttemptMs;
  sampleImu(millis());
  CHECK(bnoBus.resetWrites == 1);
  CHECK(disk.files.at("S000/imu.csv")->bytes.find("INIT_WAIT") != std::string::npos);
  sampleEnv(millis());
  writeHealth(millis());
  CHECK(disk.files.at("S000/env.csv")->bytes.find("OK") != std::string::npos);
  const auto &health = disk.files.at("S000/health.csv")->bytes;
  const auto first = health.find('\n'), second = health.find('\n', first + 1);
  CHECK(std::count(health.begin(), health.begin() + first, ',') ==
        std::count(health.begin() + first + 1, health.begin() + second, ','));
  clockMs = failedAt + IMU_RETRY_MS - 1;
  sampleImu(millis());
  CHECK(bnoBus.resetWrites == 1);
  // Emulate a sensor that becomes healthy again after a physical power cycle.
  bnoBus.resetWritten = false;
  bnoBus.readyAfterMs = 700;
  clockMs++;
  sampleImu(millis());
  CHECK(imuOk && bnoBus.resetWrites == 2);
}

static void bootWithFailedImu() {
  reset();
  bnoBus.readyAfterMs = 100000;
  setup();
  CHECK(!imuOk && session == 0);
  CHECK(millis() < 2000);  // fake zero-latency buses; not a hardware timing claim
  reset();
  pins[PIN_SW_MODE] = LOW;
  setup();
  CHECK(stopRequested && session == -1 && disk.mounts == 0);
}

static std::vector<std::string> csvLastRow(const std::string &path) {
  const std::string &text = disk.files.at(path)->bytes;
  CHECK(!text.empty() && text.back() == '\n');
  const auto start = text.rfind('\n', text.size() - 2);
  std::string row = text.substr(start + 1, text.size() - start - 2);
  std::vector<std::string> fields;
  size_t pos = 0;
  while (true) {
    auto comma = row.find(',', pos);
    fields.push_back(row.substr(pos, comma == std::string::npos ? comma : comma - pos));
    if (comma == std::string::npos) break;
    pos = comma + 1;
  }
  return fields;
}
static void invalidRow(const std::string &file, size_t count, const char *status) {
  auto fields = csvLastRow("S000/" + file);
  CHECK(fields.size() == count && fields[3] == status);
  for (size_t n = 4; n < count; ++n) CHECK(fields[n].empty());
}
static void bnoFixture() {
  auto words = [](std::initializer_list<int16_t> values) {
    std::vector<uint8_t> result;
    for (int16_t value : values) {
      result.push_back(uint16_t(value) & 0xff);
      result.push_back(uint16_t(value) >> 8);
    }
    return result;
  };
  bnoBus.registers[0x20] = words({16384, -8192, 4096, -16384});
  bnoBus.registers[0x08] = words({100, -200, 300});
  bnoBus.registers[0x14] = words({16, -32, 48});
  bnoBus.registers[0x0e] = words({160, -320, 480});
  bnoBus.registers[0x35] = {0xe4};
}

static void bnoCheckedValues() {
  reset();
  bnoFixture();
  imu::Quaternion q;
  imu::Vector<3> a, g, m;
  uint8_t cs, cg, ca, cm;
  CHECK(bno.getQuatChecked(q));
  CHECK(q.w() == 1 && q.x() == -0.5 && q.y() == 0.25 && q.z() == -1);
  CHECK(bno.getVectorChecked(Adafruit_BNO055::VECTOR_ACCELEROMETER, a));
  CHECK(a.x() == 1 && a.y() == -2 && a.z() == 3);
  CHECK(bno.getVectorChecked(Adafruit_BNO055::VECTOR_GYROSCOPE, g));
  CHECK(g.x() == 1 && g.y() == -2 && g.z() == 3);
  CHECK(bno.getVectorChecked(Adafruit_BNO055::VECTOR_MAGNETOMETER, m));
  CHECK(m.x() == 10 && m.y() == -20 && m.z() == 30);
  CHECK(bno.getCalibrationChecked(&cs, &cg, &ca, &cm));
  CHECK(cs == 3 && cg == 2 && ca == 1 && cm == 0);
  CHECK(startStorage(writeMetadata));
  sampleImu(millis());
  auto row = csvLastRow("S000/imu.csv");
  CHECK(row.size() == 21 && row[3] == "OK");
  CHECK(std::abs(std::stod(row[11]) - PI / 180) < 0.00001);
  CHECK(imuOk && calSys == 3);
  // A short quaternion transfer must preserve the caller's previous object.
  bnoBus.registers[0x20].pop_back();
  CHECK(!bno.getQuatChecked(q));
  CHECK(q.w() == 1 && q.x() == -0.5);
  bnoBus.failReadReg = 0x08;
  CHECK(!bno.getVectorChecked(Adafruit_BNO055::VECTOR_ACCELEROMETER, a));
  CHECK(a.y() == -2);
  bnoBus.failReadReg = 0x35;
  CHECK(!bno.getCalibrationChecked(&cs, &cg, &ca, &cm));
  CHECK(cs == 3 && cg == 2 && ca == 1 && cm == 0);
}

static void bnoTransferFailures() {
  for (int reg : {0x20, 0x08, 0x14, 0x0e, 0x35}) {
    for (bool shortRead : {false, true}) {
      reset();
      bnoFixture();
      CHECK(startStorage(writeMetadata));
      sampleImu(millis()); // establish prior valid data
      if (shortRead) bnoBus.registers[reg].pop_back();
      else bnoBus.failReadReg = reg;
      sampleImu(millis());
      invalidRow("imu.csv", 21, "READ_FAIL");
      CHECK(!imuOk && imuReady && calSys == 0 && imuFailTotal == 1);
      CHECK(imuConsecutiveFails == 1 && imuResets == 0);
      updateLeds(millis());
      CHECK(pins[PIN_LED_FAULT] == HIGH && pins[PIN_LED_CAL] == LOW);
      sampleEnv(millis()); // unrelated stream continues
      CHECK(csvLastRow("S000/env.csv")[3] == "OK");
      bnoBus.failReadReg = -1;
      bnoFixture();
      sampleImu(millis());
      CHECK(csvLastRow("S000/imu.csv")[3] == "OK");
      CHECK(imuOk && imuConsecutiveFails == 0 && imuFailTotal == 1);
    }
  }
  reset();
  bnoFixture();
  CHECK(startStorage(writeMetadata));
  bnoBus.failReadReg = 0x20;
  for (int n = 0; n < IMU_FAILS_BEFORE_RESET; ++n) sampleImu(millis());
  CHECK(imuResets == 1 && imuFailTotal == IMU_FAILS_BEFORE_RESET);
  CHECK(imuReady && !imuOk); // reset/config success is not valid sample data
  invalidRow("imu.csv", 21, "READ_FAIL");
}

static void bnoConfigurationFailures() {
  for (int reg : {0x3d, 0x3e, 0x07, 0x3f}) {
    reset();
    bnoBus.failWriteReg = reg;
    CHECK(!initImu() && !imuReady);
  }
  reset();
  bnoBus.failReadReg = 0;
  CHECK(!initImu() && !imuReady);
  reset();
  CHECK(bno.begin());
  bnoBus.failWriteReg = 0x3f;
  CHECK(!bno.setExtCrystalUse(true));
}

struct MsFault { const char *op; int addr, cmd, call; };
static void msFault(const MsFault &fault) {
  msBus.failOperation = fault.op;
  msBus.failAddress = fault.addr;
  msBus.failCommand = fault.cmd;
  msBus.failCall = fault.call;
  msBus.matches = 0;
}
static void msValuesAndWrappers() {
  reset();
  sensors_event_t p{}, t{}, h{};
  CHECK(ms8607.getEvent(&p, &t, &h));
  CHECK(p.type == SENSOR_TYPE_PRESSURE && p.pressure > 0);
  CHECK(t.type == SENSOR_TYPE_AMBIENT_TEMPERATURE && std::isfinite(t.temperature));
  CHECK(h.type == SENSOR_TYPE_RELATIVE_HUMIDITY && h.relative_humidity == 56.5f);
  CHECK(startStorage(writeMetadata));
  sampleEnv(millis());
  CHECK(csvLastRow("S000/env.csv")[3] == "OK");
  msBus.badHumidityCrc = true;
  CHECK(!ms8607.getHumiditySensor()->getEvent(&h));
  CHECK(h.version == 0 && h.relative_humidity == 0);
  msFault({"write", 0x76, 0x58, 1});
  CHECK(!ms8607.getTemperatureSensor()->getEvent(&t));
  CHECK(t.version == 0);
  msFault({"write", 0x76, 0x48, 1});
  CHECK(!ms8607.getPressureSensor()->getEvent(&p));
  CHECK(p.version == 0);
}

static void msMeasurementFailures() {
  const MsFault faults[] = {
    {"write", 0x76, 0x58, 1},             // start temperature conversion
    {"write_then_read", 0x76, 0x00, 1},   // temperature ADC response
    {"write", 0x76, 0x48, 1},             // start pressure conversion
    {"write_then_read", 0x76, 0x00, 2},   // pressure ADC response
    {"write", 0x40, 0xf5, 1},             // start humidity conversion
    {"read", 0x40, -1, 1},                // humidity response/short read
  };
  for (const auto &fault : faults) {
    reset();
    CHECK(startStorage(writeMetadata));
    sampleEnv(millis());
    CHECK(csvLastRow("S000/env.csv")[3] == "OK");
    msFault(fault);
    sampleEnv(millis());
    invalidRow("env.csv", 8, "READ_FAIL");
    CHECK(!envOk && envReady && envFailTotal == 1);
    updateLeds(millis());
    CHECK(pins[PIN_LED_FAULT] == HIGH);
    sampleImu(millis());
    CHECK(csvLastRow("S000/imu.csv")[3] == "OK");
    msBus.failOperation.clear();
    sampleEnv(millis());
    CHECK(envOk && envFailTotal == 1 && csvLastRow("S000/env.csv")[3] == "OK");
    // Public driver must clear prior events instead of exposing cached values.
    sensors_event_t p{}, t{}, h{};
    CHECK(ms8607.getEvent(&p, &t, &h));
    msFault(fault);
    CHECK(!ms8607.getEvent(&p, &t, &h));
    CHECK(p.version == 0 && t.version == 0 && h.version == 0);
  }
  reset();
  CHECK(startStorage(writeMetadata));
  sampleEnv(millis());
  msBus.badHumidityCrc = true;
  sampleEnv(millis());
  invalidRow("env.csv", 8, "READ_FAIL");
  CHECK(!envOk && envFailTotal == 1);
  msBus.badHumidityCrc = false;
  sampleEnv(millis());
  CHECK(envOk && csvLastRow("S000/env.csv")[3] == "OK");
}

static void msInitializationFailures() {
  std::vector<MsFault> faults = {
    {"begin", 0x76, -1, 1}, {"begin", 0x40, -1, 1},
    {"write", 0x76, 0x1e, 1}, {"write", 0x40, 0xfe, 1},
    {"write_then_read", 0x40, 0xe7, 1}, {"write", 0x40, 0xe6, 1},
  };
  for (int reg = 0xa0; reg <= 0xac; reg += 2)
    faults.push_back({"write_then_read", 0x76, reg, 1});
  for (const auto &fault : faults) {
    reset();
    auto *originalWrapper = ms8607.getTemperatureSensor();
    msFault(fault);
    CHECK(!ms8607.begin(&Wire));
    sensors_event_t p{}, t{}, h{};
    CHECK(!ms8607.getEvent(&p, &t, &h));
    msBus.failOperation.clear();
    CHECK(ms8607.begin(&Wire));
    CHECK(ms8607.getTemperatureSensor() == originalWrapper);
    CHECK(ms8607.getEvent(&p, &t, &h));
  }
  reset();
  CHECK(startStorage(writeMetadata));
  envReady = envOk = false;
  msBus.badPromCrc = true;
  sampleEnv(millis());
  invalidRow("env.csv", 8, "INIT_FAIL");
  CHECK(!envReady && !envOk && envFailTotal == 1);
  msBus.badPromCrc = false;
  sampleEnv(millis());
  CHECK(envReady && envOk && csvLastRow("S000/env.csv")[3] == "OK");
  // Corrupt coefficient data while leaving the stored fixture CRC unchanged.
  msBus.prom[2] ^= 1;
  CHECK(!ms8607.begin(&Wire));
  msBus.prom[2] ^= 1;
  CHECK(ms8607.reset());
  sensors_event_t p{}, t{}, h{};
  CHECK(!ms8607.getEvent(&p, &t, &h));
  CHECK(ms8607.init(0));
  CHECK(ms8607.getEvent(&p, &t, &h));
}

int main() {
  try {
    for (auto test : {successfulSessions, incompleteSessions, mountDirectoryAndExhaustion,
                      exclusiveFiles, writeAndSyncRecovery, cleanStopAndFailedClose,
                      retryTimingAndRollover, bnoResetTimeouts,
                      initCooldownAndOtherStreams, bootWithFailedImu,
                      bnoCheckedValues, bnoTransferFailures, bnoConfigurationFailures,
                      msValuesAndWrappers, msMeasurementFailures, msInitializationFailures}) {
      test();
    }
    std::cout << "PASS: 16 groups; actual sketch/storage/metadata/BNO/MS drivers with fake hardware\n";
  } catch (const std::exception &error) {
    std::cerr << "FAIL: " << error.what() << "\n";
    return 1;
  }
}
