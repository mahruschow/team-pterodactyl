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
  Wire.present = true;
  clockMs = 100;
  storageFaults = 0;
  lastSdAttemptMs = 0;
  for (auto &s : streams) { s.seq = 0; s.writeFails = 0; }
  stopRequested = false;
  imuOk = envOk = true;
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
  imuOk = false;
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

int main() {
  try {
    for (auto test : {successfulSessions, incompleteSessions, mountDirectoryAndExhaustion,
                      exclusiveFiles, writeAndSyncRecovery, cleanStopAndFailedClose,
                      retryTimingAndRollover, bnoResetTimeouts,
                      initCooldownAndOtherStreams, bootWithFailedImu}) {
      test();
    }
    std::cout << "PASS: 10 groups; actual sketch/storage/metadata/BNO driver with fake hardware\n";
  } catch (const std::exception &error) {
    std::cerr << "FAIL: " << error.what() << "\n";
    return 1;
  }
}
