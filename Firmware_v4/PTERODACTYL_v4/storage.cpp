#include "storage.h"
#include <stdio.h>
#include <string.h>

LogStream streams[S_COUNT] = {
  {"imu.csv", "session,seq,t_ms,status,qw,qx,qy,qz,ax_mps2,ay_mps2,az_mps2,gx_rps,gy_rps,gz_rps,mx_uT,my_uT,mz_uT,cal_sys,cal_gyro,cal_accel,cal_mag", FsFile(), 0, 0},
  {"env.csv", "session,seq,t_ms,status,pressure_pa,temperature_c,humidity_rh,pressure_alt_isa_m", FsFile(), 0, 0},
  {"gps.csv", "session,seq,t_ms,status,fix,fix_quality,satellites,utc_date,utc_time,lat_deg,lon_deg,alt_msl_m,hdop,speed_mps,course_deg", FsFile(), 0, 0},
  {"health.csv", "session,seq,t_ms,vbat_v,imu_ok,env_ok,gps_age_ms,imu_fail_total,env_fail_total,imu_resets,gps_parse_fails,overruns,write_fail_total,max_loop_us,mode_stop,pbf_present,storage_fault_total", FsFile(), 0, 0},
  {"events.csv", "session,seq,t_ms,event,detail", FsFile(), 0, 0},
};
int session = -1;
uint32_t storageFaults = 0;
uint32_t lastSdAttemptMs = 0;

// Invalidate before closing: even a failed close must stop the logging heartbeat.
bool closeSession() {
  const bool wasLogging = session >= 0;
  session = -1;
  bool ok = true;
  for (auto &s : streams) {
    if (s.handle) {
      const bool writeError = s.handle.getWriteError();
      const bool closed = s.handle.close();  // always close, including on write error
      if (writeError || !closed) {
        s.writeFails++;
        ok = false;
      }
    } else if (wasLogging) {
      // A required handle disappearing is not a successful clean stop.
      s.writeFails++;
      ok = false;
    }
    // Drop the old file object before a later SD.begin() remount.
    s.handle = FsFile();
  }
  if (!ok) {
    storageFaults++;
    lastSdAttemptMs = millis();
  }
  return ok;
}

static void storageFault() {
  storageFaults++;
  closeSession();  // best effort; preserve all partial files for diagnosis
  lastSdAttemptMs = millis();
}

bool startStorage(MetadataWriter metadata) {
  if (session >= 0) return true;
  closeSession();
  lastSdAttemptMs = millis();
  if (!SD.begin(BUILTIN_SDCARD)) {
    storageFault();
    return false;
  }
  char dir[8];
  for (int n = 0; n < 1000; n++) {
    snprintf(dir, sizeof(dir), "S%03d", n);
    if (SD.exists(dir)) continue;
    if (!SD.mkdir(dir)) {
      storageFault();
      return false;
    }
    for (auto &s : streams) {
      char path[24];
      snprintf(path, sizeof(path), "%s/%s", dir, s.file);
      // Exclusive creation is a second guard if an exists() check misbehaves.
      s.handle = SD.sdfs.open(path, O_WRONLY | O_CREAT | O_EXCL);
      const size_t length = strlen(s.header);
      if (!s.handle || s.handle.write(s.header, length) != length ||
          s.handle.write('\n') != 1 || s.handle.getWriteError() ||
          !s.handle.sync()) {
        s.writeFails++;
        storageFault();
        return false;
      }
    }
    if (!metadata(dir, n)) {
      streams[S_EVENTS].writeFails++;
      storageFault();
      return false;
    }
    // Commit only after all five CSV headers and metadata are durable per sync().
    for (auto &s : streams) s.seq = 0;
    session = n;
    return true;
  }
  storageFault();  // all 1000 folders occupied: never reuse or delete one
  return false;
}

void writeLine(StreamId id, const char *text) {
  if (session < 0) return;  // no buffering/replay during an outage
  LogStream &s = streams[id];
  const size_t length = strlen(text);
  if (!s.handle || s.handle.write(text, length) != length ||
      s.handle.write('\n') != 1 || s.handle.getWriteError()) {
    s.writeFails++;
    storageFault();
  }
}

bool flushAll() {
  if (session < 0) return false;
  for (auto &s : streams) {
    if (!s.handle || s.handle.getWriteError() || !s.handle.sync()) {
      s.writeFails++;
      storageFault();
      return false;
    }
  }
  return true;
}

uint32_t writeFailTotal() {
  uint32_t total = 0;
  for (auto &s : streams) total += s.writeFails;
  return total;
}
