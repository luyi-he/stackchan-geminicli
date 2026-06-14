/*
 * Bridge HAL for StackChan Integration
 */
#pragma once
#include <memory>
#include <cstdint>
#include <string>
#include <lvgl.h>
#include <functional>
#include <smooth_ui_toolkit.hpp>
#include <smooth_lvgl.hpp>
#include <vector>

namespace app_center {
    struct AppInfo_t {
        std::string name;
    };
}

class Hal {
public:
    void delay(std::uint32_t ms);
    std::uint32_t millis();
    void lvglLock() {}
    void lvglUnlock() {}
};

Hal& GetHAL();

class LvglLockGuard {
public:
    LvglLockGuard() {}
    ~LvglLockGuard() {}
};
