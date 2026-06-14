/*
 * Mock mooncake_log.h
 */
#pragma once
#include <esp_log.h>
#include <string_view>

namespace mclog {
    inline void tagInfo(const std::string_view& tag, const char* format, ...) {
        // Just use ESP_LOGI
    }
}
