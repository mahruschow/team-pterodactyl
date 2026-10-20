// PTERODACTYL v4 firmware configuration.
// Pin numbers follow Native_KiCad_v4/PTERODACTYL_v4.kicad_sch (net names in comments).
// Rates and thresholds are the Step 2 proposals in docs/V1_REQUIREMENTS.md, not approved mission values.
#pragma once
#include <Arduino.h>

#define FW_VERSION "4.0.1-draft"

// Status LEDs (STATUS1-4 through 680 ohm resistors)
constexpr uint8_t PIN_LED_FAULT = 2;   // STATUS1, red: any fault
constexpr uint8_t PIN_LED_GPS   = 3;   // STATUS2, yellow: GPS fix and fresh
constexpr uint8_t PIN_LED_LOG   = 4;   // STATUS3, green: 1 Hz heartbeat while logging
constexpr uint8_t PIN_LED_CAL   = 5;   // STATUS4, orange: BNO055 system calibration = 3

constexpr uint8_t PIN_IMU_RST   = 9;   // IMU_RST to BNO055 RST (driven open-drain style)
constexpr uint8_t PIN_VBAT      = 26;  // VBAT_SENSE (A12) via 100k/22k divider
constexpr uint8_t PIN_SW_MODE   = 30;  // SW_MODE: switch to GND = stop logging (clean stop)
constexpr uint8_t PIN_BUTTON    = 31;  // BTN_USER: press = event marker
constexpr uint8_t PIN_PBF       = 32;  // PBF_SENSE: jumper to GND; removal = launch marker

#define GPS_SERIAL Serial2              // GPS_TXD -> pin 7 (RX2), GPS_RXD <- pin 8 (TX2)
constexpr uint32_t GPS_BAUD = 9600;     // PA1616D default

constexpr uint32_t I2C_CLOCK_HZ = 100000;  // Bring-up rate; 400 kHz needs measured rise time (T6)
constexpr uint8_t BNO055_ADDR = 0x28;
constexpr uint8_t MS8607_PT_ADDR = 0x76;
constexpr uint8_t MS8607_RH_ADDR = 0x40;

// Schedules (ms)
constexpr uint32_t IMU_PERIOD_MS    = 100;   // 10 Hz
constexpr uint32_t ENV_PERIOD_MS    = 1000;  // 1 Hz
constexpr uint32_t HEALTH_PERIOD_MS = 1000;  // 1 Hz
constexpr uint32_t FLUSH_PERIOD_MS  = 1000;  // LOG-06: flush at most every 1 s
constexpr uint32_t SD_RETRY_MS      = 5000;
constexpr uint32_t GPS_STALE_MS     = 3000;  // GGA older than this is stale
constexpr uint32_t DEBOUNCE_MS      = 50;

// Fault handling
constexpr uint32_t BNO_RESET_TIMEOUT_MS = 1000; // post-software-reset CHIP_ID poll budget
constexpr uint32_t IMU_RETRY_MS = 5000;         // after a completed init/reset attempt
constexpr uint8_t IMU_FAILS_BEFORE_RESET = 5;  // consecutive failed reads before hardware reset

// Battery sense
constexpr float VBAT_DIVIDER = (100.0f + 22.0f) / 22.0f;
constexpr float ADC_REF_V = 3.3f;
constexpr uint8_t ADC_BITS = 12;

// Pressure altitude: International Standard Atmosphere, sea-level reference
constexpr float ISA_P0_PA = 101325.0f;
