# PTERODACTYL v4 firmware

Draft logger for the v4 carrier (Teensy 4.1, BNO055 #2472, MS8607 #4716, PA1616D GPS #5440, onboard microSD; no telemetry). It compiles cleanly for Teensy 4.1 but has **not yet run on hardware**.

- `PTERODACTYL_v4/PTERODACTYL_v4.ino`: the logger.
- `PTERODACTYL_v4/config.h`: pins (matching `Native_KiCad_v4`), rates and thresholds.
- `PTERODACTYL_v4/sketch.yaml`: board and pinned library versions.

See [docs/FIRMWARE_V4.md](../docs/FIRMWARE_V4.md) for behaviour, log formats, LEDs, build steps and what is still untested. The original v19/v19.1 firmware remains in `Firmware_reference/` for comparison.
