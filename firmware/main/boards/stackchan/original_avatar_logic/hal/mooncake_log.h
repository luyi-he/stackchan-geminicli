/*
 * Mock mooncake_log.h for StackChan Integration
 */
#pragma once
#include <esp_log.h>
#include <string_view>

namespace mclog {
    // Basic mock that accepts variadic arguments
    template<typename... Args>
    inline void tagInfo(const char* tag, const char* format, Args... args) {
        // Implementation can be empty or bridge to ESP_LOGI
    }

    template<typename... Args>
    inline void tagWarn(const char* tag, const char* format, Args... args) {
    }

    template<typename... Args>
    inline void tagError(const char* tag, const char* format, Args... args) {
    }

    // Support underscored versions if needed by some files
    template<typename... Args>
    inline void tag_info(const char* tag, const char* format, Args... args) {}
    
    template<typename... Args>
    inline void tag_warn(const char* tag, const char* format, Args... args) {}
    
    template<typename... Args>
    inline void tag_error(const char* tag, const char* format, Args... args) {}
}
