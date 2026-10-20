"""Run host fault injection against production firmware, not a Python model.

Requires a C++17 compiler: --cxx clang++, --cxx g++, or --cxx /path/to/zig.
Build artifacts are placed in a temporary directory; no hardware is accessed.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
FW = ROOT / "Firmware_v4/PTERODACTYL_v4"
TESTS = ROOT / "tests/firmware"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cxx", default="g++")
    args = parser.parse_args()
    compiler = [args.cxx]
    if Path(args.cxx).stem == "zig":
        compiler.append("c++")
    with tempfile.TemporaryDirectory(prefix="pterodactyl-fw-") as temp:
        exe = Path(temp) / "reliability_test.exe"
        command = compiler + [
            "-std=c++17", "-Wall", "-Wextra", "-Werror",
            "-I", str(TESTS / "fakes"),
            str(TESTS / "reliability_test.cpp"),
            str(FW / "storage.cpp"), str(FW / "metadata.cpp"),
            str(FW / "src/bno055/Adafruit_BNO055.cpp"),
            str(FW / "src/ms8607/Adafruit_MS8607.cpp"),
            "-o", str(exe),
        ]
        subprocess.run(command, check=True, timeout=300)
        # A regression to the upstream infinite loop must fail the test run.
        subprocess.run([str(exe)], check=True, timeout=15)


if __name__ == "__main__":
    main()
