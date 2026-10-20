# Firmware validation — October 20, 2026

Base commit: `e1663f7`, branch `saadat-dev`. Tested source is identified by
`source-manifest.json`; this directory is committed together with that source.
Hashes are of the captured working files; Git line-ending conversion can change
byte hashes on another checkout.

| Check | Result |
| --- | --- |
| Host C++ fault injection | PASS — 10 parameterized groups against actual sketch, storage, metadata and patched BNO source |
| Teensy 4.1 build, `--warnings all` | PASS — zero warnings, platform 1.62.0 and installed pinned dependencies |
| PCB/schematic edits | None |
| Hardware operation / timing / power loss | Not tested |

`host-tests.log` records the passing run. The host compiler was Zig 0.13.0
(`zig c++`, C++17, `-Wall -Wextra -Werror`). On its first invocation, building
Zig's own Windows libunwind runtime emitted DLL-attribute warnings; the firmware
and test translation units compiled under `-Werror`. The recorded final run used
that cached runtime. Zig was installed only in the chat's scratch directory and
is not a firmware dependency.

`build.log` contains the final Arduino CLI output and dependency versions.
The sketch uses the local BNO055 patch, so the installed BNO library is absent
from the used-library list. No isolated `--profile` dependency download/build
was performed, and nothing was uploaded to a board.

Reproduce from the repository:

```text
python tools/test_firmware_reliability.py --cxx clang++
arduino-cli compile --warnings all Firmware_v4/PTERODACTYL_v4
```

The host runner accepts `g++` or an explicit Zig executable too. Its execution
timeout catches regressions that hang the test process. Fakes exercise software
decisions and preserve partial file contents; they do not emulate FAT/exFAT,
SD electrical behavior, actual I2C timing, GPS parsing or sensor accuracy.
See [checkpoint details](../../../FIRMWARE_RELIABILITY.md) for remaining work.
