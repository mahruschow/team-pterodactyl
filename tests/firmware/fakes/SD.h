#pragma once
#include "Arduino.h"
#include <map>
#include <set>
#include <memory>
#include <stdexcept>
constexpr int BUILTIN_SDCARD = 254, O_WRONLY = 1, O_CREAT = 2, O_EXCL = 4;
struct FakeFileData { std::string bytes; bool open = false, writeError = false; };
struct FakeDisk {
  std::map<std::string, std::shared_ptr<FakeFileData>> files;
  std::set<std::string> dirs;
  std::string failOperation, failPath;
  int failOnCall = 1, matchedCalls = 0, mounts = 0;
  uint32_t operationMs = 0;
  bool missing = false, lieAboutExists = false;
  bool fail(const char *op, const std::string &path = "") {
    delay(operationMs);
    return failOperation == op && (failPath.empty() || failPath == path) &&
           ++matchedCalls == failOnCall;
  }
  bool allClosed() const {
    for (const auto &entry : files) if (entry.second->open) return false;
    return true;
  }
};
inline FakeDisk disk;
class FsFile {
  std::shared_ptr<FakeFileData> data;
  std::string path;
public:
  FsFile() = default;
  FsFile(std::shared_ptr<FakeFileData> d, std::string p) : data(d), path(p) {}
  explicit operator bool() const { return data && data->open; }
  size_t write(const void *text, size_t n) {
    if (!*this) return 0;
    if (disk.fail("write", path)) {
      const size_t partial = n ? n - 1 : 0;
      data->bytes.append(static_cast<const char *>(text), partial);
      data->writeError = true;
      return partial;
    }
    data->bytes.append(static_cast<const char *>(text), n);
    return n;
  }
  size_t write(uint8_t b) { return write(&b, 1); }
  size_t printf(const char *fmt, ...) {
    char text[2048];
    va_list args;
    va_start(args, fmt);
    int n = vsnprintf(text, sizeof(text), fmt, args);
    va_end(args);
    return write(text, n);
  }
  bool getWriteError() const { return !*this || data->writeError; }
  bool sync() { return *this && !disk.fail("sync", path); }
  bool close() {
    const bool ok = sync() && !disk.fail("close", path);
    if (data) data->open = false;  // SdFat closes even if its sync fails
    return ok;
  }
};
struct FakeSdFs {
  FsFile open(const char *path, int flags) {
    if (disk.fail("open", path)) return {};
    if (disk.files.count(path) && (flags & O_EXCL)) return {};
    auto d = std::make_shared<FakeFileData>();
    d->open = true;
    disk.files[path] = d;
    return FsFile(d, path);
  }
};
struct FakeSD {
  FakeSdFs sdfs;
  bool begin(int) {
    if (!disk.allClosed()) throw std::runtime_error("remount with live handles");
    disk.mounts++;
    return !disk.missing;
  }
  bool exists(const char *p) { return !disk.lieAboutExists && disk.dirs.count(p); }
  bool mkdir(const char *p) {
    if (disk.fail("mkdir", p)) return false;
    disk.dirs.insert(p);
    return true;
  }
};
inline FakeSD SD;
