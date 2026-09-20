// test_package.cpp - crc32c 1.1.2.1 smoke test
// Calls crc32c::Crc32c and crc32c::Extend APIs to verify the library
// is correctly built and linked.

#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>

#include "crc32c/crc32c.h"

int main() {
    // Test 1: Compute CRC32C of a known buffer
    const uint8_t buffer[] = {0x12, 0x34, 0x56, 0x78};
    uint32_t result = crc32c::Crc32c(buffer, sizeof(buffer));
    constexpr uint32_t expected_buffer_crc = 0x4300918A;
    if (result != expected_buffer_crc) {
        std::fprintf(stderr, "ERROR: known-vector mismatch: 0x%08X != 0x%08X\n",
                     result, expected_buffer_crc);
        return 1;
    }
    std::printf("CRC32C of {0x12,0x34,0x56,0x78} = 0x%08X\n", result);

    // Fixed CRC32C vector for four zero bytes.
    const uint8_t zeros[] = {0, 0, 0, 0};
    uint32_t zeros_crc = crc32c::Crc32c(zeros, sizeof(zeros));
    constexpr uint32_t expected_zeros_crc = 0x48674BC7;
    if (zeros_crc != expected_zeros_crc) {
        std::fprintf(stderr, "ERROR: zero-vector mismatch: 0x%08X != 0x%08X\n",
                     zeros_crc, expected_zeros_crc);
        return 1;
    }
    std::printf("CRC32C of 4 zero bytes = 0x%08X\n", zeros_crc);

    // Test 2: Extend a CRC with additional data
    uint32_t partial = crc32c::Crc32c(buffer, 2);
    uint32_t extended = crc32c::Extend(partial, buffer + 2, 2);
    if (extended != result) {
        std::fprintf(stderr, "ERROR: Extend mismatch: %u != %u\n",
                     extended, result);
        return 1;
    }
    std::printf("Extend consistency: OK\n");

    // Test 3: Compute CRC32C of a std::string
    std::string str = "Hello, crc32c!";
    uint32_t str_crc = crc32c::Crc32c(str);
    std::printf("CRC32C of \"Hello, crc32c!\" = %u\n", str_crc);

    // Test 4: Verify C API (crc32c_value) matches C++ API
    uint32_t c_api_result = crc32c_value(buffer, sizeof(buffer));
    if (c_api_result != result) {
        std::fprintf(stderr, "ERROR: C API mismatch: %u != %u\n",
                     c_api_result, result);
        return 1;
    }
    std::printf("C API consistency: OK\n");

    std::printf("All crc32c tests passed!\n");
    return 0;
}
