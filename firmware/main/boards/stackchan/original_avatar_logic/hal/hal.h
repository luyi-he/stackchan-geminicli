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

enum class HeadPetGesture { None, Press, Release, SwipeForward, SwipeBackward };
enum class ImuMotionEvent { None = 0, Shake, PickUp };

class Hal {
public:
    void delay(std::uint32_t ms);
    std::uint32_t millis();
    void lvglLock() {}
    void lvglUnlock() {}

    // Missing RGB methods
    void setRgbColor(uint8_t index, uint8_t r, uint8_t g, uint8_t b) {}
    void refreshRgb() {}

    // Missing Signals
    uitk::Signal<HeadPetGesture> onHeadPetGesture;
    uitk::Signal<ImuMotionEvent> onImuMotionEvent;
};

Hal& GetHAL();

class LvglLockGuard {
public:
    LvglLockGuard() {}
    ~LvglLockGuard() {}
};
