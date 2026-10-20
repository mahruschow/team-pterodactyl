#include "config.h"
#include "storage.h"

bool writeMetadata(const char *dir, int number) {
  char path[24];
  snprintf(path, sizeof(path), "%s/meta.txt", dir);
  FsFile m = SD.sdfs.open(path, O_WRONLY | O_CREAT | O_EXCL);
  if (!m) return false;
  m.printf("firmware=%s\nbuilt=%s %s\nsession=%d\n", FW_VERSION, __DATE__, __TIME__, number);
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
  m.printf("t_ms=uint32 Teensy millis() since boot; wraps after about 49.7 days\n");
  m.printf("storage_recovery=new folder; no replay of records during outage\n");
  m.printf("bno_reset_timeout_ms=%lu\nimu_retry_ms=%lu\n", (unsigned long)BNO_RESET_TIMEOUT_MS, (unsigned long)IMU_RETRY_MS);
  m.printf("vbat_divider=%.4f\nadc_bits=%u\n", VBAT_DIVIDER, ADC_BITS);
  const bool synced = !m.getWriteError() && m.sync();
  const bool closed = m.close();  // always release, even when sync failed
  return synced && closed;
}
