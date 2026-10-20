// Session lifecycle shared by the Teensy logger and host fault-injection tests.
#pragma once
#include <SD.h>

enum StreamId { S_IMU, S_ENV, S_GPS, S_HEALTH, S_EVENTS, S_COUNT };
struct LogStream {
  const char *file;
  const char *header;
  FsFile handle;  // Teensy SdFat exposes sync()/close() results; File::flush does not.
  uint32_t seq;
  uint32_t writeFails;
};

extern LogStream streams[S_COUNT];
extern int session;  // -1 until every required file has been written and synced
extern uint32_t storageFaults;
extern uint32_t lastSdAttemptMs;

using MetadataWriter = bool (*)(const char *dir, int number);
bool writeMetadata(const char *dir, int number);
bool startStorage(MetadataWriter metadata);
bool closeSession();
bool flushAll();
void writeLine(StreamId id, const char *text);
uint32_t writeFailTotal();
